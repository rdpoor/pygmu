import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("samples/multisamples/Violin_Undul_C3_RM.wav") # .mono()
lower = src.interpolate(0.5)
pg.Transport(lower).play()


