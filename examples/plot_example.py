import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

"""
Test plot utility
"""

source = pg.WavReaderPE("samples/music/TamperFrame_SugarPlumFaries.wav").crop(pg.Extent(ut.stof(4), ut.stof(16)), 500)

#ut.plot_pes(source, plot_types=["raw", "spectrogram", "waterfall", "peak"])
ut.plot_pes(source, plot_types=["waterfall"], height=1000)


