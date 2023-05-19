import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("samples/music/TamperFrame19.wav") # .mono()

delayed = src.delays(0.5, 3, 0.5)
delayed.pygplay()

delayed2 = src.delays(0.5, 3, 0.5).reverb(0.65)
delayed2.pygplay()



