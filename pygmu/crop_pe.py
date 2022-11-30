import numpy as np
from pygmu.extent import Extent
from pygmu.pyg_pe import PygPE

class CropPE(PygPE):
    """
    Crop the start and/or end time of a source PE
    """

    def __init__(self, src_pe:PygPE, extent:Extent):
        super(CropPE, self).__init__()
        self._src_pe = src_pe
        self._extent = extent.intersect(src_pe.extent())

    def render(self, requested:Extent):

        intersection = requested.intersect(self.extent())
        if intersection.is_empty():
            # no intersection
            return np.zeros([requested.duration(), self.channel_count()], np.float32)
        elif intersection.equals(requested):
            # full overlap: just return src_pe's frames
            return self._src_pe.render(intersection)
        else:
            # Create dst_buf equal to the length of the request.  Ask src_pe
            # to produce frames that fall within the intersection, then lay
            # the frames into the dst_buf at the required offset
            dst_buf = np.zeros([requested.duration(), self.channel_count()], np.float32)
            src_buf = self._src_pe.render(intersection)
            offset = intersection.start() - requested.start()
            src_n_frames = intersection.duration()
            assert(src_n_frames == src_buf.shape[0])
            dst_buf[offset:offset + src_n_frames, :] = src_buf
            return dst_buf

    def extent(self):
        return self._extent

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
