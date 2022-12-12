import os
import sys
import numpy as np
from scipy import signal

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

orig_beat = pg.WavReaderPE("samples/BigBeat120bpm10.wav")
print("frame_rate = ", orig_beat.frame_rate())

comb = pg.CombPE(orig_beat, f0=440, q=5, filter_type='peak')
pg.Transport(comb).play()

comb = pg.CombPE(orig_beat, f0=440, q=5, filter_type='peak', pass_zero=True)
pg.Transport(comb).play()

comb = pg.CombPE(orig_beat, f0=440, q=20, filter_type='peak')
pg.Transport(comb).play()

comb = pg.CombPE(orig_beat, f0=440, q=20, filter_type='peak', pass_zero=True)
pg.Transport(comb).play()

comb = pg.CombPE(orig_beat, f0=440, q=200, filter_type='peak')
pg.Transport(comb).play()

comb = pg.CombPE(orig_beat, f0=440, q=200, filter_type='peak', pass_zero=True)
pg.Transport(comb).play()
