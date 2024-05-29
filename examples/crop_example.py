import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("samples/music/SwanLakeOp-ActIIConcl.wav").stereo()
sr = src.frame_rate()

# cut the source down to the segment starting at 1.0 secs,for a duration of 3.0 seconds
# add a small 5000-sample ramp up and down, then pad the beginning with 3 seconds of silence and the ending with 2
cropped = src.crop(pg.Extent(1 * sr,4 * sr), 5000, 5000).pad(3 * sr, 2 * sr)

pg.Transport(cropped).play()

