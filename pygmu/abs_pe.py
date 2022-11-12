import numpy as np
from extent import Extent
from pyg_pe import PygPE

class AbsPE(PygPE):
    """
    Take the absolute value of the input PE
    """

    def __init__(self, src:PygPE):
        self._src = src

    def render(self, requested:Extent, n_channels:int):
        (srcbuf, offset) = self._src.render(requested, n_channels)
        return (np.abs(srcbuf), offset)

    def extent(self):
        return self._src.extent()
