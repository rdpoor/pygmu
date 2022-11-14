import numpy as np
from extent import Extent
from pyg_pe import PygPE
from transport import Transport

class ImpulsePE(PygPE):
    """
    Dirac delta function, also known as the unit impulse, is zero everywhere
    except at zero where its value is 1.0
    """

    def __init__(self):
        super(ImpulsePE, self).__init__()


    def render(self, requested:Extent, n_channels:int):
        dst_buf = np.zeros([requested.duration(), n_channels], np.float32)
        if requesteed.start() <= 0 and requested.end() > 0:
            dst_buf[-requested.start():] = 1.0
        return dst_buf
