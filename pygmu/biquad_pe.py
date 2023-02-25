import numpy as np
from scipy import signal
from extent import Extent
from pyg_pe import PygPE
import pyg_exceptions as pyx
import utils as ut

# Work in progress.  See also:
# https://github.com/hosackm/BiquadFilter/blob/master/Biquad.h
# https://github.com/thestk/stk/blob/master/include/BiQuad.h
# https://github.com/thestk/stk/blob/master/src/BiQuad.cpp
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt.html
#
# Game Plan:
# * mono, fixed params, discrete inner loop using stk biquad model
# * verify results with audio
# * stereo, verify
# * stereo, variable F0, verify
# * stereo, variable bandwidth, verify

class BiquadPE(PygPE):
    """
    Two pole / two zero filter
    """

    LOWPASS = "lowpass"
    HIGHPASS = "highpass"
    BANDPASS = "bandpass"
    ALLPASS = "allpass"
    PEAK = "peak"
    NOTCH = "notch"
    # LOWSHELF = "lowshelf"
    # HIGHSHELF = "highshelf"

    def __init__(self, src_pe, db_gain=0, f0=440, q=20, filter_type="lowpass", frame_rate=None):
        """
        BiQuad filter.  db_gain, f0, q can be constant or other PEs.
        Note that db_gain is used only for PEAK, NOTCH, LOWSHELF, HIGHSHELF
        """
        super(BiquadPE, self).__init__()
        self._src_pe = src_pe
        self._db_gain = db_gain
        self._f0 = f0
        self._q = q
        self._filter_type = filter_type
        self._frame_rate = frame_rate
        if self._frame_rate is None:
            self._frame_rate = src_pe.frame_rate()
        if self._frame_rate is None:
            raise pyx.FrameRateMismatch("frame_rate must be specified")
        # filter coefficients [b0, b1, b2, a0, a1, a2]
        self._coeffs = np.zeros(6, dtype=np.float32)
        # filter initial state (carried over between calls to render)
        self._zinit = np.zeros((self.channel_count(), 1, 2), dtype=np.float32)

    def render(self, requested:Extent):
        overlap = self._src_pe.extent().intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, requested.duration(), self.channel_count())

        src_frames = self._src_pe.render(requested)

        # optimize case for constant coefficients.
        all_constant = True

        if isinstance(self._db_gain, PygPE):
            # db_gain is an array of time-varying numbers
            db_gain = self._db_gain.render(requested)
            all_constant = False
        else:
            # db_gain is a constant
            db_gain = self._db_gain
        if isinstance(self._f0, PygPE):
            # f0 is an array of time-varying numbers
            f0 = self._f0.render(requested)
            all_constant = False
        else:
            # f0 is a constant
            f0 = self._f0
        if isinstance(self._q, PygPE):
            # q is an array of time-varying numbers
            q = self._q.render(requested)
            all_constant = False
        else:
            # q is a constant
            q = self._q


        if all_constant:
            self.set_coefficients(db_gain, f0, q)
            x = src_frames.transpose()  # as expected by sosfilt
            y, self._zinit = signal.sosfilt(self._coeffs, x, zi=self._zinit)
            return y.transpose()

        else:
            # nb: Tricky code: src_frames.shape => (n_frames, n_channels), which
            # are the two arguments needed by ut.uninitialized_frames()
            dst_frames = ut.uninitialized_frames(*src_frames.shape)
            # this feels really messy.  expand constant coeffs into arrays.
            if not isinstance(db_gain, np.ndarray):
                db_gain = ut.const_frames(db_gain, len(src_frames), 1)
            if not isinstance(f0, np.ndarray):
                f0 = ut.const_frames(f0, len(src_frames), 1)
            if not isinstance(q, np.ndarray):
                q = ut.const_frames(q, len(src_frames), 1)

        for i, x in enumerate(src_frames):
            if all_constant == False:
                self.set_coefficients(db_gain[i][0], f0[i][0], q[i][0])

            y = (self._b[0] * x +
                 self._b[1] * self._x[1] +
                 self._b[2] * self._x[2] -
                 self._a[1] * self._y[1] -
                 self._a[2] * self._y[2])
            self._x[2] = self._x[1]
            self._x[1] = x
            self._y[2] = self._y[1]
            self._y[1] = y
            dst_frames[i] = y
        return dst_frames

    def extent(self):
        return self._src_pe.extent()

    def channel_count(self):
        return self._src_pe.channel_count()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def set_coefficients(self, db_gain, f0, q):
        # db_gain is only used for PEAK, NOTCH, *SHELF.
        # TODO: consider different constructors for those...
        A = np.power(10, db_gain / 40)  # ?
        omega = 2.0 * np.pi * f0 / self.frame_rate()
        sn = np.sin(omega)
        cs = np.cos(omega)
        alpha = sn / (2.0 * q)
        beta = np.sqrt(A + A)
        # print(db_gain, f0, q, A, omega, sn, cs, alpha, beta)

        # K_ = np.tan(np.pi * f0 / self.frame_rate())
        # kSqr_ = K_ * K_
        # denom_ = 1 / (kSqr_ * q + K_ + q)
        # self._a[0] = 1.0
        # self._a[1] = 2 * q * (kSqr_ - 1) * denom_
        # self._a[2] = (kSqr_ * q - K_ + q) * denom_

        if self._filter_type == self.LOWPASS:
            self._coeffs = [
                (1 - cs) / 2,  # b0
                1 - cs,        # b1
                (1 - cs) / 2,  # b2
                1 + alpha,     # a0
                -2 * cs,       # a1
                1 - alpha      # a2
                ]
        elif self._filter_type == self.HIGHPASS:
            self._coeffs = [
                (1 + cs) / 2,  # b0
                -(1 + cs),     # b1
                (1 + cs) / 2,  # b2
                1 + alpha,     # a0
                -2 * cs,       # a1
                1 - alpha      # a2
                ]
        elif self._filter_type == self.BANDPASS:
            self._coeffs = [
                alpha,         # b0
                0,             # b1
                -alpha,        # b2
                1 + alpha,     # a0
                -2 * cs,       # a1
                1 - alpha      # a2
                ]
        elif self._filter_type == self.ALLPASS:
            self._coeffs = [
                1 - alpha,     # b0
                -2 * cs,       # b1
                1 + alpha,     # b2
                1 + alpha,     # a0
                -2 * cs,       # a1
                1 - alpha      # a2
                ]
        elif self._filter_type == self.PEAK:
            self._coeffs = [
                1 + (alpha * A), # b0
                -2 * cs,         # b1
                1 - (alpha * A), # b2
                1 + (alpha / A), # a0
                -2 * cs,         # a1
                1 - (alpha / A)  # a2
                ]
        elif self._filter_type == self.NOTCH:
            self._coeffs = [
                1,               # b0
                -2 * cs,         # b1
                1,               # b2
                1 + (alpha / A), # a0
                -2 * cs,         # a1
                1 - (alpha / A)  # a2
                ]
        elif self._filter_type == self.LOWSHELF:
            self._coeffs = [
                A * ((A + 1) - (A - 1) * cs + beta * sn), # b0
                2 * A * ((A - 1) - (A + 1) * cs),         # b1
                A * ((A + 1) - (A - 1) * cs - beta * sn), # b2
                (A + 1) + (A - 1) * cs + beta * sn,       # a0
                -2 * ((A - 1) + (A + 1) * cs),            # a1
                (A + 1) + (A - 1) * cs - beta * sn        # a2
                ]
        elif self._filter_type == self.HIGHSHELF:
            self._coeffs = [
                A * ((A + 1) + (A - 1) * cs + beta * sn), # b0
                -2 * A * ((A - 1) + (A + 1) * cs),        # b1
                A * ((A + 1) + (A - 1) * cs - beta * sn), # b2
                (A + 1) - (A - 1) * cs + beta * sn,       # a0
                -2 * ((A - 1) + (A + 1) * cs),            # a1
                (A + 1) - (A - 1) * cs - beta * sn        # a2
                ]
        else:
            print("Unrecognized filter type")

        # Normalize coefficients
        a0 = self._coeffs[3]
        self._coeffs /= a0
        # print("self._coeffs =", self._coeffs)

