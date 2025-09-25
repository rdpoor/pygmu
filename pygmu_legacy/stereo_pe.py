import numpy as np
from extent import Extent
from pyg_pe import PygPE

class StereoPE(PygPE):
    """
    Convert a mono source to stereo by duplicating the channel.
    If the source is already stereo, pass it through directly.
    """

    def __init__(self, src_pe):
        super(StereoPE, self).__init__()
        self._src_pe = src_pe

    def render(self, requested: Extent):
        buf = self._src_pe.render(requested)
        if buf.shape[0] == 1:
            buf = np.vstack([buf, buf])
        return buf

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return 2
