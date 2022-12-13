import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class LoopAPE(PygPE):
    """
    Loop source from loop_start to loop_start + loop_duration
    """

    def __init__(self, src_pe, loop_start:float, loop_duration:float):
        super(LoopAPE, self).__init__()
        self._src_pe = src_pe
        self._insk = loop_start
        self._dur = loop_duration

    def render(self, requested:Extent):
    	src_loop_extent = Extent(self._insk, (self._insk + self._dur))
    	src_buf = self._src_pe.render(src_loop_extent)
    	dst_buf = ut.uninitialized_frames(requested.duration(), self.channel_count())
    	dst_ndx = 0
    	dst_size = requested.duration()
    	src_size = src_loop_extent.duration()
    	src_ndx = requested.start() % src_size
    	while dst_ndx < dst_size:
    		src_cnt = min(dst_size - dst_ndx,min(src_size - src_ndx, dst_size)) #limit the size of this pass to the smaller of remaining requested frames or remaining frames in the loop
    		dst_buf[dst_ndx:dst_ndx + src_cnt, :] = src_buf[src_ndx:src_ndx + src_cnt, :]
    		dst_ndx += src_cnt
    		src_ndx = 0
    	return dst_buf

    def extent(self):
        return Extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()