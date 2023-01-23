import numpy as np
from extent import Extent
from pyg_gen import PygGen

class ConstPE(PygGen):
    """
    Generate a constant value.
    """

    def __init__(self, value, frame_rate=None):
        super(ConstPE, self).__init__(frame_rate=frame_rate)
        self._value = value

    def render(self, requested:Extent):
        duration = requested.duration()
        return np.full([1, duration], self._value, dtype=np.float32)

    def channel_count(self):
        return 1
