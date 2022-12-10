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

print("hit return after each example to hear the next")

src = pg.NoisePE(gain=1.0, channel_count=1).crop(pg.Extent(0,5*44100))
pg.Transport(pg.BiquadPE(src, 440.0, 0.999, "resonator")).play()

