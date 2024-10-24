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

print("hit return each sample stops playing to hear the next...")
# pg.Transport(pg.WavReaderPE("samples/music/044-n-2723_stero.wav")).play()
# pg.Transport(mogrify("samples/music/044-n-2723_stero.wav")).play()

pg.Transport(pg.WavReaderPE("samples/loops/04_Cat.wav")).play()
pg.Transport(mogrify("samples/loops/04_Cat.wav")).play()

pg.Transport(pg.WavReaderPE("samples/spoken/11_uh_uh_f.wav")).play()
pg.Transport(mogrify("samples/spoken/11_uh_uh_f.wav")).play()
