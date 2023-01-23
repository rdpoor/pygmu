import numpy as np
from extent import Extent
from pyg_pe import PygPE
import pyg_exceptions as pyx

"""
Spread a single-channel streeam into N channels.
"""

class SpreadPE(PygPE):
    """
    Spread a single-channle source equally into N channels
    """

    def __init__(self, src_pe, channel_count=2):
        """
        Spread single-channel src_pe into n-channels.
        """
        super(SpreadPE, self).__init__()
        if src_pe.channel_count() != 1:
            raise pyx.ChannelCountMismatch("spread input must be single channel")
        self._src_pe = src_pe
        self._channel_count = channel_count

    def render(self, requested:Extent):
        src_frames = self._src_pe.render(requested)
        return src_frames.repeat(self._channel_count, axis=0)

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._channel_count
