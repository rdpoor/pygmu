import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut
import random

class GranularPE(PygPE):
    """
    Apply granular synthesis to a pe. This effect involves dividing a sound into small segments
    (grains) and manipulating and recombining them to create new textures and effects.
    """

    def __init__(self, src_pe, grain_size=0.81, grain_overlap=0.15, frame_rate=48000):
        super(GranularPE, self).__init__()
        self._src_pe = src_pe
        self._grain_size = grain_size
        self._grain_overlap = grain_overlap
        self._frame_rate = frame_rate
        self._grain_size_frames = int(grain_size * frame_rate)
        self._grain_step_frames = int(self._grain_size_frames * (1 - grain_overlap))
        self._grain_window = np.hanning(self._grain_size_frames)  # Hanning window


    def render(self, requested: Extent):
        print('requested duration:', requested.duration())
        print('grain_size', self._grain_size, 'grain_overlap', self._grain_overlap, '_grain_step_frames', self._grain_step_frames, 'grain_size_frames', self._grain_size_frames, 'grain_window', self._grain_window)

        overlap = requested.intersect(self.extent())
        if overlap.is_empty():
            return ut.const_frames(0.0, self.channel_count(), requested.duration())

        input_frames = self._src_pe.render(overlap)
        output_frames = np.zeros((self.channel_count(), requested.duration()))
        out_step = self._grain_step_frames * (1 - self._grain_overlap)

        num_grains = (requested.duration() + self._grain_step_frames - 1) // self._grain_step_frames
        #num_grains += 100
        print('num_grains:', num_grains)
        for i in range(num_grains):
            grain_start = i * self._grain_step_frames
            grain_end = grain_start + self._grain_size_frames

            if grain_end > input_frames.shape[1]:
                continue

            print('grain_start', i, 'grain_start frame:', grain_start, 'grain_end frame:', grain_end)

            grain = input_frames[:, grain_start:grain_end]
            windowed_grain = grain * self._grain_window[:grain.shape[1]]

            output_start = int(i * out_step * random.uniform(0.2, 2.7))
            output_end = int(output_start + self._grain_size_frames)
            print('output_start frame:', output_start, 'output_end frame:', output_end)

            output_frames[:, output_start:output_end] += windowed_grain

        return output_frames

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
