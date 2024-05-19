import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class WaveShapePE(PygPE):
    """
    Apply wave shaping to a pe. The wave shaping effect is achieved by applying
    a nonlinear transformation function to the input signal.
    """

    def __init__(self, src_pe, shaping_func):
        super(WaveShapePE, self).__init__()
        self._src_pe = src_pe
        self._shaping_func = shaping_func
        self._lfo_phase = 0

    def render(self, requested: Extent):
        overlap = requested.intersect(self.extent())
        if overlap.is_empty():
            return ut.const_frames(0.0, self.channel_count(), requested.duration())

        n_samples = overlap.duration()
        frame_rate = self.frame_rate()

        input_frames = self._src_pe.render(overlap)
        output_frames = self._shaping_func(input_frames)

        return output_frames

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
