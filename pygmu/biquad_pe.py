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
    BANDREJECT = "bandreject"
    ALLPASS = "allpass"
    RESONATOR = "resonator"

    def __init__(self, src_pe, center_freq, q, filter_type="bandpass"):
        super(BiquadPE, self).__init__()
        self._src_pe = src_pe
        self._filter_type = filter_type
        self._a = np.zeros(3, dtype=np.float32)
        self._b = np.zeros(3, dtype=np.float32)
        self._inputs = np.zeros(3, dtype=np.float32)
        self._outputs = np.zeros(3, dtype=np.float32)
        self.set_coefficients(center_freq, q)

    def render(self, requested:Extent):
        src_frames = self._src_pe.render(requested)
        # nb: Tricky code: src_frames.shape => (n_frames, n_channels), which 
        # happens to be the two arguments needed by ut.uninitialized_frames()
        dst_frames = ut.uninitialized_frames(*src_frames.shape)
        for i, src_frame in enumerate(src_frames):
            self._inputs[0] = src_frame
            dst_frame = (self._b[0] * self._inputs[0] +
                        self._b[1] * self._inputs[1] +
                        self._b[2] * self._inputs[2] -
                        self._a[2] * self._outputs[2] -
                        self._a[1] * self._outputs[1])
            self._inputs[2] = self._inputs[1]
            self._inputs[1] = self._inputs[0]
            self._outputs[2] = self._outputs[1]
            self._outputs[1] = dst_frame
            dst_frames[i] = dst_frame
        return dst_frames

    def extent(self):
        return self._src_pe.extent()

    def channel_count(self):
        return self._src_pe.channel_count()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def set_coefficients(self, center_freq, q):
        K_ = np.tan(np.pi * center_freq / self.frame_rate())
        kSqr_ = K_ * K_
        denom_ = 1 / (kSqr_ * q + K_ + q)

        self._a[0] = 1.0
        self._a[1] = 2 * q * (kSqr_ - 1) * denom_
        self._a[2] = (kSqr_ * q - K_ + q) * denom_

        if self._filter_type == self.LOWPASS:
            self._b[0] = kSqr_ * q * denom_
            self._b[1] = 2 * self._b[0]
            self._b[2] = self._b[0]
        elif self._filter_type == self.HIGHPASS:
            self._b[0] = q * denom_
            self._b[1] = -2 * self._b[0]
            self._b[2] = self._b[0]
        elif self._filter_type == self.BANDPASS:
            self._b[0] = K_ * denom_
            self._b[1] = 0.0
            self._b[2] = -self._b[0]
        elif self._filter_type == self.BANDREJECT:
            self._b[0] = q * (kSqr_ + 1) * denom_
            self._b[1] = 2 * q * (kSqr_ - 1) * denom_
            self._b[2] = self._b[0]
        elif self._filter_type == self.ALLPASS:
            self._b[0] = self._a[2]
            self._b[1] = self._a[1]
            self._b[2] = 1
        elif self._filter_type == self.RESONATOR:
            # q is interpreted as 0.0 < radius < 1.0
            self._a[2] = q * q
            self._a[1] = -2.0 * q * np.cos(2 * np.pi * center_freq / self.frame_rate())
            self._b[0] = 0.5 - 0.5 * self._a[2]
            self._b[1] = 0.0
            self._b[2] = -self._b[0]
        else:
            print("Unrecognized filter type")

