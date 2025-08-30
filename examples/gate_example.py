import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut


src = pg.WavReaderPE("samples/music/TamperFrame18.wav").stereo().normalize()


print("Creating test signal with varying amplitude...")


gated_signal = pg.GatePE(src, threshold_db=-20, attack=0.002, release=0.1)


print("Playing gated signal...")
pg.Transport(gated_signal).play()

print("Gate example complete!")
