import numpy as np
from extent import Extent
from pyg_pe import PygPE

class DelayPE(PygPE):
    """
    Delay a PE by a fixed number of samples
    """

    def __init__(self, src:PygPE, delay=0):
        self._src = src
        self._delay = delay

    def render(self, requested:Extent, n_channels:int):
        intersection = requested.intersect(self.extent())
        offset = intersection.start() - requested.start()
        (buf, ignored) = self._src.render(-self._delay, n_channels)
        return (buf, offset)

    def n_channels(self):
        return self._src.n_channels()

    def extent(self):
        return self._src.extent().offset(self._delay)
