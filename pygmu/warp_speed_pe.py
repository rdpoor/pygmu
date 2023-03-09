import math
import numpy as np
import numbers
from extent import Extent
from pyg_pe import PygPE
import utils as ut
import pyg_exceptions as pyx

class WarpSpeedPE(PygPE):
    """
    Variable rate / resampling using linear interpolation.
    """

    def __init__(self, src_pe, speed=1.0):
        super(WarpSpeedPE).__init__()

        self._src_pe = src_pe
        self._speed = speed
        try:
            # python-esque technique to check for numeric speed.
            # "ask forgiveness, not permission"
            self._speed = speed * 1.0
        except TypeError:
            raise pyx.ArgumentError("WarpSpeed rate argument must be a number")

    def get_src_frame(self):
        """
        Return the last rendered frame number.  This is useful if you want to
        change the speed and not introduce a discontinuity.
        """
        return self._src_frame

    def set_speed(self, speed):
        self._speed = speed

    def get_speed(self):
        return self._speed

    def render(self, requested):
        if isinstance(self._speed, numbers.Number):
            # constant speed.
            t0 = requested.start() * self._speed
            t1 = requested.end() * self._speed
            src_t0 = t0
            src_t1 = t1
            if src_t1 < src_t0:
                # enforce src_t0 <= src_t1
                src_t1, src_t0 = src_t0, src_t1
            # src_t0 and src_t1 define the extent of the source frames we need
            # to request from the source.  Since src_t1 is exclusive, we add 1.
            src_t0 = int(math.floor(src_t0))
            src_t1 = int(math.floor(src_t1)) + 1

            src_extent = Extent(src_t0, src_t1)
            src_frames = self._src_pe.render(src_extent)

            # xp[n] is the frame number of src_frames[n]
            xp = np.arange(src_extent.start(), src_extent.end())

            # times defines the frame #s at which to evaluate src_frames.
            # Note times are generally non-integer.
            times = np.linspace(
                t0,              # inclusive
                t1,              # exclusive
                num=int(requested.duration()),
                endpoint=False,
                dtype=np.float32)
            dst_channels = []
            for fp in src_frames:
                # use np.interp() to compute samples at the given times
                # print("t0, t1, src_t0, src_t1: ", t0, t1, src_t0, src_t1)
                # print("times:", times)
                # print("xp:", xp)
                # print("fp:", fp)
                samples = np.interp(times, xp, fp)
                # print("y:", samples)
                dst_channels.append(samples)
            dst_frames = np.vstack(dst_channels)

            self._src_frame = t1  # update frame for get_src_frame()
            return dst_frames

        else:
            raise(RuntimeError("dynamic speeds not yet supported"))

    def extent(self):
        if self._speed == 0:
            # infinitely long...
            return Extent()
        try:
            t0 = self._src_pe.extent().start() / self._speed
            t1 = self._src_pe.extent().end() / self._speed
            # print("t0, t1 =", t0, t1)
            if t1 > t0:
                return Extent(t0, t1)
            else:
                return Extent(t1, t0)
        except TypeError:
            raise(RuntimeError("dynamic speeds not yet supported"))

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
