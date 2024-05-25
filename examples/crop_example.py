import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("samples/music/SwanLakeOp-ActIIConcl.wav").stereo() # .crop(pg.Extent(3635000, 3700000))


cropped = src.crop(pg.Extent(0,48000 * 2), 5020, 5020).pad(3 * 48000, 2 * 58000)

pg.Transport(cropped).play()

