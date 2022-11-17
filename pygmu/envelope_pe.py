import numpy as np
from extent import Extent
from pyg_pe import PygPE
from linear_ramp_pe import LinearRampPE


class EnvelopePE(PygPE):
    """
    put simple fades on beginning and end
    """

    def __init__(self, src_pe:PygPE, fade_in_dur, fade_out_dur):
        super(EnvelopePE, self).__init__()
        self._src_pe = src_pe
        self._fade_in_dur = fade_in_dur
        self._fade_out_dur = fade_out_dur

    def render(self, requested:Extent, n_channels:int):

        intersection = requested.intersect(self.extent())
        if intersection.is_empty():
            # no intersection
            return np.zeros([requested.duration(), n_channels], np.float32)

        if intersection.equals(requested):
            # full overlap
            src_buf = self._src_pe.render(intersection, n_channels)
            end_frame = self._src_pe.extent().end()
            in_ramp = LinearRampPE(0,1,Extent(start=0,end=self._fade_in_dur)).render(intersection, n_channels)
            out_ramp = LinearRampPE(1,0,Extent(start=end_frame - self._fade_out_dur,end=end_frame)).render(intersection, n_channels)
            return src_buf * in_ramp * out_ramp
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
            return np.flip(dst_buf, 0);

    def extent(self):
        return self._src_pe.extent()
