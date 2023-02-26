import numpy as np
from scipy import signal
import math
from extent import Extent
from pyg_pe import PygPE
import pyg_exceptions as pyx
import utils as ut

# Work in progress.  See also:
# https://github.com/hosackm/BiquadFilter/blob/master/Biquad.h
# https://github.com/thestk/stk/blob/master/include/Biquad.h
# https://github.com/thestk/stk/blob/master/src/Biquad.cpp
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt.html
# https://gist.github.com/RyanMarcus/d3386baa6b4cb1ac47f4
# view-source:https://www.earlevel.com/scripts/widgets/20210825/biquads3.js
#
# Game Plan:
# * mono, fixed params, discrete inner loop
# * verify results with audio
# * stereo, verify
# * stereo, variable F0, verify
# * stereo, variable bandwidth, verify

# A0 = 0  -- alwasy assumed to be 1.0
A1 = 0
A2 = 1
B0 = 2
B1 = 3
B2 = 4

class BiquadPE(PygPE):

    def __init__(self, src, frame_rate=None):
        self._src = src

        self._frame_rate = frame_rate
        if self._frame_rate is None:
            self._frame_rate = src.frame_rate()

        if self.frame_rate() is None:
            raise pyx.FrameRateMismatch("frame_rate must be specified")

        if self.channel_count() != 1:
            raise pyx.ChannelCountMismatch("only mono sources are supported")

        self._coeffs = None

        self._x1 = 0
        self._x2 = 0
        self._y1 = 0
        self._y2 = 0

    def extent(self):
        return self._src.extent()

    def frame_rate(self):
        return self._frame_rate

    def channel_count(self):
        return self._src.channel_count()

    def coeffs(self):
        # lazy instantiation of coefficient array
        if self._coeffs is None:
            self._coeffs = np.ndarray(5, dtype=np.float32)
        return self._coeffs

    def render(self, requested):
        """
        Implement a biquad filter with response:
          H(z) = (b0 + b1*z^-1 + b2*z^-2) / (a1*z^-1 + a2*z^2)
        using "direct form 1":
          y[n] = (b0*x[n] + b1*x[n-1] + b2*x[n-2]) - (a1*y[n-1] + a2*y[n-2])
        Using appropriate choices of [a1, a2, b0, b1, b2], you can implment a
        wide variety of second-order filters.
        """
        n_frames = requested.duration()
        X = self._src.render(requested)
        Y = np.zeros((1, n_frames))
        # unpack for inner loop
        a1 = self._coeffs[A1]
        a2 = self._coeffs[A2]
        b0 = self._coeffs[B0]
        b1 = self._coeffs[B1]
        b2 = self._coeffs[B2]
        x2 = self._x2
        x1 = self._x1
        y2 = self._y2
        y1 = self._y1
        for i in np.arange(n_frames):
            x0 = X[0, i]
            y0 = (b0*x0 + b1*x1 + b2*x2) - (a1*y1 + a2*y2)
            Y[0, i] = y0
            x2 = x1
            x1 = x0
            y2 = y1
            y1 = y0
        # repack for next frame...
        self._x2 = x2
        self._x1 = x1
        self._y2 = y2
        self._y1 = y1

        return Y

    def default_coeffs(self, f0, q):
        """
        Some of the common filters use identical parameters for the denominator
        (a1, a2), and shared values K and norm in the denominator.
        """
        coeffs = self.coeffs()
        K = np.tan(np.pi * f0 / self.frame_rate())
        K2 = K * K
        norm = 1 / (1 + K/q + K2)

        coeffs[A1] = 2 * (K2 - 1) * norm
        coeffs[A2] = (1 - K/q + K2) * norm

        return coeffs, norm, K

class BQLowPassPE(BiquadPE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src_pe, frame_rate)

        coeffs, norm, K = self.default_coeffs(f0, q)
        coeffs[B0] = K * K * norm
        coeffs[B1] = 2 * coeffs[B0]
        coeffs[B2] = coeffs[B0]

class BQHighPassPE(BiquadPE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src_pe, frame_rate)
        coeffs, norm, K = self.default_coeffs(f0, q)
        coeffs[B0] = norm
        coeffs[B1] = -2 * coeffs[B0]
        coeffs[B2] = coeffs[B0]

