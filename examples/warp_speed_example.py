import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test WarpSpeedPE
"""

print("hit return after each example to hear the next")

# plain warping
print("normal speed from start of file")
source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
warped = pg.WarpSpeedPE(source, 1.0)  # normal speed
pg.Transport(warped).play()

# sdrawkcab
print("reverse from end of file")
source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
# Note use of frame= argument to start ad the end of the sound file
warped = pg.WarpSpeedPE(source, -1.0, frame=source.extent().end())
pg.Transport(warped).play()

print("detuned and mixed with original")
source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
warped = pg.WarpSpeedPE(source, 1.02)  # a bit fast
pg.Transport(pg.MixPE(source, warped)).play()

print("just for fun: forwards and backwards mixed at half speed")
source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
warped1 = pg.WarpSpeedPE(source, 0.5)
warped2 = pg.WarpSpeedPE(source, -0.5, frame=source.extent().end())
pg.Transport(pg.MixPE(warped1, warped2)).play()

