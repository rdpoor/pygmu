import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("samples/music/TamperFrame19.wav")
sr = src.frame_rate()

seg = src.crop(pg.Extent(0,1*sr),6000,6000).gain(0.5)

delayed = seg.delays(0.5, 3, 0.5)

delayed2 = delayed.delays(0.5, 8, 0.5)

pg.Transport(delayed2).play()




