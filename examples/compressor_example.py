import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("samples/SwanLakeOp-ActIIConcl.wav")
env = pg.EnvDetectPE(src, attack=0.9, release=0.0001)
compressed = pg.CompressorPE(src, env, ratio=3.0, threshold_db=-20, makeup_db=10)
pg.Transport(compressed).play()
