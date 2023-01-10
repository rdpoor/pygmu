import numpy as np
from extent import Extent
from pyg_pe import PygPE

class LimiterPE(PygPE):
    """
    Simple hard amplitude limiter -- because we have no knee, discontinuities will be created
    """

    def __init__(self, src_pe, headroom_db = 2):
        super(LimiterPE, self).__init__()
        self._src_pe = src_pe
        self._observed_max = 0
        self._reduction = 1
        self._hard_limit = 1 - (0.7)

    def render(self, requested:Extent):
        src_buf = self._src_pe.render(requested)
        amax = np.amax(src_buf)
        if amax > self._observed_max:
            self._observed_max = amax
            if amax > self._hard_limit:
                self._reduction = (amax - self._hard_limit) / amax
        #print('self._reduction',self._reduction,self._observed_max)
        return src_buf * self._reduction

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        """
        With no inputs, default to the class definition.  With one or more inputs,
        use the frame_rate of the first input.
        """
        return self._src_pe.frame_rate()

    def channel_count(self):
        """
        With no inputs, default to the class definition.  With one or more inputs,
        use the channel_count of the first input.
        """
        return self._src_pe.channel_count()