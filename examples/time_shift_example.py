import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test TimewarpPE
"""

FRAME_RATE = 48000

# mixing original with time-varying delay == flanging
source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
warped = pg.TimeShiftPE(source, pg.SinPE(frequency=1, amplitude=100.0, frame_rate=FRAME_RATE))
# TimeShiftPE with a time-varying delay has infinite extent.  Crop it to the length of the original
warped = warped.crop(source.extent())

pg.Transport(pg.MixPE(source, warped)).play()
