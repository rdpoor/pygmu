import os
import sys
import numpy as np

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

t = 0
pes = []
for w in ['sawtooth', 'pulse']:
    for h in range(2, 20, 4):
        for pitch in [57, 61, 64, 68, 69]:
            f = ut.pitch_to_freq(pitch)
            period = 48000 / f
            src = pg.BlitsigPE(frequency=f, n_harmonics=h, channel_count=1, frame_rate=48000, waveform=w)
            pes.append(src.crop(pg.Extent(0, 12000)).delay(t))
            t += 13000
mix = pg.MixPE(*pes)
# mix = pg.WavWriterPE(mix, "examples/blit_example.wav").crop(pg.Extent(0, mix.extent().duration()))
pg.Transport(mix).play()
