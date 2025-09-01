import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut
from trim_pe import TrimPE

# Load a source file - using the same as crop_example
src = pg.WavReaderPE("samples/music/SwanLakeOp-ActIIConcl.wav").stereo()

# Create a padded version with silence at start and end to demonstrate trimming
padded_src = src.pad(front_pad_frames=int(2.0 * src.frame_rate()), 
                    rear_pad_frames=int(1.5 * src.frame_rate()))

print("Original extent:", src.extent())
print("Padded extent:", padded_src.extent())

# Trim silence from beginning and end with different thresholds
trimmed_loose = TrimPE(padded_src, threshold=0.001, attack=0.9, release=0.1)
trimmed_tight = TrimPE(padded_src, threshold=0.01, attack=0.9, release=0.1)

print("Trimmed (loose) extent:", trimmed_loose.extent())
print("Trimmed (tight) extent:", trimmed_tight.extent())

# Play the trimmed version
pg.Transport(trimmed_loose).play()