import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import numpy as np
import pygmu as pg
import soundfile as sf
import utils as ut

clip = pg.WavReaderPE("samples/TamperClip93.wav")
filtered = pg.FilterPE(clip, 3, 400)
filtered.play()
