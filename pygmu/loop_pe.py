import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class LoopPE(PygPE):
    """
    Loop source from loop_start to loop_start + loop_duration
    """

    def __init__(self, src_pe, loop_duration:float):
        super(LoopPE, self).__init__()
        self._src_pe = src_pe
        self._dur = loop_duration

    def render(self, requested:Extent):
        src_buf = self._src_pe.render(Extent(0, self._dur))
        dst_buf = ut.uninitialized_frames(self.channel_count(), requested.duration())
        dst_ndx = 0
        dst_size = requested.duration()
        src_ndx = requested.start() % self._dur
        while dst_ndx < dst_size:
            # limit the size of this pass to the smaller of remaining requested frames or remaining frames in the source loop
            src_size = min(dst_size - dst_ndx, min(self._dur - src_ndx, dst_size)) 
            dst_buf[:, dst_ndx:dst_ndx + src_size] = src_buf[:, src_ndx:src_ndx + src_size]
            dst_ndx += src_size
            src_ndx = 0
        return dst_buf

    def extent(self):
        return Extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()