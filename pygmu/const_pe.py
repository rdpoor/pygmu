import numpy as np
from extent import Extent
from pyg_pe import PygPE

class ConstPE(PygPE):
    """
    Generate a constant value.
    """

    def __init__(self, value:np.float32):
        self._value = value

    def render(self, requested:Extent, n_channels:int):
        duration = requested.duration()
        return np.full([duration, n_channels], self._value, dtype=np.float32)
