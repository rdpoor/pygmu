import numpy as np
from extent import Extent
from pyg_gen import PygGen

class LinearRampPE(PygGen):
    """
    Generate a ramp with start time, end time, start value and end value.
    """

    def __init__(self, start_v, end_v, extent:Extent, frame_rate=None):
        super(LinearRampPE, self).__init__(frame_rate=frame_rate)
        self._start_v = start_v
        self._end_v = end_v
        self._extent = extent
        self._dvdt = (end_v - start_v) / (extent.end() - extent.start())

    def render(self, requested:Extent):
        overlap = requested.intersect(self.extent())
        if overlap.is_empty():
            return np.zeros(requested.duration(), dtype=np.float32).reshape(1, -1)

        # of frames to generate before, during and after the ramp
        # n_before = max(0, min(self.extent().start() - requested.start(), requested.duration()))
        # n_during = overlap.duration()
        # n_after = max(0, min(requested.end() - self.extent().end(), requested.duration()))
        n_before = max(0, self._extent.start() - requested.start())
        n_after = max(0, requested.end() - self._extent.end())
        n_during = requested.duration() - (n_before + n_after)

        # start with an empty array (a needless consistency...)
        dst_buf = np.ndarray(0, dtype=np.float32)

        # Fill n_before of the start value
        if n_before > 0:
            dst_buf = np.append(dst_buf, np.full(n_before, self._start_v))

        # Fill n_during for the ramp itself.
        if n_during > 0:
            # generate a 1-D ramp from intersected start to intersected end
            ramp = np.linspace(
                self.lerp(overlap.start()),
                self.lerp(overlap.end()),
                num=n_during,
                endpoint=False,
                dtype=np.float32)
            dst_buf = np.append(dst_buf, ramp)

        # Fill n_after of the end value.
        if n_after > 0:
            dst_buf = np.append(dst_buf, np.full(n_after, self._end_v))

        dst_buf.shape = (1, -1)  # reshape into 2D array with one row
        return dst_buf

    def extent(self):
        return self._extent

    def channel_count(self):
        return 1

    def lerp(self, t):
        return self._start_v + self._dvdt * (t - self.extent().start())
