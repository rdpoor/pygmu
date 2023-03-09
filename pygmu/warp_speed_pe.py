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

    def __init__(self, src_pe, speed, frame=0):
        super(WarpSpeedPE).__init__()

        self._src_pe = src_pe
        self._speed = speed
        if isinstance(self._speed, PygPE) and self._speed.channel_count() != 1:
            raise pyx.ChannelCountMismatch("dynamic rate must be single channel")
        self._frame = frame

    def set_frame(self, frame):
        self._frame = frame

    def get_frame(self):
        return self._frame

    def set_speed(self, speed):
        self._speed = speed

    def get_speed(self):
        return self._speed

    def render(self, requested):
        if isinstance(self._speed, numbers.Number):
            # constant speed
            t0 = self._frame
            t1 = t0 + requested.duration() * self._speed
            src_t0 = int(round(t0))
            src_t1 = int(round(t1))
            if src_t1 < src_t0:
                # need to fetch frames in positive time order: swap
                src_t1, src_t0 = src_t0, src_t1
            # extra sample at each end for interpolation.  Note: t1 is
            # exclusive bounds, so +2 rather than +1
            src_t0 -= 1
            src_t1 += 2

            # src_t0 and src_t1 define the extent of the source frames we need
            extent = Extent(src_t0, src_t1)
            src_frames = self._src_pe.render(Extent(src_t0, src_t1))

            # xp[n] is the frame number of src_frames[n]
            xp = np.arange(extent.start(), extent.end())

            # times defines the frame #s at which to evaluate src_frames
            times = np.linspace(
                t0,
                t1,
                num=int(requested.duration()),
                endpoint=False,
                dtype=np.float32)
            dst_channels = []
            for fp in src_frames:
                # print(t0, t1, src_t0, src_t1)
                # print("times:", times)
                # print("xp:", xp)
                # print("fp:", fp)
                samples = np.interp(times, xp, fp)
                # print("y:", samples)
                dst_channels.append(samples)
            dst_frames = np.vstack(dst_channels)

            self._frame = t1  # update frame for next call to render()
            return dst_frames

        else:
            raise(RuntimeError("dynamic speeds not yet supported"))

    def extent(self):
        if isinstance(self._speed, numbers.Number):
            t0 = self._src_pe.extent().start()
            t1 = t0 + self._src_pe.extent().duration() / self._speed
            return Extent(t0, t1)
        else:
            raise(RuntimeError("dynamic speeds not yet supported"))

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
