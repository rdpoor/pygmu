import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

def secs(s):
    return int(s * 48000)

def mix_at(src, t, amp = 1):
    return pg.DelayPE(src,t).mulconst(amp)

def delays(src, secs, howmany = 1, decay = 1):
    frame_rate = 48000
    delay_units = []
    amp = 1
    for i in range(1, howmany):
        delay_units.append(src.delay(int(i * secs * frame_rate)).mulconst(amp))
        amp *= decay
    return pg.MixPE(src,*delay_units)

sourceA= pg.WavReaderPE("samples/ItsGonnaRain_Original.wav")
noloopA= sourceA.crop(pg.Extent(start=0,end=secs(6))).env2(secs(.13),secs(3))
loopA = pg.LoopPE(sourceA,secs(2.95),secs(.8)).crop(pg.Extent(start=0,end=secs(60))).env2(secs(.13),secs(5))
loopA2 = pg.LoopPE(sourceA,secs(2.95),secs(.78)).crop(pg.Extent(start=0,end=secs(60))).env2(secs(.13),secs(15))
loopB = pg.LoopPE(sourceA,secs(3.95),secs(.75)).crop(pg.Extent(start=0,end=secs(60))).env2(secs(3),secs(5))
loopB2 = pg.LoopPE(sourceA,secs(3.95),secs(.72)).crop(pg.Extent(start=0,end=secs(60))).env2(secs(3),secs(15))
loopC = pg.LoopPE(sourceA,secs(5.5),secs(.75)).crop(pg.Extent(start=0,end=secs(60))).env2(secs(3),secs(5))
loopC2 = pg.LoopPE(sourceA,secs(5.5),secs(.71)).crop(pg.Extent(start=0,end=secs(60))).env2(secs(3),secs(10))
loopC3 = pg.LoopPE(sourceA,secs(5.5),secs(.67)).crop(pg.Extent(start=0,end=secs(60))).env2(secs(3),secs(15))

elements = []
gain = 1.85

t = 0
elements.append(mix_at(noloopA,secs(t),gain * 0.5))
t = t + 4
elements.append(mix_at(loopA2.env2(secs(4),secs(5)),secs(t),gain * 0.5))
elements.append(mix_at(loopA,secs(t),gain * 0.5))
t = t + 12
elements.append(mix_at(loopB,secs(t),gain * 0.5))
elements.append(mix_at(loopB2,secs(t),gain * 0.5))
t = t + 11
elements.append(mix_at(loopC,secs(t),gain * 0.5))
elements.append(mix_at(loopC2,secs(t),gain * 0.5))
elements.append(mix_at(loopC3,secs(t),gain * 0.5))
t = t + 12
elements.append(mix_at(noloopA,secs(t),gain * 0.5))


mosh = pg.LimiterPE(pg.MixPE(*elements))
hi_mosh = pg.Biquad2PE(mosh, 0, 88, 22, "highpass")
hi_mosh.play()