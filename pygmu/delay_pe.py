import numpy as np
from extent import Extent
from pyg_pe import PygPE

class DelayPE(PygPE):
    """
    Delay a PE by a fixed number of frames
    """

    def __init__(self, src_pe:PygPE, delay=0):
        super(DelayPE, self).__init__()
        self._src_pe = src_pe
        self._delay = delay
        self._extent = src_pe.extent().offset(delay)

    def render(self, requested:Extent):
        return self._src_pe.render(requested.offset(-self._delay))

    def extent(self):
        return self._extent

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
