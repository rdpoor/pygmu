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

reverb_path = 'samples/IR/Large Wide Echo Hall.wav'

impulse = pg.WavReaderPE(reverb_path)

Faun0 = pg.WavReaderPE("samples/TamperFrame_AfternoonOfAFaun.wav").crop(pg.Extent(0,secs(36)))
FaunRev = Faun0.reverse(25)

Claire = pg.WavReaderPE("samples/TamperFrame_ClaireDeLune_Edit.wav").crop(pg.Extent(secs(25),secs(41))).splice(secs(1.4),secs(1))

# plain interpolation

Faund4 = pg.TimewarpPE(Faun0, pg.IdentityPE().gain(0.666))
Faund12 = pg.TimewarpPE(Faun0, pg.IdentityPE().gain(0.333)).crop(pg.Extent(0,secs(36))).splice(100,secs(1))
Faund24 = pg.TimewarpPE(Faun0, pg.IdentityPE().gain(0.1666)).crop(pg.Extent(0,secs(76))).splice(100,secs(1))

FaundR4 = pg.TimewarpPE(FaunRev, pg.IdentityPE().gain(0.666)).splice(secs(1.5),secs(1))
FaundR12 = pg.TimewarpPE(FaunRev, pg.IdentityPE().gain(0.333)).splice(secs(1.5),secs(1))
FaundR24 = pg.TimewarpPE(FaunRev, pg.IdentityPE().gain(0.1666)).splice(secs(1.5),secs(1))


# FaundR4.play()
# FaundR12.play()

elements = []

gain = 0.8

t = 0
elements.append(mix_at(Faund4,secs(t),gain).pan(90))

t += 2.5
elements.append(delays(mix_at(Faund12,secs(t),gain).pan(-120),0.7,3,0.5))

t += 3
elements.append(mix_at(Faund24,secs(t),gain).pan(20))

t += 24
elements.append(mix_at(FaundR12,secs(t),gain).pan(-120))
t += 1.6
elements.append(mix_at(FaundR4,secs(t),gain).pan(90))



t += 9
elements.append(delays(mix_at(Faun0,secs(t),gain/2).pan(10),0.7,3,0.5))
t += 0.7
elements.append(delays(mix_at(Faun0,secs(t),gain/3).pan(10),1.7,4,0.5))

# ct = 70
# elements.append(mix_at(Claire,secs(ct),gain * 10).pan(-30))


mosh = pg.MixPE(*elements).crop(pg.Extent(0,secs(75))).splice(10,secs(1.4))

convolved = pg.ConvolvePE(mosh.gain(0.08), impulse)

dst = pg.WavWriterPE(convolved, "test.wav")
pg.FtsTransport(dst).play()
pg.Transport(pg.WavReaderPE("test.wav")).play()

#pg.Transport(convolved).play()

