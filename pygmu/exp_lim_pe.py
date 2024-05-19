import numpy as np
from extent import Extent
from pyg_pe import PygPE

class ExpanderLimiterPE(PygPE):
    def __init__(self, src_pe, target_amp=1.0, release_time=0.1, frame_rate=None):
        super(ExpanderLimiterPE, self).__init__()
        self._src_pe = src_pe
        self.target_amp = target_amp
        self.release_time = release_time
        self._frame_rate = frame_rate
        if self._frame_rate is None:
            self._frame_rate = self._src_pe.frame_rate()
        self.gain = 1.0
        self.release_coeff = np.exp(-1.0 / (self.release_time * self._frame_rate))

    def render(self, requested):
        overlap = requested.intersect(self.extent())
        if overlap.is_empty():
            return np.zeros((self.channel_count(), requested.duration()), dtype=np.float32)

        src_frames = self._src_pe.render(overlap)
        dst_frames = np.zeros((self.channel_count(), requested.duration()), dtype=np.float32)

        for i in range(overlap.duration()):
            max_amp = np.max(np.abs(src_frames[:, i]))
            if max_amp > 0:
                target_gain = self.target_amp / max_amp
            else:
                target_gain = 1.0  # Handle the case of 0 amplitude

            self.gain += (target_gain - self.gain) * (1 - self.release_coeff)
            dst_frames[:, i] = src_frames[:, i] * self.gain

        return dst_frames

    def extent(self):
        return self._src_pe.extent()

    def channel_count(self):
        return self._src_pe.channel_count()

    def frame_rate(self):
        return self._frame_rate