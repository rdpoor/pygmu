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

src = pg.NoisePE(gain=0.5, frame_rate=FRAME_RATE)

# constant f0, constant Q
# flt = pg.BQLowPassPE(src, f0=330, q=40).crop(pg.Extent(0, 5*FRAME_RATE))
# dst = pg.WavWriterPE(flt, "test.wav")
# pg.FtsTransport(dst).play()
# pg.Transport(pg.WavReaderPE("test.wav")).play()
flt = pg.BQBandPassPE(src, f0=330, q=400).gain(100)
pg.Transport(flt).play()