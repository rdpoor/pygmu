import numpy as np
from scipy import signal
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class CompressorPE(PygPE):
    """
    Compressor / Limiter
    """

    SQUELCH_SLOPE = 10   # how fast input falls off below squelch_db

    def __init__(self,
                 src_pe,
                 env_pe,
                 threshold_db = 0.0,
                 ratio = 2.0,
                 post_gain_db = None):
        """
        Compressor / Limiter

        src_pe: Sound source
        env_pe: output of envelope detector, 1.0 is nominal full-scale
        threshold_db: level above which compression takes effect
        ratio: compression ratio when input_db > thresh_db
        post_gain_db: gain applied after compression.  If not
          specified, defaults to threshold_db. 

                                               .
                   ratio = N:1           .
                                   .
                             .
                       +
    radio = 1:1      . |
                   .   |
                 .     |
               .       |
                   thresh_db

    Output level vs input level
   
1. When input_db is <= thresh_db, output_db = input_db 
2. Else output_db = thresh_db + (input_db - thresh_db) / ratio

        """
        self._src_pe = src_pe
        self._env_pe = env_pe
        self._threshold_db = threshold_db
        self._m = 1/ratio
        self._post_gain_db = post_gain_db
        if post_gain_db is None:
            self._post_gain_db = -threshold_db

    def render(self, requested:Extent):
        overlap = self._src_pe.extent().intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, requested.duration(), self.channel_count())
        
        src = self._src_pe.render(requested)
        db_env = ut.ratio_to_db(self._env_pe.render(requested))
        gain_env = self.compute_gain(db_env)
        dst = src * gain_env
        # print("==== render:")
        # print("gain_env=", gain_env.shape, gain_env)
        # print("src=", src.shape, src)
        # print("dst=", dst.shape, dst)
        return dst

    def extent(self):
        return self._src_pe.extent()

    def channel_count(self):
        return self._src_pe.channel_count()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def theshold_db(self):
        return self._threshold_db

    def ratio(self):
        return 1/self._m

    def post_gain_db(self):
        return self._post_gain_db

    def compute_gain(self, db_env):
        # assume no compression
        out_db = db_env.copy()
        # apply compression where db_env > threshold
        compressed = np.where(db_env > self._threshold_db)
        out_db[compressed] = self._m * (db_env[compressed] - self._threshold_db) + self._threshold_db
        # gain = output / input (but we're still in db...)
        gain_db = (out_db - db_env) + self._post_gain_db
        return ut.db_to_ratio(gain_db)
