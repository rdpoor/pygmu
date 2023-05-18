# This bit of boilerplate allows Python to find the pygmu library
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
def secs(s):
    return int(s * 48000)

# crop followed by warp_speed results in an infinite loop in which render is called for an extent of 0
Watts1 = pg.WavReaderPE("samples/spoken/Alan Watts Humanity Within the Universe.mp3").crop(pg.Extent(secs(124),secs(126))).time_shift(-secs(124))
test = Watts1.warp_speed(0.588)

Watts1.pygplay()
test.pygplay()

# mix = pg.WavWriterPE(Watts1, 'debug_warp.wav').warp_speed(0.588)
# pg.FtsTransport(mix).play()
# pg.Transport(pg.WavReaderPE('debug_warp.wav')).play()


