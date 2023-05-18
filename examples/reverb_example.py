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

limited = src.reverb(0.78, 'IR_HotHall.wav')
limited.pygplay()

limited2 = src.reverb(0.78, 'St Nicolaes Church.wav')
limited2.pygplay()




