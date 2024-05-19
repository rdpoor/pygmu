import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class NormalizePE(PygPE):
    """
    Normalize/denormalize the signal amplitude on-the-fly to maintain close to max loudness (1.0).
    """
    def __init__(self, src_pe, release_time=0.1, frame_rate=48000):
        super(NormalizePE, self).__init__()
        self._src_pe = src_pe
        self._release_time = release_time
        self._frame_rate = frame_rate
        self._scaling_value = 1.0
        self._target_level = 1.0  # Desired target level (max loudness)

    def render(self, requested: Extent):
        overlap = requested.intersect(self.extent())
        print('requested',requested.duration())
        if overlap.is_empty():
            return ut.const_frames(0.0, self.channel_count(), requested.duration())

        input_frames = self._src_pe.render(overlap)
        output_frames = np.zeros_like(input_frames)
        
        # Release factor based on the release time and frame rate
        release_factor = np.exp(-1 / (self._release_time * self._frame_rate))

        # Process each sample to normalize amplitude
        for i in range(input_frames.shape[1]):
            current_sample = input_frames[:, i]
            peak = np.max(np.abs(current_sample))
            if peak > 0:
                target_scaling_value = self._target_level / peak
                self._scaling_value = max(self._scaling_value * release_factor, target_scaling_value)
            
            output_frames[:, i] = current_sample * self._scaling_value
            if i % 1000 == 0:  # Print every 1000 samples for debugging
                print(f"Sample {i}: Scaling value: {self._scaling_value} peak: {peak}")

        return output_frames

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()