A0 = 0
A1 = 1
A2 = 2
B0 = 3
B1 = 4
B2 = 5

class BQPE(PygPE):

    def __init__(self, src, frame_rate=None):
        self._src = src
        self.frame_rate = frame_rate
        if self.frame_rate is None:
            self.frame_rate = src.frame_rate()
        if self._frame_rate is None:
            raise pyx.FrameRateMismatch("frame_rate must be specified")
        self._coeffs = None

    def extent(self):
        return self._src.extent()

    def frame_rate(self):
        return self._frame_rate

    def set_coeffs(self, coeffs):
        self._coeffs = coeffs

    def render(self, requested):

        n_frames = requested.duration()
        X = src.render(requested)
        Y = np.zeros((1, n_frames))
        # unpack for inner loop
        a1 = coeffs[A1]
        a2 = coeffs[A2]
        b0 = coeffs[B0]
        b1 = coeffs[B1]
        b2 = coeffs[B2]
        x2 = self._x2
        x1 = self._x1
        y2 = self._y2
        y1 = self._y1
        for i in np.arange(len(X)):
            x0 = X[i]
            y0 = (b0 * x0 + b1 * x1 + b2 * x2) - (a1 * y1 + a2 * y2)
            Y[i] = y0
            x2 = x1
            x1 = x0
            y2 = y1
            y1 = y0
        # repack for next frame...
        self._x2 = x2
        self._x1 = x1
        self._y2 = y2
        self._y1 = y1

  return y0;

  def default_coeffs(self, f0, q):
        coeffs = np.ndarray(6, dtype=np.float32)
        K = np.tan(np.pi * f0 / self.frame_rate)
        K2 = K * K
        denom = 1 / (K2 * q + K + q)

        coeffs[A0] = 0
        coeffs[A1] = 2 * q * (K2 - 1) * denom
        coeffs[A2] = (K2 * q - K + q) * denom

        return coeffs, denom, K

