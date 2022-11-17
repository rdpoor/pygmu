import numpy as np
from extent import Extent
from pyg_pe import PygPE


class ReversePE(PygPE):
    """
    reverse the order of a source PE
    """

    def __init__(self, src_pe:PygPE):
        super(ReversePE, self).__init__()
        self._src_pe = src_pe
        #self._extent = self._src_pe.extent()

    def render(self, requested:Extent, n_channels:int):

        intersection = requested.intersect(self.extent())
        if intersection.is_empty():
            # no intersection
            return np.zeros([requested.duration(), n_channels], np.float32)
        elif intersection.equals(requested):
            # full overlap: just grab the corresponding samples and reverse them
            src_extent = Extent(start=self._src_pe.extent().end() - intersection.end(), end=self._src_pe.extent().end() - intersection.start())
            src_buf = self._src_pe.render(src_extent, n_channels)
            return np.flip(src_buf, 0)
        else:
            # Create dst_buf equal to the length of the request.
            # src frames will come from an extent mirrored around the center of the src extent
            # to produce frames that fall within the intersection, then lay
            # the frames into the dst_buf at the required offset
            dst_buf = np.zeros([requested.duration(), n_channels], np.float32)
            src_extent = Extent(start=self._src_pe.extent().end() - intersection.end(), end=self._src_pe.extent().end() - intersection.start())
            src_buf = self._src_pe.render(src_extent, n_channels)
            offset = intersection.start() - requested.start()
            dst_buf[offset:offset + intersection.duration(), :] = src_buf
            return np.flip(dst_buf, 0)

    def extent(self):
        return self._src_pe.extent()
