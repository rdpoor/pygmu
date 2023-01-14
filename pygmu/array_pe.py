import numpy as np
from extent import Extent
from pyg_gen import PygGen
import utils as ut

class ArrayPE(PygGen):
    """
    A Processing Element with a fixed array of source data.
    """

    def __init__(self, frames, frame_rate=None):
        super(ArrayPE, self).__init__(frame_rate=frame_rate)
        self._frames = np.array(frames, dtype=np.float32)
        n_channels = ut.channel_count(self._frames)
        n_frames = ut.frame_count(self._frames)
        # ArrayPE frames always start at t=0
        self._extent = Extent(start=0, end=n_frames)
        self._channel_count = n_channels

    def render(self, requested:Extent):
        intersection = requested.intersect(self.extent())
        if intersection.is_empty():
            # no intersection
            dst_frames = np.zeros([self.channel_count(), requested.duration()], np.float32)
        else:
            src_frames = self._frames[:,intersection.start():intersection.end()]
            if intersection.equals(requested):
                # full overlap: just return array's frames
                dst_frames = src_frames
            else:
                # partial overlap: create dst_frames equal to the length of the
                # request and selectively overwrite dst_frames from src_frames.
                dst_frames = np.zeros([self.channel_count(), requested.duration()], np.float32)
                offset = intersection.start() - requested.start()
                n_frames = intersection.duration()
                dst_frames[:,offset:offset + n_frames] = src_frames
        return dst_frames

    def extent(self):
        return self._extent

    def channel_count(self):
        return self._channel_count
