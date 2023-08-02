import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
import pyg_exceptions as pyx
import pygmu as pg
from pygmu import (PygPE, WavReaderPE)

pluck = pg.WavReaderPE('./samples/music/044-n-2723_stero.wav')
stretched = pluck.tralfam()
dur = stretched.extent().duration()
looped = stretched.loop(dur).crop(pg.Extent(0, 10*dur))
looped2 = stretched.loop(dur).time_shift(dur/2).crop(pg.Extent(0, 10*dur))
mix = pg.MixPE(looped, looped2)
# pg.Transport(pg.TralfamPE(looped)).play()
mix.pygplay('nooootttteeee')
