import numpy as np
from pyg_gen import PygGen

class NoisePE(PygGen):
    """
    Generate white noise evenly distibuted between +/- gain
    """

    def __init__(self, gain=1.0, frame_rate=None):
        super(NoisePE, self).__init__(frame_rate=frame_rate)
        self._gain = gain

    def render(self, requested):
        noise = np.random.random((1, requested.duration())) * 2.0 - 1.0
        # TODO: support dynamic gain
        return noise * self._gain

    def channel_count(self):
        return 1
