import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class TimewarpPE(PygPE):
    """
    Remap time.
    """


    def __init__(self, src_pe, timeline):
        super(TimewarpPE).__init__()
        self._src_pe = src_pe
        self._timeline = timeline

    def render(self, requested):
        times = self._timeline.render(requested)
        tmin = int(np.floor(np.min(times)))
        tmax = int(np.ceil(np.max(times)))
        # fetch src_pe's frames between tmin and tmax
        extent = Extent(tmin, tmax+2)
        # print(extent, extent.duration())
        src_frames = self._src_pe.render(extent)
        # allocate resulting frames
        dst_frames = ut.uninitialized_frames(requested.duration(), self.channel_count())
        for i in range(requested.duration()):
            # idx_f is fractional index into src_frames.  linear interpolate...
            # TODO: vectorize?
            idx_f = times[i] - tmin
            idx_i = int(np.floor(idx_f))
            idx_rem = idx_f - idx_i  # 0.0 <= idx_rem < 1.0
            # print(i, times[i], idx_f, idx_i, idx_rem)
            frame = src_frames[idx_i] + idx_rem * (src_frames[idx_i + 1] - src_frames[idx_i])
            dst_frames[i] = frame
        return dst_frames


    def extent(self):
        """Assume that timeline defines the extent, not src_pe"""
        return self._timeline.extent()

    def channel_count(self):
        return self._src_pe.channel_count()