class BQBandPassPE(BiquadPE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        """
        Has 0db gain at f0
        """
        super().__init__(src_pe, frame_rate)
        coeffs, norm, K = self.default_coeffs(f0, q)
        coeffs[B0] = K * (norm / q)
        coeffs[B1] = 0.0
        coeffs[B2] = -coeffs[B0]

class BQBandRejectPE(BiquadPE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        """
        Has 0db gain everywhere except in the vicinity of f0
        """
        super().__init__(src_pe, frame_rate)
        coeffs, norm, K = self.default_coeffs(f0, q)
        coeffs[B0] = (K * K + 1) * norm
        coeffs[B1] = 2 * (K * K -1) * norm
        coeffs[B2] = coeffs[B0]

class BQAllPassPE(BiquadPE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src_pe, frame_rate)
        """
        Has 0db gain everywhere, for real!
        """
        coeffs, denom, K = self.default_coeffs(f0, q)
        coeffs[B0] = coeffs[A2]
        coeffs[B1] = coeffs[A1]
        coeffs[B2] = 1

class BQPeakPE(BiquadPE):
    def __init__(self, src_pe, f0=440, q=20, gain_db=0, frame_rate=None):
        """
        Serves as both a peak filter when gain_db > 0 and a notch filter when
        gain_db < 0.  Has 0db gain everywhere except around f0.
        """
        super().__init__(src_pe, frame_rate)
        coeffs = self.coeffs()
        K = np.tan(np.pi * f0 / self.frame_rate())
        K2 = K*K
        V = math.pow(10, abs(gain_db) / 20);
        if gain_db >= 0:
            # peaking
            norm = 1 / (1 + K/q + K2)
            coeffs[A1] = 2 * (K2 - 1) * norm
            coeffs[A2] = (1 - K/q + K2) * norm
            coeffs[B0] = (1 + (V*K)/q + K2) * norm
            coeffs[B1] = coeffs[A1]
            coeffs[B2] = (1 - (V*K)/q + K2) * norm
        else:
            # notching
            norm = 1 / (1 + (V*K)/q + K2)
            coeffs[A1] = 2 * (K2 - 1) * norm
            coeffs[A2] = (1 - (V*K)/q + K2) * norm
            coeffs[B0] = (1 + K/q + K2) * norm
            coeffs[B1] = coeffs[A1]
            coeffs[B2] = (1 - K/q + K2) * norm

class BQLowShelfPE(BiquadPE):
    def __init__(self, src_pe, f0=440, gain_db=0, frame_rate=None):
        """
        Has gain_db below f0, has 0db gain above f0.
        """
        super().__init__(src_pe, frame_rate)
        coeffs = self.coeffs()
        K = np.tan(np.pi * f0 / self.frame_rate())
        K2 = K*K
        V = math.pow(10, abs(gain_db) / 20);
        SQRT2 = math.sqrt(2)

        if gain_db >= 0:
            norm = 1 / (1 + SQRT2 * K + K2);
            coeffs[A1] = 2 * (K2 - 1) * norm;
            coeffs[A2] = (1 - SQRT2 * K + K2) * norm;
            coeffs[B0] = (1 + math.sqrt(2*V) * K + V * K2) * norm;
            coeffs[B1] = 2 * (V * K2 - 1) * norm;
            coeffs[B2] = (1 - math.sqrt(2*V) * K + V * K2) * norm;
        else:
            norm = 1 / (1 + math.sqrt(2*V) * K + V * K2);
            coeffs[B0] = (1 + SQRT2 * K + K2) * norm;
            coeffs[B1] = 2 * (K2 - 1) * norm;
            coeffs[B2] = (1 - SQRT2 * K + K2) * norm;
            coeffs[A1] = 2 * (V * K2 - 1) * norm;
            coeffs[A2] = (1 - math.sqrt(2*V) * K + V * K2) * norm;

class BQHighShelfPE(BiquadPE):
    def __init__(self, src_pe, f0=440, gain_db=0, frame_rate=None):
        super().__init__(src_pe, frame_rate)
        coeffs = self.coeffs()
        K = np.tan(np.pi * f0 / self.frame_rate())
        K2 = K*K
        V = math.pow(10, abs(gain_db) / 20);
        SQRT2 = math.sqrt(2)
        if gain_db >= 0:
            norm = 1 / (1 + SQRT2 * K + K2);
            coeffs[A1] = 2 * (K2 - 1) * norm;
            coeffs[A2] = (1 - SQRT2 * K + K2) * norm;
            coeffs[B0] = (V + math.sqrt(2*V) * K + K2) * norm;
            coeffs[B1] = 2 * (K2 - V) * norm;
            coeffs[B2] = (V - math.sqrt(2*V) * K + K2) * norm;
        else:
            norm = 1 / (V + math.sqrt(2*V) * K + K2);
            coeffs[A1] = 2 * (K2 - V) * norm;
            coeffs[A2] = (V - math.sqrt(2*V) * K + K2) * norm;
            coeffs[B0] = (1 + SQRT2 * K + K2) * norm;
            coeffs[B1] = 2 * (K2 - 1) * norm;
            coeffs[B2] = (1 - SQRT2 * K + K2) * norm;
