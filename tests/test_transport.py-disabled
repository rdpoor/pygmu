import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import random
import utils as ut

sourceA= pg.WavReaderPE("samples/ItsGonnaRain_Original.wav")
monoSource= pg.WavReaderPE("samples/Sine_C4.wav")

ret = pg.Transport(monoSource).play()
ret = pg.Transport(monoSource).play(True) # should auto continue
ret = pg.Transport(monoSource).term_play()
ret = pg.Transport(sourceA).play()
ret = pg.Transport(sourceA).play(True) # should continue
ret = pg.Transport(sourceA).play(True, 0) #should hang
ret = pg.Transport(sourceA).term_play(True) #should continue
ret = pg.Transport(sourceA).term_play(True, 0) #should hang

filename = "tests/test_transport.wav"
dst = pg.WavWriterPE(sourceA, filename)
pg.FtsTransport(dst).play()
pg.Transport(pg.WavReaderPE(filename)).play()
pg.Transport(pg.WavReaderPE(filename)).play(True)

