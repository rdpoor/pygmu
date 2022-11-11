import numpy as np
from extent import Extent
from pyg_pe import PygPE

class MulPE(PygPE):
    """
    Multiply an arbitrary number of PEs
    """

    def __init__(self, *pes):
        self._pes = pes
        self._has_extent = False
        self._extent = None  # evaluate on demand

    def render(self, requested, n_channels):
        outbuf = np.ones([requested.duration(), n_channels]).astype(np.float32)
        for pe in self._pes:
            overlap = requested.intersect(pe.extent())
            if overlap is not None:
                # this PE has frames available in the requested range
                # compute the index of the first overlapping sample and multiply
                # starting there.
                delta = overlap.start() - requested.start()
                outbuf[delta:] *= pe.render(overlap, n_channels)
        return outbuf

    def extent(self):
        # lazy evaluation of extent
        if not self._has_extent:
            self._extent = None
            for pe in self._pes:
                if self._extent is None:
                    self._extent = pe.extent()    # inheret extent from first PE
                else:
                    # extend extent to span each pe's extent
                    self._extent = self._extent.union(pe.extent())
            self._has_extent = true
        return extent
