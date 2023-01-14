import os
import sys
import numpy as np

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

def stof(seconds):
    return int(seconds * frame_rate)

dur = 0.5

frame_rate = 48000
t = 0
pes = []
for n_harmonics in [4, 9, 0]:
    for pitch in [38, 45, 52, 59, 66, 73]:
        freq = ut.pitch_to_freq(pitch)
        src = pg.BlitSawPE(frequency=freq, n_harmonics=n_harmonics, frame_rate=frame_rate)
        pes.append(src.crop(pg.Extent(0, stof(dur))).delay(stof(t)))
        t += dur
for n_harmonics in [4, 9, 0]:
    # ramp pitch from 38 to 73 over dur * 6 seconds
    freq_pe = pg.RampPE(ut.mtof(38), ut.mtof(73), pg.Extent(0, stof(dur*6)))
    blit_pe = pg.BlitSawPE(frequency=freq_pe, n_harmonics=n_harmonics, frame_rate=frame_rate)
    pes.append(blit_pe.crop(freq_pe.extent()).delay(stof(t)))
    t += dur * 6
mix = pg.MixPE(*pes).gain(0.3)

# freq_pe = pg.RampPE(110, 440, pg.Extent(0, stof(6)), channel_count=1)
# blit_pe = pg.BlitSawPE(frequency=freq_pe, n_harmonics=9, frame_rate=frame_rate).crop(freq_pe.extent())
# mix = blit_pe.gain(0.3)

output_filename = "examples/blit_example.wav"
mix = pg.WavWriterPE(mix, output_filename).crop(pg.Extent(0, mix.extent().duration()))
#pg.FtsTransport(mix).play()
#pg.Transport(pg.WavReaderPE(output_filename)).play()
pg.Transport(mix).play()
