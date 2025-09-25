import numpy as np
from extent import Extent
from pyg_gen import PygGen
from pyg_pe import PygPE
import pyg_exceptions as pyx

class PwmPE(PygGen):
    """
    Generate a rectangular wave with given period and duty cycle.  Note that 
    period is the number of frames per period, duty_cycle is the ratio of time 
    it spends = 1.0.  A duty_cycle of 0.0 is low all the time, 0.5 is high half
    the time, 1.0 is high all the time (like some friends I know).

    Note also that period and duty_cycle can be a constant or the output of 
    another PE.  

    No attempt is made to protect against oddball values (negative duty cycle,
    etc).

    """

    def __init__(self, period:int, duty_cycle:np.float32, frame_rate=None):
        super(PwmPE, self).__init__(frame_rate=frame_rate)
        if isinstance(period, PygPE) and period.channel_count() != 1:
            raise pyx.ChannelCountMismatch("PwmPE period must be 1 channel")
        if isinstance(duty_cycle, PygPE) and duty_cycle.channel_count() != 1:
            raise pyx.ChannelCountMismatch("PwmPE duty_cycle must be 1 channel")
        self._period = period
        self._duty_cycle = duty_cycle

    def render(self, requested:Extent):
        if isinstance(self._period, PygPE):
            # period is the output of a PE.  Render the values and use them.
            period = self._period.render(requested)
            period[np.where(period<1)] = 1;  # enforce positive period
        else:
            # period is constant.
            period = self._period

        if isinstance(self._duty_cycle, PygPE):
            # duty_cycle is the output of a PE.  Render the values and use them.
            thresh = self._duty_cycle.render(requested) * period
        else:
            # duty_cycle is constant.  
            thresh = self._duty_cycle * period

        # t is simply a vector of time values.
        t = np.arange(requested.start(), requested.end()).reshape(1, -1)
        # t % period counts from 0 to period
        # (t % period < thresh) is true when t MOD period is less than thresh
        # (t % period < thresh).astype(np.float32) coerces True=1.0, False=0.0
        # print("pwm", period.shape, thresh.shape, t.shape)
        v = (t % period < thresh).astype(np.float32)
        return v

    def channel_count(self):
        return 1
