import numpy as np
import pygmu as pg
import soundfile as sf
from pygmu.extent import Extent
from env2_pe import Env2PE
from interpolate_pe import InterpolatePE


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

def flipper(filename):
    frames, frame_rate = sf.read(filename)
    return pg.ArrayPE(np.flip(frames))
    #return pg.ReversePE(frames)

def soundPE(filename):
    frames, frame_rate = sf.read(filename)
    return pg.ArrayPE(frames)
 
    
#pg.Transport().play(mogrify("../samples/PED_118_Em_Whistle_Flute.wav"))

#pg.Transport().play(flipper("../samples/04_Cat.wav"))

#pg.Transport().play(InterpolatePE(pg.WavReaderPE("../samples/04_Cat.wav"), 0.25))

fade_in = 11000
fade_out = 70000

pg.Transport(pg.MixPE(
    pg.MulPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/Tamper_MagnifyingFrame1.wav"), fade_in, fade_out)), pg.ConstPE(0.15)),
    pg.MulPE(pg.DelayPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/TamperClip38.wav"), fade_in, fade_out)), 22000), pg.ConstPE(0.5)),
    pg.MulPE(pg.DelayPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/TamperClip38.wav"), fade_in, fade_out)), 80000), pg.ConstPE(0.5)),
    pg.MulPE(pg.DelayPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/Tamper_MagnifyingFrame1.wav"), fade_in, fade_out)), 80000), pg.ConstPE(0.25)),
    pg.MulPE(pg.ReversePE(pg.DelayPE(Env2PE(pg.CropPE(mogrify("../samples/TamperClip38.wav"), Extent(start=110000)), fade_in, fade_out), -110000)), pg.ConstPE(0.5)),
    pg.MulPE(pg.DelayPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/Tamper_MagnifyingFrame1.wav"), fade_in * 6, fade_out * 6)), 120000), pg.ConstPE(0.5)),
    pg.MulPE(pg.DelayPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/Tamper_MagnifyingFrame1.wav"), fade_in * 6, fade_out * 6)), 320000), pg.ConstPE(0.5)),
    pg.MulPE(pg.DelayPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/Tamper_MagnifyingFrame1.wav"), fade_in * 6, fade_out * 6)), 720000), pg.ConstPE(0.5)),
    pg.MulPE(pg.DelayPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/TamperClip38.wav"), fade_in, fade_out)), 160000), pg.ConstPE(0.35)),
    pg.MulPE(pg.DelayPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/TamperClip38.wav"), fade_in, fade_out * 6)), 320000), pg.ConstPE(0.18)),
    pg.MulPE(pg.DelayPE(Env2PE(pg.WavReaderPE("../samples/TamperClip38.wav"), fade_in * 6, fade_out * 2), 420000), pg.ConstPE(0.28)),
    pg.MulPE(pg.DelayPE(pg.ReversePE(Env2PE(pg.WavReaderPE("../samples/Tamper_MagnifyingFrame1.wav"), fade_in, fade_out * 4)), 480000), pg.ConstPE(0.21)),
)).play()
