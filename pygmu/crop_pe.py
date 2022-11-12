import numpy as np
from extent import Extent
from pyg_pe import PygPE

class CropPE(PygPE):
    """
    Crop the start and/or end time of a source PE
    """

    def __init__(self, src:PygPE, extent:Extent):
        self._src = src
        self._extent = extent.intersect(src.extent())

    def render(self, requested:Extent, n_channels:int):
        intersection = requested.intersect(self.extent())
        if intersection.is_empty():
            # no overlap at all.
            return (np.zeros([0, n_channels], np.float32), 0)
        else:
            # partial or full overlap
            offset = intersection.start() - requested.start()
            (buf, ignored) = self._src.render(requested, n_channels)
            return (buf, offset)

    def extent(self):
        return self._extent
