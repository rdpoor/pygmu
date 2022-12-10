import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

# Work in progress.  See also:
# https://github.com/hosackm/BiquadFilter/blob/master/Biquad.h
# https://github.com/hosackm/BiquadFilter/blob/master/Biquad.c

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
    LOWSHELF = "lowshelf"
    HIGHSHELF = "highshelf"

    def __init__(self, src_pe, db_gain, center_freq, q, filter_type="bandpass"):
        super(BiquadPE, self).__init__()
        self._src_pe = src_pe
        self._db_gain = db_gain
        self._filter_type = filter_type
        self._a = np.zeros(3, dtype=np.float32)
        self._b = np.zeros(3, dtype=np.float32)
        self._x = np.zeros(3, dtype=np.float32)
        self._y = np.zeros(3, dtype=np.float32)
        self.set_coefficients(db_gain, center_freq, q)

    def render(self, requested:Extent):
        src_frames = self._src_pe.render(requested)
        # nb: Tricky code: src_frames.shape => (n_frames, n_channels), which 
        # happens to be the two arguments needed by ut.uninitialized_frames()
        dst_frames = ut.uninitialized_frames(*src_frames.shape)
        for i, x in enumerate(src_frames):
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

    def set_coefficients(self, db_gain, center_freq, q):
        # A is only used for PEAK, NOTCH, SHELF.
        # TODO: consider different constructors
        A = np.power(10, db_gain / 40)  # ?
        omega = 2.0 * np.pi * center_freq / self.frame_rate()
        sn = np.sin(omega)
        cs = np.cos(omega)
        print(omega, sn, cs, q)
        alpha = sn / (2.0 * q)
        beta = np.sqrt(A + A)

        # K_ = np.tan(np.pi * center_freq / self.frame_rate())
        # kSqr_ = K_ * K_
        # denom_ = 1 / (kSqr_ * q + K_ + q)
        # self._a[0] = 1.0
        # self._a[1] = 2 * q * (kSqr_ - 1) * denom_
        # self._a[2] = (kSqr_ * q - K_ + q) * denom_

        if self._filter_type == self.LOWPASS:
            self._b[0] = (1 - cs) / 2
            self._b[1] = 1 - cs
            self._b[2] = (1 - cs) / 2
            self._a[0] = 1 + alpha
            self._a[1] = -2 * cs
            self._a[2] = 1 - alpha
        elif self._filter_type == self.HIGHPASS:
            self._b[0] = (1 + cs) / 2
            self._b[1] = -(1 + cs)
            self._b[2] = (1 + cs) / 2
            self._a[0] = 1 + alpha
            self._a[1] = -2 * cs
            self._a[2] = 1 - alpha
        elif self._filter_type == self.BANDPASS:
            self._b[0] = alpha
            self._b[1] = 0
            self._b[2] = -alpha
            self._a[0] = 1 + alpha
            self._a[1] = -2 * cs
            self._a[2] = 1 - alpha
        elif self._filter_type == self.ALLPASS:
            self._b[0] = 1 - alpha
            self._b[1] = -2 * cs
            self._b[2] = 1 + alpha
            self._a[0] = 1 + alpha
            self._a[1] = -2 * cs
            self._a[2] = 1 - alpha
        elif self._filter_type == self.PEAK:
            self._b[0] = 1 + (alpha * A)
            self._b[1] = -2 * cs
            self._b[2] = 1 - (alpha * A)
            self._a[0] = 1 + (alpha / A)
            self._a[1] = -2 * cs
            self._a[2] = 1 - (alpha / A)
        elif self._filter_type == self.NOTCH:
            self._b[0] = 1
            self._b[1] = -2 * cs
            self._b[2] = 1
            self._a[0] = 1 + (alpha / A)
            self._a[1] = -2 * cs
            self._a[2] = 1 - (alpha / A)
        elif self._filter_type == self.LOWSHELF:
            self._b[0] = A * ((A + 1) - (A - 1) * cs + beta * sn)
            self._b[1] = 2 * A * ((A - 1) - (A + 1) * cs)
            self._b[2] = A * ((A + 1) - (A - 1) * cs - beta * sn)
            self._a[0] = (A + 1) + (A - 1) * cs + beta * sn
            self._a[1] = -2 * ((A - 1) + (A + 1) * cs)
            self._a[2] = (A + 1) + (A - 1) * cs - beta * sn
        elif self._filter_type == self.HIGHSHELF:
            self._b[0] = A * ((A + 1) + (A - 1) * cs + beta * sn)
            self._b[1] = -2 * A * ((A - 1) + (A + 1) * cs)
            self._b[2] = A * ((A + 1) + (A - 1) * cs - beta * sn)
            self._a[0] = (A + 1) - (A - 1) * cs + beta * sn
            self._a[1] = 2 * ((A - 1) - (A + 1) * cs)
            self._a[2] = (A + 1) - (A - 1) * cs - beta * sn
        else:
            print("Unrecognized filter type")

        # Normalize coefficients
        self._b[0] /= self._a[0]
        self._b[1] /= self._a[0]
        self._b[2] /= self._a[0]
        self._a[1] /= self._a[0]
        self._a[2] /= self._a[0]

        print("a[]=", self._a, "b[]=", self._b)
        