import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class InterpolatePE(PygPE):
    """
    crudely resample
    """

    def __init__(self, src_pe:PygPE, speed_mult):
        super(InterpolatePE, self).__init__()
        self._src_pe = src_pe
        self._speed_mult = speed_mult

    def render(self, requested):
        extent = self.extent()
        overlap = extent.intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, requested.duration(), self.channel_count())
        # request the relevant extent of the source, grab an extra frame at end for interpolation of the last frame(s)        
        interp_requested = Extent(round(requested.start() * self._speed_mult), round((requested.end()) * self._speed_mult) + self.channel_count()) 
        src_frames = self._src_pe.render(interp_requested)
        dst_frames = ut.uninitialized_frames(self.channel_count(),requested.duration())
        print(src_frames.shape,dst_frames.shape)
        #dst_frames[0] = self._prev_frame_kludge
        for i in range(round(overlap.duration())):
            # idx_f is fractional index into src_frames.  linear interpolate...
            idx_f = i * self._speed_mult
            idx_i = int(np.floor(idx_f))
            idx_rem = idx_f - idx_i  # 0.0 <= idx_rem < 1.0
            frame = src_frames[idx_i] + idx_rem * (src_frames[idx_i + 1] - src_frames[idx_i])
            dst_frames[i] = frame
        return dst_frames

    def extent(self):
        # our extent is simply the source's extent, divided by our speed multiplier
        # for example, if our speed_mult is 2, then our extent will be half as long as the source
        return Extent(round(self._src_pe.extent().start()) / self._speed_mult,round(self._src_pe.extent().end() / self._speed_mult))

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
