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
        #delay_units.append(src.time_shift(int(i * secs * frame_rate)).gain(amp).pan(random.uniform(-90,90)))
        delay_units.append(src.time_shift(int(i * secs * frame_rate)).gain(amp))
        amp *= decay
    return pg.MixPE(src,*delay_units)

def mix_at(src, t, amp = 1):
    return pg.TimeShiftPE(src,t).gain(amp)

reverb_path = 'samples/IR/Conic Long Echo Hall.wav'

impulse = pg.WavReaderPE(reverb_path)




Watts1 = pg.WavReaderPE("samples/Alan Watts Humanity Within the Universe.mp3").crop(pg.Extent(secs(124),secs(337))).time_shift(int(-secs(124)))
Watts1Rev = Watts1.reverse(25)


Watts1_HP = pg.BQ2HighPassPE(Watts1, f0=110, q=8).gain(0.8)

Gleason1 = pg.WavReaderPE("samples/PrettyGirl_Gleason.wav").crop(pg.Extent(secs(0.75),secs(92)))

env = pg.EnvDetectPE(Gleason1, attack=0.9, release=0.0001)
Gleason1Compressed = pg.CompressorPE(Gleason1, env, ratio=3.0, threshold_db=-20, makeup_db=2)



Gleason1Slow = pg.WarpSpeedPE(Gleason1Compressed, 0.4)
Gleason1Slow_HP = pg.BQ2HighPassPE(Gleason1Slow, f0=212, q=4).gain(0.8)
Gleason1Rev = Gleason1Slow_HP.reverse(33)

convolved = pg.ConvolvePE(Gleason1Slow_HP.gain(0.08), impulse)
#convolved2 = pg.ConvolvePE(Gleason1Rev.gain(0.08), impulse)

#Gleason1Rev.pygplay('convolved2')

elements = []

t = 0
#elements.append(mix_at(convolved,secs(t),gain).pan(0))


gain = 0.53
elements.append(mix_at(convolved,secs(t),gain))

t += 8
gain = 0.8
elements.append(mix_at(Watts1_HP,secs(t),gain))


mosh = pg.MixPE(*elements)

mosh.pygplay('Watts')




