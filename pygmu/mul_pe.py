import numpy as np
from extent import Extent
from pyg_pe import PygPE

class MulPE(PygPE):
    """
    Multiply an arbitrary number of PEs
    """

    def __init__(self, *pes):
        super(MulPE, self).__init__()
        self._pes = pes
        self._has_extent = False
        self._extent = self.compute_extent()

    def render(self, requested:Extent, n_channels:int):
        dst_buf = np.ones([requested.duration(), n_channels], np.float32)
        for src_pe in self._pes:
            dst_buf[:] *= src_pe.render(requested, n_channels)
        return dst_buf

    def extent(self):
        return self._extent

    def compute_extent(self):
        if len(self._pes) == 0:
            return Extent()
        else:
            extent = self._pes[0].extent()
            for pe in self._pes[1:]:
                extent = extent.union(pe.extent())
            return extent
