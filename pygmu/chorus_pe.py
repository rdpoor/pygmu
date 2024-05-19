import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class ChorusPE(PygPE):
    """
    Apply chorus effect to a pe. The chorus effect is achieved by modulating
    the delay time of the input signal and mixing it with the original signal.
    """

    def __init__(self, src_pe, rate=1.5, depth=0.5, mix=0.5):
        super(ChorusPE, self).__init__()
        self._src_pe = src_pe
        self._rate = rate
        self._depth = depth
        self._mix = mix
        self._lfo_phase = 0

    def render(self, requested: Extent):
        overlap = requested.intersect(self.extent())
        if overlap.is_empty():
            return ut.const_frames(0.0, self.channel_count(), requested.duration())

        n_samples = overlap.duration()
        frame_rate = self.frame_rate()
        output_frames = ut.const_frames(0.0, self.channel_count(), n_samples)
        input_frames = self._src_pe.render(overlap)
        
        # Create an LFO (Low-Frequency Oscillator) for modulation
        lfo = np.sin(2 * np.pi * self._rate * np.arange(n_samples) / frame_rate)
        delay_samples = self._depth * (1 + lfo) * frame_rate / 1000
        self._lfo_phase = (self._lfo_phase + n_samples) % frame_rate

        for i in range(n_samples):
            delay = int(delay_samples[i])
            if i - delay < 0:
                output_frames[:, i] = input_frames[:, i]
            else:
                output_frames[:, i] = (1 - self._mix) * input_frames[:, i] + \
                                      self._mix * input_frames[:, i - delay]

        return output_frames

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
