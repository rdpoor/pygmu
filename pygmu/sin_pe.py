import numpy as np
from extent import Extent
from pyg_gen import PygGen
import pyg_exceptions as pyx

class SinPE(PygGen):
    """
    Generate a sine wave with fixed frequency, phase and amplitude.
    """

    def __init__(self, frequency=440, amplitude=1.0, phase=0.0, frame_rate=None):
        super(SinPE, self).__init__(frame_rate=frame_rate)
        if frame_rate is None:
            raise pyx.FrameRateMismatch("frame_rate must be specified")
        self._omega = frequency * 2.0 * np.pi / frame_rate
        self._amplitude = amplitude
        self._phase = phase    # in radians

    def render(self, requested:Extent):
        t0 = requested.start()
        t1 = requested.end()
        t = np.arange(t0, t1)
        return self._amplitude * np.sin(self._omega * t + self._phase).astype(np.float32).reshape(1, -1)

    def channel_count(self):
        return 1
