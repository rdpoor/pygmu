import numpy as np
from extent import Extent
from pyg_pe import PygPE

class DelayPE(PygPE):
    """
    Delay a PE by a fixed number of frames

    e.g.:
    src.extent() = [0:100]
    delay = 3
    self.extent() = [3, 103]

    request = [0,100]
    src_buf = render([-3, 97])
    ... src will handle the rest...
    """

    def __init__(self, src_pe:PygPE, delay=0):
        self._src_pe = src_pe
        self._delay = delay
        self._extent = src_pe.extent().offest(delay)

    def render(self, requested:Extent, n_channels:int):
        return self._src_pe.render(requested.offset(-self._delay), n_channels)

    def extent(self):
        return self._extent
