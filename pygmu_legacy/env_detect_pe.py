import numpy as np
from scipy import signal
from abs_pe import AbsPE
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class EnvDetectPE(PygPE):
    """
    Simple envelope detector.  If units = 'db', output level in db.
    """

    def __init__(self, src_pe, attack=0.9, release=0.1, units=None):
        # TODO: support attack and release times in seconds.  This will require
        # that frame_rate() is available from src_pe.
        self._src_pe = AbsPE(src_pe)
        self._attack = attack
        self._release = release
        self._units = units
        # state is one frame memory for a leaky integrator
        self._state = ut.const_frames(0.0, src_pe.channel_count(), 1)

    def render(self, requested:Extent):
        overlap = self._src_pe.extent().intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, self.channel_count(), requested.duration())

        src_frames = self._src_pe.render(requested)
        dst_frames = ut.uninitialized_frames(*src_frames.shape)
        for i in range(requested.duration()):
            x = src_frames[:,i:i+1]
            y = self.track(self._state, x)
            self._state = y
            dst_frames[:,i:i+1] = self._state
        if self._units == 'db':
            dst_frames = ut.ratio_to_db(dst_frames)
        return dst_frames

    def extent(self):
        return self._src_pe.extent()

    def channel_count(self):
        return self._src_pe.channel_count()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def track(self, state, sample):
        delta = np.max(sample - state)
        if delta > 0:
            return state + delta * self._attack
        else:
            return state + delta * self._release
