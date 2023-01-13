import numpy as np
from extent import Extent
from pyg_pe import PygPE
import pyg_exceptions as pyx

class SinPE(PygPE):
    """
    Generate a sine wave with fixed frequency, phase and amplitude.
    """

    def __init__(self, frequency=440, amplitude=1.0, phase=0.0, frame_rate=None):
        super(SinPE, self).__init__()
        if frame_rate is None:
            raise pyx.ArgumentError("frame_rate must be specified")
        self._frame_rate = frame_rate
        self._omega = frequency * 2.0 * np.pi / frame_rate
        self._amplitude = amplitude
        self._phase = phase    # in radians

    def render(self, requested:Extent):
        t0 = requested.start()
        t1 = requested.end()
        t = np.arange(t0, t1)
        return self._amplitude * np.sin(self._omega * t + self._phase).astype(np.float32).reshape(1, -1)

    def frame_rate(self):
        return self._frame_rate

    def channel_count(self):
        return 1
