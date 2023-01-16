import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test MapPE
"""

makeup = 20

def user_fn(frames):
	return np.sin(frames * makeup * np.pi / 2.0) / makeup

source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
warped = pg.MapPE(source, user_fn)
pg.Transport(warped).play()
