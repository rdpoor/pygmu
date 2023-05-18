import os
import sys
import time
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test PygPlayer


"""

src = pg.WavReaderPE("samples/music/TamperFrame_TooGoodToBeTrue_Edit.wav")
src2 = pg.WavReaderPE("samples/music/TamperFrame_TooGoodToBeTrue_Edit.wav")

src.pygplay('TooGoodToBeTrue')
flt = pg.BQ2BandPassPE(src, f0=330, q=20).gain(4)
flt.pygplay('flt')
src.pygplay('TooGoodToBeTrue')

