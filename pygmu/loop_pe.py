import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class LoopPE(PygPE):
    """
    Repeat source from 0 to loop_length indefinitely...
    """

    def __init__(self, src_pe, loop_length):
        super(LoopPE, self).__init__()
        self._src_pe = src_pe
        self._loop_length = loop_length

    def render(self, requested:Extent):
        dst_length = requested.duration()
        dst_frames = ut.uninitialized_frames(dst_length, self.channel_count())
        dst_idx = 0
        s = requested.start() % self._loop_length
        while dst_idx < requested.duration():
            e = self._loop_length - s
            if e < s:
                e = self._loop_length
            n = min(e - s, dst_length - dst_idx)
            if n <= 0:
                break          # TODO: code smell.  
            # at this point
            # s = start time to render
            # e = end time to render
            # n = # of frames in segment
            # dst_idx = index into dst_frames where first src_frame is written
            src_frames = self._src_pe.render(Extent(s, s+n))
            dst_frames[int(dst_idx):int(dst_idx+n),:] = src_frames
            dst_idx += n
            s = (s + n) % self._loop_length
        return dst_frames

    def extent(self):
        return Extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
