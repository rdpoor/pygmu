import numpy as np
from extent import Extent
from pyg_gen import PygGen, FrequencyMixin
import pyg_exceptions as pyx

class SinPE(FrequencyMixin, PygGen):
    """
    Generate a sine wave with flexible frequency, phase, and amplitude.
    """

    def __init__(self, frequency=440, amplitude=1.0, phase=0.0, frame_rate=None):
        super(SinPE, self).__init__(frame_rate=frame_rate)
        if frame_rate is None:
            raise pyx.FrameRateMismatch("frame_rate must be specified")
        self._frame_rate = frame_rate
        self.set_frequency(frequency)  # This will now call the method from FrequencyMixin
        self._amplitude = amplitude
        self._phase = phase    # in radians

    def render(self, requested:Extent):
        t0 = requested.start()
        t1 = requested.end()
        t = np.arange(t0, t1)
        frequency = self.get_frequency(requested)  # This will now call the method from FrequencyMixin
        if isinstance(frequency, np.ndarray):
            return self.render_dynamic(t, frequency)
        else:
            omega = frequency * 2.0 * np.pi / self._frame_rate
            return self._amplitude * np.sin(omega * t + self._phase).astype(np.float32).reshape(1, -1)

    def render_dynamic(self, t, freqs):
        dst_frames = np.full(len(t), 0.0, dtype=np.float32)

        for idx, freq in enumerate(freqs):
            omega = freq * 2.0 * np.pi / self._frame_rate
            dst_frames[idx] = self._amplitude * np.sin(phase)
            self._phase += omega
        
        return dst_frames.reshape(1, -1)

    def channel_count(self):
        return 1

    def frame_rate(self):
        return self._frame_rate
