import numpy as np
from extent import Extent
from pyg_pe import PygPE

class DelayPE(PygPE):
    """
    Delay a PE by a fixed number of samples
    """

    def __init__(self, pe, delay=0):
        self._pe = pe
        self._delay = delay

    def render(self, requested, n_channels):
        return self._pe.render(-self._delay, n_channels)

    def n_channels(self):
        return self._pe.n_channels()

    def extent(self):
        return self._pe.extent().offset(self._delay)
