import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class GainDbPE(PygPE):
    """
    Apply gain, expressed in decibels, to a pe.  gain_db can be constant or a 
    processing element.
    """

    def __init__(self, src_pe, gain_db):
        super(GainDbPE, self).__init__()
        self._src_pe = src_pe
        self._gain_db = gain_db

    def render(self, requested:Extent):
        if isinstance(self._gain_db, PygPE):
            # gain_db is the output of a PE.  Render the db values, convert to
            # ratiometric values and use them to scale src frames.
            overlap = requested.intersect(self.extent())
            dst_buf = ut.const_frames(0.0, self.channel_count(), requested.duration())
            if overlap.is_empty():
                # no overlap - dst_buf is already zero
                pass
            else:
                # nonzero overlap - render src and scale by gain, then overwrite
                # scaled frames in dst_buf
                n = overlap.duration()
                gain = ut.db_to_ratio(self._gain_db.render(overlap))
                src_buf = self._src_pe.render(overlap) * gain
                dst_idx = overlap.start() - requested.start()
                # dst_idx is the index into dst_buf where src_buf[0] gets written
                dst_buf[:, dst_idx:dst_idx+n] = src_buf
        else:
            # gain is constant.
            gain = ut.db_to_ratio(self._gain_db)
            dst_buf = self._src_pe.render(requested) * gain
        return dst_buf

    def extent(self):
        if isinstance(self._gain_db, PygPE):
            return self._src_pe.extent().intersect(self._gain_db.extent())
        else:
            return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
