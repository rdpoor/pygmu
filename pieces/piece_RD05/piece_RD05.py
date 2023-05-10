import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "../..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

# reverb = pg.WavReaderPE('../../samples/IR/480_Large Church.wav').gain(0.3)
# reverb = pg.WavReaderPE('../../samples/IR/Conic Long Echo Hall.wav').gain(0.4)
# reverb = pg.WavReaderPE('../../samples/IR/Large Bottle Hall.wav')
# reverb = pg.WavReaderPE('../../samples/IR/Masonic Lodge.wav')
# reverb = pg.WavReaderPE('../../samples/IR/Space4ArtGallery.wav')
reverb = pg.WavReaderPE('../../samples/IR/St Nicolaes Church.wav')

jaspers = [
    pg.WavReaderPE("jasper_1.wav"),
    pg.WavReaderPE("jasper_2.wav"),
    pg.WavReaderPE("jasper_3.wav"),
    pg.WavReaderPE("jasper_4.wav"),
    pg.WavReaderPE("jasper_5.wav"),
    ]

def all_jasper():
    pes = []
    s = 0
    for jasper in jaspers:
        pes.append(jasper.time_shift(s))
        s += jasper.frame_count()
    return pg.MixPE(*pes);


def deep_jasper(pe):
    return pe.warp_speed(0.5)

def wet_jasper(pe):
    echos = pg.MixPE(pe,
                     pe.time_shift(30000).gain(0.4),
                     pe.time_shift(50000).gain(0.2),
                     pe.time_shift(60000).gain(0.12))
    return pg.ConvolvePE(echos.gain(0.05), reverb)


dst = wet_jasper(deep_jasper(all_jasper()))
dst = pg.WavWriterPE(dst, "test.wav")
pg.FtsTransport(dst).play()
pg.Transport(pg.WavReaderPE("test.wav")).play()
