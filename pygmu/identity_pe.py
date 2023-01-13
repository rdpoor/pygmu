import numpy as np
from extent import Extent
from pyg_pe import PygPE

class IdentityPE(PygPE):
    """
    The IdentityPE is the function f(t) = t
    """

    def __init__(self):
        super(IdentityPE, self).__init__()

    def render(self, requested:Extent):
        t0 = requested.start()
        t1 = requested.end()
        return np.arange(t0, t1).reshape(1, -1)

    def channel_count(self):
        return 1
