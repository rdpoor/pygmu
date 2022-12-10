import numpy as np
from pyg_pe import PygPE

class NoisePE(PygPE):
    """
    Generate white noise evenly distibuted between +/- gain
    """

    def __init__(self, gain = 1.0, channel_count=PygPE.DEFAULT_CHANNEL_COUNT):
        super(NoisePE, self).__init__()
        self._gain = gain
        self._channel_count = channel_count

    def render(self, requested):
        noise = np.random.random((requested.duration(), self._channel_count)) * 2.0 - 1.0
        # TODO: support dynamic gain
        return noise * self._gain

    def channel_count(self):
        return self._channel_count
