import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("samples/SwanLakeOp-ActIIConcl.wav").mono() # .crop(pg.Extent(3635000, 3700000))
src = pg.WavWriterPE(src, "swan.wav")
env = pg.EnvDetectPE(src, attack=0.9, release=0.0001)
env = pg.WavWriterPE(env, "env.wav")
compressed = pg.CompLimPE(src, env, ratio=20.0, limit_db=-40, squelch_db=-200)
compressed = compressed.gain(ut.db_to_ratio(35))
compressed = pg.WavWriterPE(compressed, "comp.wav")
pg.FtsTransport(compressed).play()
