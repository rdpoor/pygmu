import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut
from pyg_gen import PygGen

class AddPE(PygGen, PygPE):
    """
    Simple addition, likely in service of a control signal, since MixPE is better suited for audio.
    """
    def __init__(self, src_pe, src_pe2):
        super(AddPE, self).__init__()
        self._src_pe = src_pe
        self._src_pe2 = src_pe2
        self._extent = self.compute_extent()

    def render(self, requested:Extent):
        dst_frames = self._src_pe.render(requested) + self._src_pe2.render(requested)
        return dst_frames

    def extent(self):
        return self._extent

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count() # todo: what if channel counts are different?

    def compute_extent(self):
        return self._src_pe.extent().union(self._src_pe2.extent())