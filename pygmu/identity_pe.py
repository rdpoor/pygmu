import numpy as np
from extent import Extent
from pyg_pe import PygPE

class IdentityPE(PygPE):
    """
    The IdentityPE is the function f(t) = t
    """

    def __init__(self, channel_count=PygPE.DEFAULT_CHANNEL_COUNT):
        super(IdentityPE, self).__init__()
        self._channel_count = channel_count

    def render(self, requested:Extent):
        t0 = requested.start()
        t1 = requested.end()
        dst_buf = np.tile(np.arange(t0, t1).reshape(-1, 1), (1, self.channel_count()))
        return dst_buf

    def channel_count(self):
        return self._channel_count
