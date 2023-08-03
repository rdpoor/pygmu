import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test ReversePE
"""

source = pg.WavReaderPE("samples/music/Tamper_MagnifyingFrame1.wav")
reversed = pg.ReversePE(source)
reversed.pygplay()
