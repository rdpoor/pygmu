import numpy as np
from scipy.signal import sosfilt
import math
from extent import Extent
from pyg_pe import PygPE
import pyg_exceptions as pyx
import utils as ut

"""
Biquad filter based on scipy.signal.sosfilt
"""

class Biquad2PE(PygPE):
    """
    Implement a biquad filter with response:
        H(z) = (b0 + b1*z^-1 + b2*z^-2) / (a1*z^-1 + a2*z^2)
    using "direct form 1":
        y[n] = (b0*x[n] + b1*x[n-1] + b2*x[n-2]) - (a1*y[n-1] + a2*y[n-2])
    Using appropriate choices of [a1, a2, b0, b1, b2], you can implement a
    wide variety of second-order filters.
    """

    def __init__(self, src, frame_rate=None):
        self._src = src

        self._frame_rate = frame_rate
        if self._frame_rate is None:
            self._frame_rate = src.frame_rate()

        if self.frame_rate() is None:
            raise pyx.FrameRateMismatch("frame_rate must be specified")

        self._coeffs = np.zeros(5, dtype=np.float32)
        self._state = np.zeros((self.channel_count(), 5), dtype=np.float32)

    def extent(self):
        return self._src.extent()

    def frame_rate(self):
        return self._frame_rate

    def channel_count(self):
        return self._src.channel_count()

    def set_coefficients(self, a1, a2, b0, b1, b2):
        # Arranging the coefficients like this lets us use np.dot() for
        # efficiency in the inner loop -- see render()
        self._coeffs[0] = b0
        self._coeffs[1] = b1
        self._coeffs[2] = b2
        self._coeffs[3] = -a1
        self._coeffs[4] = -a2

    def get_coefficients(self):
        # primarily for unit tests, unpack the coefficients to return the
        # canonical form: a0, a1, b0, b1, b2
        return [-self._coeffs[3], -self._coeffs[4], self._coeffs[0], self._coeffs[1], self._coeffs[2]]

    def render(self, requested):
        n_frames = requested.duration()
        X = self._src.render(requested)
        Y = np.zeros_like(X)

        for c in range(self.channel_count()):
            for i in range(n_frames):
                x0 = X[c, i]
                self._state[c, 4] = x0
                self._state[c] = np.roll(self._state[c], 1)
                y0 = np.dot(self._state[c], self._coeffs)
                Y[c, i] = y0
                self._state[c, 2] = y0

        return Y

    def default_coeffs(self, f0, q):
        """
        Most of the common filters use identical parameters for the denominator
        (a1, a2), and shared values K and norm in the numerator.
        """
        K = np.tan(np.pi * f0 / self.frame_rate())
        K2 = K * K
        norm = 1 / (1 + K/q + K2)

        a1 = 2 * (K2 - 1) * norm
        a2 = (1 - K/q + K2) * norm

        return a1, a2, norm, K

# Following is a suite of subclasses of Biquad2.  Each one initializes the
# filter coefficients according to the filter type.

class BQ2LowPassPE(Biquad2PE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src_pe, frame_rate=frame_rate)

        a1, a2, norm, K = self.default_coeffs(f0, q)
        b0 = K * K * norm
        b1 = 2 * b0
        b2 = b0
        self.set_coefficients(a1, a2, b0, b1, b2)

class BQ2HighPassPE(Biquad2PE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src_pe, frame_rate=frame_rate)
        a1, a2, norm, K = self.default_coeffs(f0, q)
        b0 = norm
        b1 = -2 * b0
        b2 = b0
        self.set_coefficients(a1, a2, b0, b1, b2)

