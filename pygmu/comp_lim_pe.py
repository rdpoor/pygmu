import numpy as np
from scipy import signal
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class CompLimPE(PygPE):
    """
    Compressor / Limiter
    """

    SQUELCH_SLOPE = 10   # how fast input falls off below squelch_db

    def __init__(self,
                 src_pe,
                 env_pe,
                 ratio = 2.0,
                 limit_db = 0.0,
                 squelch_db = -50.0):
        """
        Compressor / Limiter

        src_pe: Sound source
        env_pe: output of envelope detector, 1.0 is nominal full-scale
        ratio: compression ratio when squelch_db <= env_pe <= limit_db
        limit_db: ouput is hard limited to stay below limit_db.
        squelch_db: When env_pe <= squelch_db, output is attenuated.

To understand the parameters (all values are in db):

output db:

      y1                                 +-------                                            
                                    .    |                                                   
                               .         |                                                   
                          .              |                                                   
                     .                   |                                                   
      y0        +                        |
               /|                        |
              / |                        |
             /  |                        |
                x0                       x1
                       input db
   
1. When input is >= x1 db, output is limit_db
2. When input is < x0 db, output falls off at SQUELCH_RATIO below x0.
3. Between x0 and x1, output rises at 1/ratio db per unit change in 
   input db.

If x >= x1, output_db(x) = y1 (limiting)
If x0 <= x < x1, output_db(x) = m * (x - x0) + y0 (compressing, m=1/ratio)
If x < x0, output_db(x) = SQUELCH_SLOPE * (x - x0) + y0 (squelching)

y – y1 = m(x – x1)

Note: y0 is not given directly.  Solving for y0:
y0 - y1 = m * (x0 - x1)
y0 = m * (x0 - x1) + y1
        """
        self._src_pe = src_pe
        self._env_pe = env_pe
        self._m = 1/ratio
        self._x1 = limit_db
        self._y1 = limit_db
        self._x0 = squelch_db
        self._y0 = self._m * (self._x0 - self._x1) + self._y1

    def render(self, requested:Extent):
        overlap = self._src_pe.extent().intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, self.channel_count(), requested.duration())
        
        src_frames = self._src_pe.render(requested)
        env_frames = self._env_pe.render(requested)
        db_frames = ut.ratio_to_db(env_frames)
        gain_frames = self.compute_gain(db_frames)
        dst_frames = src_frames * gain_frames
        return dst_frames

    def extent(self):
        return self._src_pe.extent()

    def channel_count(self):
        return self._src_pe.channel_count()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def compute_gain(self, input_db):
        out_db = self.output_db(input_db)
        gain_db = out_db - input_db
        # print("in=\n{}\nout=\n{}\ngain=\n{}\n".format(input_db, out_db, gain_db))
        return ut.db_to_ratio(gain_db)

    def output_db(self, x):
        """
        This function returns output_db as a function of input_db
        """
        # apply compression ratio over entire range
        y = self._m * (x - self._x0) + self._y0
        # apply hard limiting
        y[np.where(x > self._x1)] = self._x1
        # apply squelch
        squelched = np.where(x < self._x0)
        y[squelched] = self.SQUELCH_SLOPE * (x[squelched] - self._x0) + self._y0
        return y

    def ratio(self):
        return 1/self._m

    def limit_db(self):
        return self._x1

    def squelch_db(self):
        return self._x0
