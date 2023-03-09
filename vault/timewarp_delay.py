import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import numpy as np
import pygmu as pg
import soundfile as sf

def secs(s):
    return int(s * 48000)

def delays(src, secs, howmany = 1, decay = 1):
    frame_rate = 48000
    delay_units = []
    amp = 1
    for i in range(1, howmany):
        #delay_units.append(src.delay(int(i * secs * frame_rate)).gain(amp).pan(random.uniform(-90,90)))
        delay_units.append(src.delay(int(i * secs * frame_rate)).gain(amp))
        amp *= decay
    return pg.MixPE(src,*delay_units)

def mix_at(src, t, amp = 1):
    return pg.DelayPE(src,t).gain(amp)

#theory0 = pg.WavReaderPE("samples/TamperFrame_SwingTheory.wav")
theory0 = pg.WavReaderPE("samples/TamperFrame_SwingTheory.wav").crop(pg.Extent(secs(0),secs(2.2))).gain(0.5)

theory0.play()


# NOTE --investigate the weirdness of using warp_speed in this way -- seems to interact with the delay offset strangely
mosh2 = theory0.warp_speed(0.71)
#mosh2 = pg.WarpSpeedPE(theory0, 0.71).delay(secs(5))
mosh2.play()

mosh2.delay(secs(5))
mosh2.play()

#mosh2 = theory0.gain(1.2)
#
elements2 = [theory0]
elements2.append(mix_at(mosh2,secs(5),0.8))



jimmy = pg.MixPE(*elements2)
jimmy.play()
