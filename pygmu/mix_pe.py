import numpy as np
from extent import Extent
from pyg_pe import PygPE

class MixPE(PygPE):
    """
    Mix an arbitrary number of PEs
    """

    def __init__(self, *pes):
        self._pes = pes
        self._has_extent = False
        self._extent = self.compute_extent()

    def render(self, requested:Extent, n_channels:int):
        dstbuf = np.zeros([requested.duration(), n_channels], np.float32)
        has_any_frames = False

        for src_pe in self._pes:
            (srcbuf, offset) = src_pe.render(requested, n_channels)
            if (srcbuf.size > 0):
                # src_pe has frames available in the requested range: sum
                # info dstbuf
                x = min(dstbuf.shape[0], srcbuf.shape[0] - offset)
                dstbuf[offset:offset + srcbuf.shape[0], :] += srcbuf[0:x, :]
                has_any_frames = True
        if has_any_frames:
            return (dstbuf, 0)
        else:
            # optimization so caller doesn't need to process empty frames
            return (np.zeros([0,n_channels], np.float32), 0)

    def extent(self):
        return self._extent

    def compute_extent(self):
        extent = None
        for pe in self._pes:
            # See note in extent.py: Extent.union() should accept *extents
            # return Extent.union([pe.extent() for pe in self._pes])
            if extent is None:
                extent = pe.extent()    # inheret extent from first PE
            else:
                # extend extent to span each pe's extent
                extent = extent.union(pe.extent())
        return extent
