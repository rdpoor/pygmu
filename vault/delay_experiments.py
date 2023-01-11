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
source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav").gain(3)
warped = pg.DelayPE(source, pg.SinPE(frequency=82, amplitude=100.0, frame_rate=FRAME_RATE))
# DelayPE with a time-varying delay has infinite extent.  Crop it to the length of the original
warped = warped.crop(source.extent())

warped.play()

warped2 = pg.DelayPE(source, pg.SinPE(frequency=4306, amplitude=114.0, frame_rate=FRAME_RATE))
warped2 = warped2.crop(source.extent())

warped3 = pg.DelayPE(source, pg.SinPE(frequency=2612, amplitude=14.0, frame_rate=FRAME_RATE))
warped3 = warped3.crop(source.extent())


pg.Transport(pg.MixPE(warped2, warped3)).play()
