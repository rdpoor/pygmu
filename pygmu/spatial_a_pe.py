import numpy as np
from extent import Extent
from pyg_pe import PygPE
from mono_pe import MonoPE

"""
Stereo to mono frames and back again:

>>> a=ut.ramp_frames(0, 4, 4, 2)
array([[0., 0.],
       [1., 1.],
       [2., 2.],
       [3., 3.]], dtype=float32)
>>> b = np.dot(a, [[1], [1]])
array([[0.],
       [2.],
       [4.],
       [6.]])
>>> c = np.dot(b, [[0.5, 2.0]])
array([[ 0.,  0.],
       [ 1.,  4.],
       [ 2.,  8.],
       [ 3., 12.]])
"""

class SpatialAPE(PygPE):
    """
    Locate a sound source into a stereo sound field, version A.
    This version:
    * accepts mono or stereo (mixing to mono)
    * accepts fixed "theta": 0 = front, -pi = hard left, pi = hard right
    * accepts two fixed gain terms for left and right.  
    * renders a stereo output
    """

    SPEED_OF_SOUND_MPS = 343
    HEAD_RADIUS_M = 0.22


    def __init__(self, src_pe, theta:float=0, gain_l:float=1.0, gain_r:float=1.0):
        super(SpatialAPE, self).__init__()
        self._src_pe = src_pe
        self.setup_chains(theta, gain_l, gain_r)

    def render(self, requested:Extent):
        left_frames = self._left_chain.render(requested)
        right_frames = self._right_chain.render(requested)
        return np.hstack((left_frames, right_frames))

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return 2

    def intra_aural_delay_frames(self, theta):
        """
        Return the # of frames delay between left and right.
        With theta > 0 (sound originates to the right), the delay will be positive.
        """
        dly_s = (self.HEAD_RADIUS_M / self.SPEED_OF_SOUND_MPS) * np.sin(theta)
        dly_frames = dly_s * self.frame_rate()
        return dly_frames

    def setup_chains(self, theta, gain_l, gain_r):
        self._left_chain = MonoPE(self._src_pe)
        self._right_chain = MonoPE(self._src_pe)

        delay = self.intra_aural_delay_frames(theta)

        if delay > 0:
            self._left_chain = self._left_chain.delay(int(delay))
        elif delay < 0:
            self._right_chain = self._right_chain.delay(int(-delay))

        if gain_l != 1.0:
            self._left_chain = self._left_chain.gain(gain_l)

        if gain_r != 1.0:
            self._right_chain = self._right_chain.gain(gain_r)
