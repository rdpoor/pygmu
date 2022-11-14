import numpy as np
from extent import Extent
from pyg_pe import PygPE
from transport import Transport

class UnitPE(PygPE):
    """
    The UnitPE is the function f(t) = t
    """

    def __init__(self):
        super(UnitPE, self).__init__()

    def render(self, requested:Extent, n_channels:int):
        t0 = requested.start()
        t1 = requested.end()
        dst_buf = np.tile(np.arange(t0, t1).reshape(-1, 1), (1, n_channels))
        return dst_buf
