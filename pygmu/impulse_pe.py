from pygmu.pyg_pe import PygPE
from pygmu.extent import Extent
import pygmu.utils

class ImpulsePE(PygPE):
    """
    Dirac delta function, also known as the unit impulse, is zero everywhere
    except at zero where its value is 1.0
    """

    def __init__(self, channel_count=PygPE.DEFAULT_CHANNEL_COUNT):
        super(ImpulsePE, self).__init__()
        self._channel_count = channel_count


    def render(self, requested:Extent):
        dst_buf = utils.const_frames(0.0, requested.duration(), self.channel_count())
        r0 = requested.start()
        r1 = requested.end()
        if r0 <= 0 and r1 > 0:
            dst_buf[-r0:-r0+1,:] = 1.0
        return dst_buf

    def channel_count(self):
        return self._channel_count
