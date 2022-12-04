import numpy as np
from extent import Extent
from pyg_pe import PygPE

class PwmPE(PygPE):
    """
    Generate a rectangular wave with given period and duty cycle.
    """

    def __init__(self, period:int, duty_cycle:np.float32, channel_count=PygPE.DEFAULT_CHANNEL_COUNT):
        super(PwmPE, self).__init__()
        self._period = period
        self._duty_cycle = duty_cycle
        self._channel_count = channel_count

    def render(self, requested:Extent):
        if isinstance(self._period, PygPE):
            period = self._period.render(requested)
        else:
            period = self._period

        if isinstance(self._duty_cycle, PygPE):
            thresh = self._duty_cycle.render(requested) * period
        else:
            thresh = self._duty_cycle * period

        t = np.arange(requested.start(), requested.end()).reshape(-1, 1)
        v = (t % period < thresh).astype(np.float32)
        return v

    def channel_count(self):
        return self._channel_count
