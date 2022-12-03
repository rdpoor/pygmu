import numpy as np
from extent import Extent
from pyg_pe import PygPE

class SinPE(PygPE):
    """
    Generate a sine wave with fixed frequency, phase and amplitude.
    """

    def __init__(self, frequency=440, amplitude=1.0, phase=0.0, frame_rate=PygPE.DEFAULT_FRAME_RATE, channel_count=PygPE.DEFAULT_CHANNEL_COUNT):
        super(SinPE, self).__init__()
        self._omega = frequency * 2.0 * np.pi / frame_rate
        self._amplitude = amplitude
        self._phase = phase    # in radians
        self._frame_rate = frame_rate
        self._channel_count = channel_count

    def render(self, requested:Extent):
        t0 = requested.start()
        t1 = requested.end()
        t = np.tile(np.arange(t0, t1).reshape(-1, 1), (1, self.channel_count()))
        return self._amplitude * np.sin(self._omega * t + self._phase).astype(np.float32)

    def frame_rate(self):
        return self._frame_rate

    def channel_count(self):
        return self._channel_count
