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
        self._loop_dur = loop_duration

    def render(self, requested):
        dst_dur = requested.duration()     # number of frames to render
        dst_frames = np.ndarray([self.channel_count(), dst_dur]) # output buffer
        src_idx = requested.start() % self._loop_dur # starting index
        dst_idx = 0                      # how many frames written to dst_frames
        # At this point:
        #   dst_dur is the number of frames to be written
        #   dst_frames is a butffer to received the frames
        #   src_idx is the starting index into the source data
        #   dst_idx is the number of frames written.
        #
        # The number of frames that can be copied in each time around the loop
        # will be limited by the number of frames remaining to be written
        # (write_avail) or when we run into the end of the source loop 
        # (read_avail). 
        while dst_idx < dst_dur:
            write_avail = dst_dur - dst_idx
            read_avail = self._loop_dur - src_idx
            avail = min(read_avail, write_avail)

            # fetch avail src_frames, insert into dst_frames
            src_frames = self._src_pe.render(Extent(src_idx, src_idx+avail))
            dst_frames[:, dst_idx:dst_idx + avail] = src_frames

            # increment read and write indeces
            src_idx = (src_idx + avail) % self._loop_dur
            dst_idx += avail

        return dst_frames

    def extent(self):
        # Extent goes infinitely into the past and future...
        return Extent()

    def frame_rate(self):
        # Inherited from source
        return self._src_pe.frame_rate()

    def channel_count(self):
        # inherited from source
        return self._src_pe.channel_count()

