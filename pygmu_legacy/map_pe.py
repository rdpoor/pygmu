import numpy as np
from extent import Extent
from pyg_pe import PygPE

class MapPE(PygPE):
    """
    Map input to output through a user-supplied function.  The user supplied
    function takes one argument, a numpy 2D array, and is expected to return
    the same.
    """

    def __init__(self, src_pe, user_fn):
        super(MapPE, self).__init__()
        self._src_pe = src_pe
        self._user_fn = user_fn

    def render(self, requested:Extent):
        src_frames = self._src_pe.render(requested)
        dst_frames = self._user_fn(src_frames)
        return dst_frames

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()

