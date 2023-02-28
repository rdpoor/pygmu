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

src = pg.MixPE(
    pg.NoisePE(gain=0.5, frame_rate=FRAME_RATE).pan(-90),
    pg.NoisePE(gain=0.5, frame_rate=FRAME_RATE).pan(90))
flt = pg.BQ2BandPassPE(src, f0=330, q=20).gain(10)
pg.Transport(flt).play()
