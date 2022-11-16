import numpy as np
from extent import Extent
from pyg_pe import PygPE
from transport import Transport

class SinPE(PygPE):
    """
    Generate a sine wave with fixed frequency, phase and amplitude.
    """

    def __init__(self, frequency=440, amplitude=1.0, phase=0.0):
        super(SinPE, self).__init__()
        self._omega = frequency * 2.0 * np.pi / Transport.FRAME_RATE
        self._amplitude = amplitude
        self._phase = phase    # in radians

    def render(self, requested:Extent, n_channels:int):
        t0 = requested.start()
        t1 = requested.end()
        t = np.tile(np.arange(t0, t1).reshape(-1, 1), (1, n_channels))
        return self._amplitude * np.sin(self._omega * t + self._phase).astype(np.float32)
