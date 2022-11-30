import numpy as np
from pygmu.extent import Extent
from pygmu.pyg_pe import PygPE

class ArrayPE(PygPE):
    """
    A Processing Element with a fixed array of source data.
    """

    def __init__(self, frames, channel_count=PygPE.DEFAULT_CHANNEL_COUNT):
        super(ArrayPE, self).__init__()
        self._frames = frames
        self._extent = Extent(start=0, end=frames.shape[0])
        self._channel_count = channel_count

    def render(self, requested:Extent):
        intersection = requested.intersect(self.extent())
        if intersection.is_empty():
            # no intersection
            dst_frames = np.zeros([requested.duration(), self.channel_count()], np.float32)
        else:
            src_frames = self._frames[intersection.start():intersection.end(),:]
            if intersection.equals(requested):
                # full overlap: just return array's frames
                dst_frames = src_frames
            else:
                # partial overlap: create dst_frames equal to the length of the
                # request and selectively overwrite dst_frames from src_frames.
                dst_frames = np.zeros([requested.duration(), self.channel_count()], np.float32)
                offset = intersection.start() - requested.start()
                n_frames = intersection.duration()
                dst_frames[offset:offset + n_frames, :] = src_frames
        return dst_frames

    def extent(self):
        return self._extent

    def channel_count(self):
        return self._channel_count
