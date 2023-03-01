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

reverb_path = 'samples/IR/Conic Long Echo Hall.wav'

impulse = pg.WavReaderPE(reverb_path)

Plum0 = pg.WavReaderPE("samples/TamperFrame_SugarPlumFaries_Edit2.wav").crop(pg.Extent(secs(3),secs(33))).delay(-secs(3))
PlumA = Plum0.warp_speed(0.5)
PlumB = Plum0.warp_speed(0.35)

elements = []

gain = 0.8

t = 0
elements.append(mix_at(PlumA,secs(t),gain))

t += 5.5
#elements.append(delays(mix_at(PlumB,secs(t),gain).pan(-120),0.7,3,0.5))
elements.append(mix_at(PlumB,secs(t),gain))

mosh = pg.MixPE(*elements)
mosh.play()


# convolved = pg.ConvolvePE(mosh.gain(0.08), impulse)
# dst = pg.WavWriterPE(convolved, "test2.wav")
# pg.FtsTransport(dst).play()
# pg.Transport(pg.WavReaderPE("test2.wav")).play()

