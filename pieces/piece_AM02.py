import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import numpy as np
import pygmu as pg
import soundfile as sf


# convert between complex and (magnitude, phase)
def c2mp(c): return np.abs(c), np.angle(c)
def mp2c(mag, phase): return mag * np.exp(1j*phase)

def monofy(frames):
    # Convert stero frames (2 column, N rows) into mono (one row)
    return np.dot(frames, [[0.5], [0.5]]).reshape(-1)

def sterofy(frames):
    # convert horizontal mono array into stero frames (2 columns, N rows)
    return np.dot(frames.reshape(-1, 1), [[1.0, 1.0]])

def soundPE(filename):
    frames, frame_rate = sf.read(filename)
    return pg.ArrayPE(frames)

def delays(src, secs, howmany = 1, decay = 1):
    frame_rate = 48000
    delay_units = []
    amp = 1
    for i in range(1, howmany):
        delay_units.append(src.delay(int(i * secs * frame_rate)).gain(amp))
        amp *= decay
    return pg.MixPE(src,*delay_units)

def secs(s):
    return int(s * 48000)

def mix_at(src, t, amp = 1):
    return pg.DelayPE(src,t).gain(amp)
 

fade_in = secs(0.3)
fade_out = secs(2.1)

sourceA = pg.WavReaderPE("samples/KeyboardSonatainECKPiano.wav").crop(pg.Extent(start=0,end=secs(10))).env(secs(0.5),secs(0.5))
sourceA2 = pg.WavReaderPE("samples/KeyboardSonatainECKPiano.wav").crop(pg.Extent(start=20,end=secs(30))).env(secs(0.5),secs(0.5))
sourceB = pg.WavReaderPE("samples/PrettyGirl_Gleason.wav").crop(pg.Extent(start=20,end=secs(30))).env(secs(0.5),secs(0.5))
sourceC = pg.WavReaderPE("samples/TamperClip93.wav")

frag1 = pg.EnvPE(sourceA, fade_in, fade_out).reverse(10)
frag1a = delays(frag1, 0.6,5,0.8).gain(0.3)
frag1b = delays(frag1a, 0.16,7,0.88).gain(0.2)

frag11 = pg.EnvPE(sourceA2, fade_in, fade_out).reverse(10)
frag11a = delays(frag1, 0.6,5,0.8)
frag11b = delays(frag1a, 0.16,5,0.88).gain(0.2)

frag2 = pg.EnvPE(sourceB, fade_in, fade_out).reverse(10).gain(1.1)
frag2a = delays(frag2, 0.36,7,0.78)

frag3 = pg.EnvPE(sourceC, fade_in * 4, fade_out).gain(0.15)
frag3a = delays(frag3, 0.36,7,0.78)

#frag1b.play()

elements = []

gain = 1.85

t = 0
elements.append(mix_at(frag1a,secs(t),gain * 0.25))
t = t + 3
elements.append(mix_at(frag3a,secs(t),gain * 0.13))
t = t + 3
elements.append(mix_at(frag2a,secs(t),gain * 0.3))
t = t + 4
elements.append(mix_at(frag1b,secs(t),gain * 0.25))
t = t + 4
elements.append(mix_at(frag3a,secs(t),gain * 0.73))
elements.append(mix_at(frag11b,secs(t),gain * 0.85))
t = t + 3

mosh = pg.MixPE(*elements)

mosh.play()



