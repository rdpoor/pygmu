import numpy as np
from pygmu.extent import Extent
from pygmu.pyg_pe import PygPE

class ConstPE(PygPE):
    """
    Generate a constant value.
    """

    def __init__(self, value:np.float32, channel_count=PygPE.DEFAULT_CHANNEL_COUNT):
        super(ConstPE, self).__init__()
        self._value = value
        self._channel_count = channel_count

    def render(self, requested:Extent):
        duration = requested.duration()
        return np.full([duration, self.channel_count()], self._value, dtype=np.float32)

    def channel_count(self):
        return self._channel_count
