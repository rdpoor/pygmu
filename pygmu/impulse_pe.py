from pyg_pe import PygPE
from extent import Extent
import utils

class ImpulsePE(PygPE):
    """
    Dirac delta function, also known as the unit impulse, is zero everywhere
    except at zero where its value is 1.0
    """

    def __init__(self):
        super(ImpulsePE, self).__init__()


    def render(self, requested:Extent, n_channels:int):
        dst_buf = utils.const_frames(0.0, requested.duration(), n_channels)
        r0 = requested.start()
        r1 = requested.end()
        if r0 <= 0 and r1 > 0:
            dst_buf[-r0:-r0+1,:] = 1.0
        return dst_buf
