import numpy as np
from pygmu.extent import Extent
from pygmu.pyg_pe import PygPE

class MixPE(PygPE):
    """
    Mix an arbitrary number of PEs
    """

    def __init__(self, *pes):
        super(MixPE, self).__init__()
        self._pes = pes
        self._has_extent = False
        self._extent = self.compute_extent()

    def render(self, requested:Extent):
        dst_buf = np.zeros([requested.duration(), self.channel_count()], np.float32)
        for src_pe in self._pes:
            dst_buf += src_pe.render(requested)
        return dst_buf

    def extent(self):
        return self._extent

    def frame_rate(self):
        """
        With no inputs, default to the class definition.  With one or more inputs,
        use the frame_rate of the first input.
        """
        if len(self._pes) == 0:
            return super.frame_rate()
        else:
            return self._pes[0].frame_rate()

    def channel_count(self):
        """
        With no inputs, default to the class definition.  With one or more inputs,
        use the frame_rate of the first input.
        """
        if len(self._pes) == 0:
            return super.channel_count()
        else:
            return self._pes[0].channel_count()

    def compute_extent(self):
        if len(self._pes) == 0:
            return Extent()
        else:
            # start with the extent of the first pe, extend it by taking the
            # union with each following pe's extent.
            extent = self._pes[0].extent()
            for pe in self._pes[1:]:
                extent = extent.union(pe.extent())
            return extent

 