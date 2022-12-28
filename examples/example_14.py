import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

source = pg.WavReaderPE("samples/Sine440_Stereo.wav")
#source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav").env(100,42000)
speed = float(input('enter speed:'))
if speed <= 0:
    print('postive numbers are better')
timeline = pg.IdentityPE(channel_count=1).gain(speed)

warped = pg.TimewarpPE(source, timeline)

x = pg.WavWriterPE(warped, "example_14.wav")
pg.Transport(x).play()