class BQ2BandPassPE(Biquad2PE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        """
        Has 0db gain at f0
        """
        super().__init__(src_pe, frame_rate=frame_rate)
        a1, a2, norm, K = self.default_coeffs(f0, q)
        b0 = K * (norm / q)
        b1 = 0.0
        b2 = -b0
        self.set_coefficients(a1, a2, b0, b1, b2)

class BQ2BandRejectPE(Biquad2PE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        """
        Has 0db gain everywhere except in the vicinity of f0
        """
        super().__init__(src_pe, frame_rate=frame_rate)
        a1, a2, norm, K = self.default_coeffs(f0, q)
        b0 = (K * K + 1) * norm
        b1 = 2 * (K * K -1) * norm
        b2 = b0
        self.set_coefficients(a1, a2, b0, b1, b2)

class BQ2AllPassPE(Biquad2PE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src_pe, frame_rate=frame_rate)
        """
        Has 0db gain everywhere, for real!
        """
        a1, a2, denom, K = self.default_coeffs(f0, q)
        b0 = a2
        b1 = a1
        b2 = 1
        self.set_coefficients(a1, a2, b0, b1, b2)

class BQ2PeakPE(Biquad2PE):
    def __init__(self, src_pe, f0=440, q=20, gain_db=0, frame_rate=None):
        """
        Serves as both a peak filter when gain_db > 0 and a notch filter when
        gain_db < 0.  Has 0db gain everywhere except around f0.
        """
        super().__init__(src_pe, frame_rate=frame_rate)
        K = np.tan(np.pi * f0 / self.frame_rate())
        K2 = K*K
        V = math.pow(10, abs(gain_db) / 20);
        if gain_db >= 0:
            # peaking
            norm = 1 / (1 + K/q + K2)
            a1 = 2 * (K2 - 1) * norm
            a2 = (1 - K/q + K2) * norm
            b0 = (1 + (V*K)/q + K2) * norm
            b1 = a1
            b2 = (1 - (V*K)/q + K2) * norm
        else:
            # notching
            norm = 1 / (1 + (V*K)/q + K2)
            a1 = 2 * (K2 - 1) * norm
            a2 = (1 - (V*K)/q + K2) * norm
            b0 = (1 + K/q + K2) * norm
            b1 = a1
            b2 = (1 - K/q + K2) * norm
        self.set_coefficients(a1, a2, b0, b1, b2)

class BQ2LowShelfPE(Biquad2PE):
    def __init__(self, src_pe, f0=440, gain_db=0, frame_rate=None):
        """
        Has gain_db below f0, has 0db gain above f0.
        """
        super().__init__(src_pe, frame_rate=frame_rate)
        K = np.tan(np.pi * f0 / self.frame_rate())
        K2 = K*K
        V = math.pow(10, abs(gain_db) / 20);
        SQRT2 = math.sqrt(2)

        if gain_db >= 0:
            norm = 1 / (1 + SQRT2 * K + K2);
            a1 = 2 * (K2 - 1) * norm;
            a2 = (1 - SQRT2 * K + K2) * norm;
            b0 = (1 + math.sqrt(2*V) * K + V * K2) * norm;
            b1 = 2 * (V * K2 - 1) * norm;
            b2 = (1 - math.sqrt(2*V) * K + V * K2) * norm;
        else:
            norm = 1 / (1 + math.sqrt(2*V) * K + V * K2);
            b0 = (1 + SQRT2 * K + K2) * norm;
            b1 = 2 * (K2 - 1) * norm;
            b2 = (1 - SQRT2 * K + K2) * norm;
            a1 = 2 * (V * K2 - 1) * norm;
            a2 = (1 - math.sqrt(2*V) * K + V * K2) * norm;
        self.set_coefficients(a1, a2, b0, b1, b2)

class BQ2HighShelfPE(Biquad2PE):
    def __init__(self, src_pe, f0=440, gain_db=0, frame_rate=None):
        super().__init__(src_pe, frame_rate=frame_rate)
        K = np.tan(np.pi * f0 / self.frame_rate())
        K2 = K*K
        V = math.pow(10, abs(gain_db) / 20);
        SQRT2 = math.sqrt(2)
        if gain_db >= 0:
            norm = 1 / (1 + SQRT2 * K + K2);
            a1 = 2 * (K2 - 1) * norm;
            a2 = (1 - SQRT2 * K + K2) * norm;
            b0 = (V + math.sqrt(2*V) * K + K2) * norm;
            b1 = 2 * (K2 - V) * norm;
            b2 = (V - math.sqrt(2*V) * K + K2) * norm;
        else:
            norm = 1 / (V + math.sqrt(2*V) * K + K2);
            a1 = 2 * (K2 - V) * norm;
            a2 = (V - math.sqrt(2*V) * K + K2) * norm;
            b0 = (1 + SQRT2 * K + K2) * norm;
            b1 = 2 * (K2 - 1) * norm;
            b2 = (1 - SQRT2 * K + K2) * norm;
        self.set_coefficients(a1, a2, b0, b1, b2)
