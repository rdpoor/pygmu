import numpy as np
from extent import Extent
from pyg_pe import PygPE
from mono_pe import MonoPE
import pyg_exceptions as pyx
import utils as ut

"""
Notes:
https://www.martinjaroszewicz.com/book/spatial_audio.html
https://jeffvautin.com/2015/03/computing-panning-curves/
"""

class SpatialPE(PygPE):
    """
    Locate a sound source into a stereo sound field, version A.
    This version:
    * accepts mono or stereo (mixing to mono)
    * accepts fixed "theta": 0 = front, -pi = hard left, pi = hard right
    * renders a stereo output
    """

    SPEED_OF_SOUND_MPS = 343
    HEAD_RADIUS_M = 0.22


    def __init__(self, src_pe, degree=0, theta=None, curve='cosine', frame_rate=None):
        """
        Create a panner.  
        src_pe: the source frames
        degree: -90 = hard left, 0 = center, 90 = hard right
        theta: if given, overrides degree: -pi/2 = hard left, 0=center, pi/2=hard right
        curve: one of the following:  As theta goes from hard left to hard right:
          'none' - no amplitude scaling -- time delay only
          'linear' - left amplitude ramps linearly 1.0 to 0.0, right from 0.0 to 1.0, 0.5 at center
          'cosine' - left ramps by cosine from 1.0 to 0.0, right ramps by sin, 0.7 at center
        """
        super(SpatialPE, self).__init__()
        self._src_pe = src_pe
        self.set_frame_rate(frame_rate, src_pe)

        if theta is None:
            theta = np.pi * degree / 180.0
        self.setup_chains(theta, curve)

    def render(self, requested:Extent):
        overlap = self._src_pe.extent().intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, 2, requested.duration())

        left_frames = self._left_chain.render(requested)
        right_frames = self._right_chain.render(requested)
        dst_frames = np.vstack((left_frames, right_frames))
        return dst_frames

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

    def setup_chains(self, theta, curve):
        self._left_chain = MonoPE(self._src_pe)
        self._right_chain = MonoPE(self._src_pe)

        delay = self.intra_aural_delay_frames(theta)

        if delay > 0:
            self._left_chain = self._left_chain.time_shift(int(delay))
        elif delay < 0:
            self._right_chain = self._right_chain.time_shift(int(-delay))

        if curve == 'linear':
            # norm_angle goes from 0.0 to 1.0 as theta goes from hard left to hard right 
            norm_angle = ut.lerp(theta, -np.pi/2, np.pi/2, 0, 1)
            self._left_chain = self._left_chain.gain(1-norm_angle)
            self._right_chain = self._right_chain.gain(norm_angle)
        elif curve == 'cosine':
            # omega goes from 0 to pi/2 as theta goes from hard left to hard right
            omega = (theta + np.pi/2)/2
            self._left_chain = self._left_chain.gain(np.cos(omega))
            self._right_chain = self._right_chain.gain(np.sin(omega))
        else:
            # gain is unchanged
            pass

    def set_frame_rate(self, frame_rate, src_pe):
        """
        Enforce setting of frame_rate, either from keyword arg or from source_pe.
        If both are specified, print a warning on mismatch but honor keyword arg.
        """
        self._frame_rate = frame_rate or src_pe.frame_rate()
        if self._frame_rate is not None:
            if src_pe.frame_rate()  is not None and src_pe.frame_rate() != self._frame_rate:
                print("SpatialPE warning: overriding input frame_rate of {} with {}".format(
                    src_pe.frame_rate(), frame_rate))
        else:
            if src_pe.frame_rate() is None:
                # neither specifies frame rate -- cannot proceed
                raise pyx.FrameRateMismatch("frame rate must be specified")
