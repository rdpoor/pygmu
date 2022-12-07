import numpy as np
from extent import Extent
from pyg_pe import PygPE

class LinearRampPE(PygPE):
    """
    Generate a ramp with start time, end time, start value and end value.
    """

    def __init__(self, start_v, end_v, extent:Extent, channel_count=PygPE.DEFAULT_CHANNEL_COUNT):
        super(LinearRampPE, self).__init__()
        self._start_v = start_v
        self._end_v = end_v
        self._extent = extent
        self._dvdt = (end_v - start_v) / (extent.end() - extent.start())
        self._channel_count = channel_count

    def render(self, requested:Extent):
        overlap = requested.intersect(self.extent())

        # of frames to generate before, during and after the ramp
        n_before = max(0, min(self.extent().start() - requested.start(), requested.duration()))
        n_during = overlap.duration()
        n_after = max(0, min(requested.end() - self.extent().end(), requested.duration()))

        # start with an empty array (a needless consistency...)
        dst_buf = np.ndarray([0, self.channel_count()], dtype=np.float32)

        # Fill n_before of the start value
        if (n_before > 0):
            dst_buf = np.concatenate(
                (dst_buf,
                np.full([n_before, self.channel_count()], self._start_v, dtype=np.float32)))

        # Fill n_during for the ramp itself.
        if n_during > 0:
            # generate a 1-D ramp from intersected start to intersected end
            ramp = np.linspace(
                self.lerp(overlap.start()),
                self.lerp(overlap.end()),
                num=n_during,
                endpoint=False,
                dtype=np.float32)

            # reshape into n_channel columns, append to dst_buf
            dst_buf = np.concatenate(
                (dst_buf,
                np.tile(ramp.reshape(-1, 1), (1, self.channel_count()))))

        # Fill n_after of the end value.
        if n_after > 0:
            dst_buf = np.concatenate(
                (dst_buf,
                np.full([n_after, self.channel_count()], self._end_v, dtype=np.float32)))

        return dst_buf

    def extent(self):
        return self._extent

    def channel_count(self):
        return self._channel_count

    def lerp(self, t):
        return self._start_v + self._dvdt * (t - self.extent().start())
