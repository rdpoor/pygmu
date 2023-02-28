import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test BiquadPE
"""

FRAME_RATE = 48000

src_l = pg.NoisePE(gain=0.5, frame_rate=FRAME_RATE).pan(-90)
src_r = pg.NoisePE(gain=0.5, frame_rate=FRAME_RATE).pan(90)
src = pg.MixPE(src_l, src_r)
flt = pg.BQ2BandPassPE(src, f0=330, q=400).gain(100)
pg.Transport(flt).play()
