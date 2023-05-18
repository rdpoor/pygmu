import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

def loopWindow(src,insk,dur):
    return pg.LoopPE(src.crop(pg.Extent(insk)).time_shift(-insk), dur)

def secs(s):
    return int(s * 48000)

sourceA= pg.WavReaderPE("samples/spoken/ItsGonnaRain_Original.wav")

loopB = loopWindow(sourceA,secs(2.95),secs(.8))

pg.Transport(loopB.crop(pg.Extent(start=0,end=secs(30)))).play()
