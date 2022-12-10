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

# gain_db is ignored for lowpass
pg.Transport(pg.BiquadPE(src, 0.0, 330.0, 40, "lowpass")).play()

# After the noise source stops, you can hear how long this resonates!
pg.Transport(pg.BiquadPE(src.gain(0.05), 60.0, 330.0, 10, "peak")).play()
