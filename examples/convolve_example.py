import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

filename = "examples/convolve_example.wav"

src = pg.WavReaderPE("samples/F9_TH_Live_Hat_60bpm_B.wav")
# impulse = pg.WavReaderPE("samples/IR/480_Fat Plate.wav")
impulse = pg.WavReaderPE("samples/IR/Five Columns.wav")
# impulse = pg.WavReaderPE("samples/IR/Bottle Hall.wav")
convolved = pg.ConvolvePE(src, impulse)
convolved = pg.WavWriterPE(convolved, filename)
pg.FtsTransport(convolved).play()

pg.Transport(pg.WavReaderPE(filename)).play()

