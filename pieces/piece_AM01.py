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

def mogrify(filename):
    """
    Read in an entire sound file, take its fft, randomize the phase, and convert
    back into the time domain.
    """
    frames, frame_rate = sf.read(filename)
    # mix to mono, horizontal array
    frames = monofy(frames)
    # take the FFT, randomize the phases, convert back to time domain via IFFT
    analysis = np.fft.fft(frames)
    magnitudes = np.abs(analysis)
    n_frames = magnitudes.shape[0]
    phases = np.random.default_rng().random(n_frames) * 2.0 * np.pi
    mog_analysis = mp2c(magnitudes, phases)
    mog_frames = np.real(np.fft.ifft(mog_analysis))
    # convert single horizotal array into stereo columns
    mog_frames = sterofy(mog_frames)
    return pg.ArrayPE(mog_frames)

def soundPE(filename):
    frames, frame_rate = sf.read(filename)
    return pg.ArrayPE(frames)

def delays(src, secs, howmany = 1, decay = 1):
    frame_rate = 48000
    delay_units = []
    amp = 1.0
    for i in range(1, howmany):
        print(frame_rate)
        delay_units.append(src.time_shift(int(i * secs * frame_rate)).gain(amp))
        amp *= decay
    return pg.MixPE(src,*delay_units)

def secs(s):
    return int(s * sample_rate)
 

sample_rate = 48000

fade_in = secs(0.3)
fade_out = secs(2.1)


sourceA = pg.WavReaderPE("samples/music/Tamper_MagnifyingFrame1.wav")
sourceB = pg.WavReaderPE("samples/music/TamperClip38.wav")
sourceC = mogrify("samples/music/TamperClip38.wav").crop(pg.Extent(start=140000)).time_shift(-140000)

frag1 = pg.SplicePE(sourceA, fade_in, fade_out).reverse(5)
frag2 = pg.SplicePE(sourceB, fade_in, fade_out).reverse(5)
frag3 = pg.SplicePE(sourceC, fade_in * 4, fade_out).gain(2)

frag4 = pg.MixPE(frag3,frag3.time_shift(20000).gain(0.8),frag3.time_shift(40000).gain(0.6))
frag5 = delays(frag3, 0.7, 18, 0.76)

elements = [frag5, frag1.time_shift(secs(3)), frag2.time_shift(secs(3)), frag1.time_shift(secs(8)), frag2.time_shift(secs(10)), frag5.time_shift(secs(18))]

mosh = pg.MixPE(*elements)
mosh2 = mosh.crop(pg.Extent(start=0,end=720000)).splice(fade_in, fade_out).reverse(16).splice(secs(0.01),secs(7))

mosh3 = pg.MixPE(mosh,mosh2.time_shift(secs(5.5)))

wet_mix = delays(mosh3, 0.5, 4, 0.7).gain(2)

wet_mix.pygplay()

