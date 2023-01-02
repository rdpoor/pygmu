import numpy as np
from extent import Extent
from pyg_pe import PygPE
from array_pe import ArrayPE

class CachePE(PygPE):
    """
    Cache the samples from the src_pe to save recomputing.
    """

    def __init__(self, src_pe):
        super(CachePE, self).__init__()
        self._src_pe = src_pe
        src_extent = src_pe.extent()
        if src_extent.is_indefinite():
            raise pex.IndefiniteExtent("src to CachePE cannot have indefinite extent")
        # Slurp all samples into an ArrayPE
        self._cached_pe = ArrayPE(src_pe.render(src_extent))

    def render(self, requested:Extent):
        return self._cached_pe.render(requested)

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
