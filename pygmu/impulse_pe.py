from pyg_gen import PygGen
from extent import Extent
import utils

class ImpulsePE(PygGen):
    """
    Dirac delta function, also known as the unit impulse, is zero everywhere
    except at zero where its value is 1.0
    """

    def __init__(self, frame_rate=None):
        super(ImpulsePE, self).__init__(frame_rate=frame_rate)

    def render(self, requested:Extent):
        dst_buf = utils.const_frames(0.0, 1, requested.duration())
        r0 = requested.start()
        r1 = requested.end()
        if r0 <= 0 and r1 > 0:
            dst_buf[:, -r0] = 1.0
        return dst_buf

    def channel_count(self):
        return 1
