import numpy as np
from extent import Extent
from pyg_pe import PygPE
from compressor_pe import CompressorPE
from env_detect_pe import EnvDetectPE

class LimiterAPE(PygPE):
    """
    Simple amplitude limiter
    """

    def __init__(self, src_pe, threshold_db=-10, headroom_db=3):
        """
        threshold_db sets the limiting point.
        headroom_db sets the output level n db below maximum
        """
        super(LimiterAPE, self).__init__()
        self._src_pe = src_pe
        self._env_detect = EnvDetectPE(src_pe, attack=0.9, release=0.0001)
        self._compressor = CompressorPE(
            src_pe, self._env_detect, threshold_db=threshold_db, ratio=1000,
            post_gain_db = -threshold_db - headroom_db)

    def render(self, requested:Extent):
        return self._compressor.render(requested)

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
