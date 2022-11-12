import numpy as np
from extent import Extent
from pyg_pe import PygPE
from transport import Transport

class SinPE(PygPE):
    """
    Generate a sine wave with fixed frequency, phase and amplitude.
    """

    def __init__(self, frequency=440, amplitude=1.0, phase=0.0):
        self._w = frequency * 2.0 * np.pi / Transport.FRAME_RATE
        self._amp = amplitude
        self._phase = phase

    def render(self, requested:Extent, n_channels:int):
        t0 = requested.start()
        t1 = requested.end()
        frames = np.tile(np.arange(t0, t1).reshape(-1, 1), (1, n_channels))
        theta = self._w * frames + self._phase
        # since sin() has infinite extent, the offset is always 0
        return (self._amp * np.sin(theta).astype(np.float32), 0)
