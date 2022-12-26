import numpy as np
from scipy import signal
from abs_pe import AbsPE
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class EnvDetectPE(PygPE):
    """
    Simple envelope detector.
    """

    def __init__(self, src_pe, attack=0.9, release=1.0):
        self._src_pe = AbsPE(src_pe)
        self._attack = attack
        self._release = release
        self._env = ut.const_frames(0.0, src_pe.channel_count(), 1)

    def render(self, requested:Extent):
        overlap = self._src_pe.extent().intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, requested.duration(), self.channel_count())

        src = self._src_pe.render(requested)
        dst = ut.uninitialized_frames(*src.shape)
        for i, s in enumerate(src):
            self._env = self.track(self._env, s)
            dst[i] = self._env
        return dst

    def extent(self):
        return self._src_pe.extent()

    def channel_count(self):
        return self._src_pe.channel_count()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def track(self, state, sample):
        delta = sample - state
        if delta > 0:
            return state + delta * self._attack
        else:
            return state + delta * self._release
