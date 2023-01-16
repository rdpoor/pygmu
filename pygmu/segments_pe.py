import numpy as np
from extent import Extent
from pyg_pe import PygPE
from pyg_gen import PygGen
import pyg_exceptions as pyx
import utils as ut

class SegmentsPE(PygGen):
    """
    Given a sequence of time-value segments, render value vN at time tN.
    The time-value segments are specifies as: 
       [[t0, v0], [t1, v1], ... [tn-1, vn-1]].  
    Times before t0 will render as v0, times after tN-1 than tn-1 will render as
    vN-1.  With interpolation = 'step', values will step from v0, v1, ... vN-1.
    WIth interpolation = 'ramp', values will ramp between v0, v1, ... vN-1.'
    """

    RAMP = 'ramp'
    STEP = 'step'

    def __init__(self, time_value_pairs, interpolation='ramp', frame_rate=None):
        super(SegmentsPE, self).__init__(frame_rate=frame_rate)
        if len(time_value_pairs) < 2:
            raise pyx.ArgumentError("Must have at least two time/value pairs")
        self._times = np.array([])
        self._values = np.array([])
        for t, v in time_value_pairs:
            self.add_time_value(t, v)
        self._interpolation = interpolation

    def render(self, requested:Extent):

        if requested.end() <= self._times[0]:
            # common case #1: request ends before sequence starts, return v[0]
            return ut.const_frames(self._values[0], 1, requested.duration())

        if requested.start() >= self._times[-1]:
            # common case #2: request starts after sequence ends: return v[n-1]
            return ut.const_frames(self._values[-1], 1, requested.duration())

        dst_buf = np.ndarray(requested.duration(), dtype=np.float32)
        t = requested.start()

        if self._interpolation == 'step':
            for dst_idx in range(ut.frame_count(dst_buf)):
                seq_idx = np.searchsorted(self._times, t, side='right')
                if seq_idx >= len(self._times):
                    dst_buf[dst_idx] = self._values[-1]
                elif seq_idx == 0:
                    dst_buf[dst_idx] = self._values[0]
                else:
                    dst_buf[dst_idx] = self._values[seq_idx-1]
                t += 1
        else:  # interpolation == 'ramp'
            for dst_idx in range(ut.frame_count(dst_buf)):
                seq_idx = np.searchsorted(self._times, t)
                if seq_idx >= len(self._times):
                    dst_buf[dst_idx] = self._values[-1]
                elif seq_idx == 0:
                    dst_buf[dst_idx] = self._values[0]
                else:
                    t0 = self._times[seq_idx - 1]
                    t1 = self._times[seq_idx]
                    v0 = self._values[seq_idx -1]
                    v1 = self._values[seq_idx]
                    dst_buf[dst_idx] = ut.lerp(t, t0, t1, v0, v1)
                t += 1
        # Convert 1D dst_buf to monophonic (2D with 1 row)
        return ut.normalize_frames(dst_buf)

    def channel_count(self):
        return 1

    def add_time_value(self, time, value):
        idx = np.searchsorted(self._times, time)
        if idx < len(self._times) and self._times[idx] == time:
            # already has a time / value pair at this time: update
            self._values[idx] = value
        else:
            # insert time / value pair
            self._times = np.insert(self._times, idx, time)
            self._values = np.insert(self._values, idx, value)
