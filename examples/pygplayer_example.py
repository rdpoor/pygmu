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

src = pg.WavReaderPE("samples/TamperFrame_TooGoodToBeTrue_Edit.wav")

src.pygplay()

filtered = pg.FilterPE(src, 3, 500)

filtered.pygplay('filtered', False)
