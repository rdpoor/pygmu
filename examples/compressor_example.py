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
compressed = pg.CompressorPE(src, env, ratio=3.0, threshold_db=-20, post_gain_db=10)
compressed = pg.WavWriterPE(compressed, "comp_03.wav")
pg.FtsTransport(compressed).play()
 
