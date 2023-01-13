import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut
import pyg_exceptions as pyx

class TimewarpPE(PygPE):
    """
    Remap time.
    """


    def __init__(self, src_pe, timeline):
        super(TimewarpPE).__init__()
        if timeline.channel_count() != 1:
            raise pyx.ChannelCountMismatch("timeline input must be single channel")
        self._src_pe = src_pe
        self._timeline = timeline

    def render(self, requested):
        times = self._timeline.render(requested).reshape(-1)  # a 1-D array
        t0 = int(np.floor(min(times)))
        t1 = int(np.floor(max(times))) + 1

        # please explain why we need t1+1 since it's already incremented
        extent = Extent(t0, t1+1)
        if extent.is_empty():
            return ut.const_frames(0.0, self.channel_count(), requested.duration())

        # fetch src_pe's frames between t0 and t1
        src_frames = self._src_pe.render(Extent(t0, t1+1))
        dst_channels = []

        for channel in src_frames:
            delayed_channel = np.interp(times, np.arange(t0, t1+1), channel)
            dst_channels.append(delayed_channel)
        dst_frames = np.hstack(dst_channels)
        d1 = dst_frames.shape
        # please explain why we need to reshape after hstack
        dst_frames = dst_frames.reshape(self.channel_count(), -1)
        d2 = dst_frames.shape
        return dst_frames

    def extent(self):
        """Assume that timeline defines the extent"""
        return self._timeline.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
