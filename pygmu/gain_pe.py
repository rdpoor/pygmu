import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class GainPE(PygPE):
    """
    Apply gain to a pe.  Gain can be constant or a processing element.
    """

    def __init__(self, src_pe, gain):
        super(GainPE, self).__init__()
        self._src_pe = src_pe
        self._gain = gain

    def render(self, requested:Extent):
        if isinstance(self._gain, PygPE):
            # gain is the output of a PE.  Render the values and use them.
            overlap = requested.intersect(self.extent())
            dst_buf = ut.const_frames(0.0, requested.duration(), self.channel_count())
            if overlap.is_empty():
                # no overlap - dst_buf is already zero
                pass
            else:
                # nonzero overlap - render src and scale by gain, then overwrite
                # scaled frames in dst_buf
                n = overlap.duration()
                src_buf = self._src_pe.render(overlap) * self._gain.render(overlap)
                dst_idx = overlap.start() - requested.start()
                # dst_idx is the index into dst_buf where src_buf[0] gets written
                dst_buf[dst_idx:dst_idx+n,:] = src_buf
        else:
            # gain is constant.
            dst_buf = self._src_pe.render(requested) * self._gain
        return dst_buf

    def extent(self):
        if isinstance(self._gain, PygPE):
            return self._src_pe.extent().intersect(self._gain.extent())
        else:
            return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
