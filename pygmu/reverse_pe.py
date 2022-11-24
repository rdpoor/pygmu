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
        self._gave_warning = False
    def render(self, requested:Extent):
        intersection = requested.intersect(self.extent())
        if intersection.is_empty():
            # no intersection
            return np.zeros([requested.duration(), self.channel_count()], np.float32)
        elif intersection.equals(requested):
            # full overlap: just grab the corresponding samples and reverse them
            if self._src_pe.extent().is_indefinite() and not self._gave_warning:
                print('reverse is unhappy with an indefinite source, hacked at 45 for now:',self._src_pe)
                self._gave_warning = True
            #src_extent = Extent(start=self._src_pe.extent().end() - intersection.end(), end=self._src_pe.extent().end() - intersection.start())
            fake_end = 5 * self._src_pe.frame_rate()
            src_extent = Extent(start=fake_end - intersection.end(), end=fake_end - intersection.start())
            src_buf = self._src_pe.render(src_extent)
            return np.flip(src_buf, 0)
        else:
            # Create dst_buf equal to the length of the request.
            # src frames will come from an extent mirrored around the center of the src extent
            # to produce frames that fall within the intersection, then lay
            # the frames into the dst_buf at the required offset
            dst_buf = np.zeros([requested.duration(), self.channel_count()], np.float32)
            src_extent = Extent(start=self._src_pe.extent().end() - intersection.end(), end=self._src_pe.extent().end() - intersection.start())
            src_buf = self._src_pe.render(src_extent)
            offset = intersection.start() - requested.start()
            dst_buf[offset:offset + intersection.duration(), :] = src_buf
            return np.flip(dst_buf, 0)

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
