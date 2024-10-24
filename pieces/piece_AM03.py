import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import numpy as np
import pygmu as pg
import soundfile as sf
import utils as ut

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
        delay_units.append(src.time_shift(int(i * secs * frame_rate)).gain(amp))
        amp *= decay
    return pg.MixPE(src,*delay_units)

def secs(s):
    return int(s * 48000)

def mix_at(src, t, amp = 1):
    return pg.TimeShiftPE(src,t).gain(amp)
 
semitone = pow(2.0, 1/12)


def make_timeline(pitches, n_frames = 90000):
    timeline = np.ndarray([0, 1], dtype=np.float32)
    start_frame = 0
    for p in pitches:
        freq = semitone**p
        ramp_dur = int(n_frames / freq)
        ramp = pg.utils.ramp_frames(0, n_frames, ramp_dur, 1)
        timeline = np.concatenate((timeline, ramp))
    return pg.ArrayPE(timeline)




fade_in = secs(0.3)
fade_out = secs(2.1)

sourceA = pg.WavReaderPE("samples/music/OldLaces_Schifrin.wav").crop(pg.Extent(start=0,end=secs(30))).splice(secs(0.5),secs(0.5))
sourceB = pg.WavReaderPE("samples/music/OldLaces_Schifrin.wav").crop(pg.Extent(start=30,end=secs(50))).splice(secs(0.5),secs(0.5))
sourceC = pg.WavReaderPE("samples/music/TamperClip93.wav")

frag1 = pg.SplicePE(sourceA, fade_in, fade_out).reverse(30 * 48000)
frag1a = delays(frag1, 0.6,15,0.87)
#frag1b =  pg.TimewarpPE(delays(frag1a, 0.16,17,0.9).gain(6.82), make_timeline([-20, -16]))
frag1c = delays(frag1a, 0.5,15,0.92)

frag2 = pg.SplicePE(sourceB, fade_in, fade_out).reverse(30 * 48000)
frag2a = delays(frag1, 0.6,25,0.91).gain(0.13).crop(pg.Extent(start=0,end=secs(50))).reverse(50 * 48000)

frag3 = pg.SplicePE(sourceC, fade_in, fade_out).reverse(5 * 48000).gain(0.82)
frag3b = delays(frag3, 0.36,17,0.94)

elements = []
gain = 1.85
t = 0
elements.append(mix_at(frag1a,secs(t),gain * 0.25))

t = t + 7
elements.append(mix_at(frag2a,secs(t),gain * 0.43))

elements.append(mix_at(frag3b,secs(t),gain * 2.43))

mosh = pg.LimiterPE(pg.MixPE(*elements)).gain(1.5)

mosh.pygplay()



