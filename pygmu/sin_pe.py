import numpy as np
from extent import Extent
from pyg_pe import PygPE
from transport import Transport

class SinPE(PygPE):
    """
    Generate a sine wave with fixed frequency, phase and amplitude.
    """

    def __init__(self, frequency=440, amplitude=1.0, phase=0.0, n_channels=1):
        self._omega = frequency * 2.0 * np.pi / Transport.FRAME_RATE
        self._amplitude = amplitude
        self._phase = phase
        self._n_channels = n_channels

    def render(self, requested):
        t0 = requested.start()
        t1 = requested.end()
        frames = np.tile(np.arange(t0, t1).reshape(-1, 1), (1, self._n_channels))
        return self._amplitude * np.sin(self._omega * frames + self._phase).astype(np.float32)

    def n_channels(self):
        return self._n_channels