class BQLowPassPE(BiQuadPE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src, frame_rate)

        coeffs, denom, K = self.default_coeffs(f0, q)
        coeffs[B0] = K * K * q * denom
        coeffs[B1] = 2 * coeffs[B0]
        coeffs[B2] = coeffs[B0]
        self.set_coeffs(coeffs)

class BQHighPassPE(BiQuadPE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src, frame_rate)
        coeffs, denom, K = self.default_coeffs(f0, q)
        coeffs[B0] = q * denom
        coeffs[B1] = -2 * coeffs[B0]
        coeffs[B2] = coeffs[B0]
        self.set_coeffs(coeffs)

class BQBandPassPE(BiQuadPE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src, frame_rate)
        coeffs, denom, K = self.default_coeffs(f0, q)
        coeffs[B0] = K * denom
        coeffs[B1] = 0.0
        coeffs[B2] = -coeffs[B0]
        self.set_coeffs(coeffs)

class BQBandRejectPE(BiQuadPE):
    def __init__(self, src_pe, f0=440, q=20, frame_rate=None):
        super().__init__(src, frame_rate)
        coeffs, denom, K = self.default_coeffs(f0, q)
        coeffs[B0] = q * (K * K + 1) * denom
        coeffs[B1] = 2 * q * (K * K -1) * denom
        coeffs[B2] = -coeffs[B0]
        self.set_coeffs(coeffs)

class BQAllPassPE(BiQuadPE):
    def __init__(self, src_pe, f0=440, radius=0.5, frame_rate=None):
        super().__init__(src, frame_rate)
        coeffs, denom, K = self.default_coeffs(f0, q)
        coeffs[B0] = coeffs[A2]
        coeffs[B1] = coeffs[A1]
        coeffs[B2] = 1
        self.set_coeffs(coeffs)

class BQPeakPE(BiQuadPE):
    def __init__(self, src_pe, f0=440, radius=0.5, normalize=false, frame_rate=None):
        super().__init__(src, frame_rate)

        coeffs = np.ndarray(6, dtype=np.float32)
        coeffs[A1] = -2 * radius * np.cos(np.pi * np.pi * f0 / self.frame_rate())
        coeffs[A2] = radius * radius
        coeffs[B0] = 1.0
        coeffs[B1] = 0.0
        coeffs[B2] = 0.0
        if normalize:
            # place zeros at +/- 1
            coeffs[B0] = 0.5 - 0.5 * coeffs[A2]
            coeffs[B2] = -coeffs[B0]
        self.set_coeffs(coeffs)

class BQNotchPE(BiQuadPE):
    def __init__(self, src_pe, f0=440, radius=0.5, frame_rate=None):
        # This method does not attempt to normalize the filter gain.
        coeffs = np.ndarray(6, dtype=np.float32)

        coeffs[A1] = 0.0
        coeffs[A2] = 0.0
        coeffs[B0] = 1.0
        coeffs[B1] = -2 * radius * np.cos(np.pi * np.pi * f0 / self.frame_rate())
        coeffs[B2] = radius * radius
        self.set_coeffs(coeffs)

class BQLowShelfPE(BiQuadPE):
    def __init__(self, src_pe, f0=440, q=20, gain_db=0, frame_rate=None):
        A = np.power(10, db_)
        coeffs = self.low_shelf_coeffs(f0, radius, frame_rate)
        super().__init__(src, coeffs)

class BQHighShelfPE(BiQuadPE):
    def __init__(self, src_pe, f0=440, q=20, gain_db=0, frame_rate=None):
        coeffs = self.high_shelf_coeffs(f0, radius, frame_rate)
        super().__init__(src, coeffs)
