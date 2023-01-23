import numpy as np
from extent import Extent
from pyg_gen import PygGen

class IdentityPE(PygGen):
    """
    The IdentityPE is the function f(t) = t
    """

    def __init__(self, frame_rate=None):
        super(IdentityPE, self).__init__(frame_rate=frame_rate)

    def render(self, requested:Extent):
        t0 = requested.start()
        t1 = requested.end()
        return np.arange(t0, t1).reshape(1, -1)

    def channel_count(self):
        return 1
