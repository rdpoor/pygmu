import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

def secs(s):
    return int(s * 48000)

def delays(src, secs, howmany = 1, decay = 1):
    frame_rate = 48000
    delay_units = []
    amp = 1
    for i in range(1, howmany):
        delay_units.append(src.delay(int(i * secs * frame_rate)).gain(amp))
        amp *= decay
    return pg.MixPE(src,*delay_units)

def mix_at(src, t, amp = 1):
    return pg.DelayPE(src,t).gain(amp)

dur = 145

sourceA= pg.WavReaderPE("samples/ItsGonnaRain_Original.wav")
gravy = pg.GravyPE(sourceA,secs(2.95),secs(.17),secs(0.005),False).crop(pg.Extent(start=0,end=secs(dur)))
gravy2 = pg.GravyPE(sourceA,secs(2.95),secs(.22),secs(0.0078),False).crop(pg.Extent(start=0,end=secs(dur)))
gravy3 = pg.GravyPE(sourceA,secs(2.95),secs(.41),secs(0.08),False).crop(pg.Extent(start=0,end=secs(dur)))
gravy4 = pg.GravyPE(sourceA,secs(0.95),secs(.05),secs(0.008),False).crop(pg.Extent(start=0,end=secs(dur)))
frag1a = delays(gravy, 0.36,15,0.8)
frag2a = delays(gravy3, 0.39,6,0.98)


elements = []

gain = 1.85

t = 0
elements.append(mix_at(frag1a,secs(t),gain * 0.25))
elements.append(mix_at(frag2a,secs(t),gain * 0.25))
elements.append(mix_at(gravy2,secs(t),gain * 0.25))
elements.append(mix_at(gravy2,secs(t),gain * 0.25))
elements.append(mix_at(gravy4,secs(t),gain * 0.25))

mosh =  pg.LimiterPE(pg.MixPE(*elements))

moshr =  pg.LimiterPE(pg.MixPE(*elements)).reverse(147)

all = pg.MixPE(mosh,moshr)

pg.Transport(all).play()

