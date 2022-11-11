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
        self._extent = None  # evaluate on demand

    def render(self, requested, n_channels):
        outbuf = None

        outbuf = np.zeros([requested.duration(), n_channels]).astype(np.float32)
        for pe in self._pes:
            overlap = requested.intersect(pe.extent())
            if overlap is not None:
                # this PE has frames available in the requested range
                # add this pe's data to outbuf: compute the index of the first
                # overlapping sample and sum starting there.
                delta = overlap.start() - requested.start()
                outbuf[delta:] += pe.render(overlap, n_channels)
        return outbuf

    def extent(self):
        # lazy evaluation of extent
        if not self._has_extent:
            self._extent = self.compute_extent()
            self._has_extent = True
        return self._extent

    def compute_extent(self):
        extent = None
        for pe in self._pes:
            if extent is None:
                extent = pe.extent()    # inheret extent from first PE
            else:
                # extend extent to span each pe's extent
                extent = extent.union(pe.extent())
        return extent
