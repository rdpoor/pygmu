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
        times = self._timeline.render(requested).reshape(-1)
        tmin = int(np.floor(np.min(times)))
        tmax = int(np.ceil(np.max(times)))
        # fetch src_pe's frames between tmin and tmax
        extent = Extent(tmin, tmax+2)
        if extent.is_empty():
            return ut.const_frames(0.0, requested.duration(), self.channel_count())
        src_frames = self._src_pe.render(extent)
        # allocate resulting frames
        dst_frames = ut.uninitialized_frames(requested.duration(), self.channel_count())
        for i in range(requested.duration()):
            # idx_f is fractional index into src_frames.  linear interpolate...
            # TODO: vectorize?
            idx_f = times[i] - tmin
            idx_i = int(np.floor(idx_f))
            idx_rem = idx_f - idx_i  # 0.0 <= idx_rem < 1.0
            #print(i, times[i], idx_f, idx_i, idx_rem)
            # Andy has remove the fractional interpolation here because it can create discontinuities aka clicks at frame rendering boundaries TBD
            #frame = src_frames[idx_i] + idx_rem * (src_frames[idx_i + 1] - src_frames[idx_i])
            #dst_frames[i] = frame
            dst_frames[i] = src_frames[idx_i]
        return dst_frames


    def extent(self):
        """Assume that timeline defines the extent"""
        return self._timeline.extent()

        

    def channel_count(self):
        return self._src_pe.channel_count()
