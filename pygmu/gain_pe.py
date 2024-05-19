import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut
from pyg_gen import PygGen, FrequencyMixin

class GainPE(PygGen, PygPE):
    """
    Apply gain to a pe.  Gain can be constant or a processing element.
    """

    def __init__(self, src_pe, gain, units=None):
        super(GainPE, self).__init__()
        self._src_pe = src_pe
        self._gain = gain
        self._units = units

    def render(self, requested:Extent):
        if isinstance(self._gain, PygPE):
            # gain is the output of a PE.  Render the values and use them.
            overlap = requested.intersect(self.extent())
            dst_frames = ut.const_frames(0.0, self.channel_count(), requested.duration())
            if overlap.is_empty():
                # no overlap - dst_frames is already zero
                pass
            else:
                # nonzero overlap - render src and scale by gain, then overwrite
                # scaled frames in dst_frames
                n = overlap.duration()
                gain_frames = self._gain.render(overlap)
                if self._units == 'db':
                    gain_frames = ut.db_to_ratio(gain_frames)
                src_frames = self._src_pe.render(overlap) * gain_frames
                dst_idx = overlap.start() - requested.start()
                # dst_idx is the index into dst_frames where src_buf[0] gets written
                dst_frames[:, dst_idx:dst_idx+n] = src_frames
                print('gain:', gain_frames)

        else:
            # gain is constant.
            gain = self._gain
            if self._units == 'db':
                gain = ut.db_to_ratio(self._gain)
            dst_frames = self._src_pe.render(requested) * gain
        return dst_frames

    def extent(self):
        if isinstance(self._gain, PygPE):
            return self._src_pe.extent().intersect(self._gain.extent())
        else:
            return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
