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

Plum0 = pg.WavReaderPE("samples/TamperFrame_SugarPlumFaries_Edit2.wav").crop(pg.Extent(secs(3),secs(33))).time_shift(-secs(3))
PlumA = Plum0.warp_speed(0.5)
PlumB = Plum0.warp_speed(0.35)


Drummy = pg.WavReaderPE("samples/TamperFrame_SwingTheory.wav").crop(pg.Extent(secs(0.1),secs(6))).time_shift(-secs(0.1)).gain(0.5)

PlumAThin1 = pg.BQ2HighPassPE(Drummy, f0=520, q=44).gain(0.08)
PlumAThin2 = pg.BQ2BandPassPE(Drummy, f0=520, q=14).gain(0.8)

PlumAThin2.play()

limited = PlumAThin2.limit_a(threshold_db=-30, headroom_db=5)
limited.play()

src = PlumAThin2
env = pg.EnvDetectPE(src.time_shift(-1150), attack=0.04, release=0.3)
compressed = pg.CompressorPE(src, env, ratio=3.0, threshold_db=-30, makeup_db=14)
pg.Transport(compressed).play()


#test = delays(PlumAThin1,0.7,7,0.75)
test = delays(PlumAThin1,0.7,3,0.75)


elements = []

gain = 0.8

t = 0
# elements.append(mix_at(PlumAThin1,secs(t),gain))

# t += 5.5
elements.append(delays(mix_at(PlumAThin1,secs(t),gain),0.7,7,0.75))
#elements.append(mix_at(PlumAThin1,secs(t),gain))


dst = pg.WavWriterPE(mosh, "test.wav")
pg.FtsTransport(dst).play()
pg.Transport(pg.WavReaderPE("test.wav")).play()


# convolved = pg.ConvolvePE(mosh.gain(0.08), impulse)
# dst = pg.WavWriterPE(convolved, "test2.wav")
# pg.FtsTransport(dst).play()
# pg.Transport(pg.WavReaderPE("test2.wav")).play()

