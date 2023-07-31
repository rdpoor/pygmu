import numpy as np
import os
import re
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

FILE_PREFIX = "/Users/r/Projects/GiantFish/"
def ingest(filename):
    # read wavfile, trim (fade in, fade out) and compress.
    # return PE.
    wav_pe = pg.WavReaderPE(FILE_PREFIX + filename + ".wav")
    env_pe = pg.EnvDetectPE(wav_pe, attack=0.999, release=0.001)
    # cmp_pe = pg.CompLimPE(wav_pe, env_pe, ratio=3.0, limit_db=-4.0, squelch_db=-60)
    cmp_pe = pg.CompressorPE(wav_pe, env_pe, threshold_db=-20, ratio=5.0, makeup_db=0)
    return cmp_pe

def trio(f1, f2, f3):
    # mix three sound files, panning left, center, right
    # return a duple of (mix, max_dur)
    c1 = ingest(f1)
    c2 = ingest(f2)
    c3 = ingest(f3)

    p1 = pg.SpatialPE(c1, degree=-90, curve='cosine')
    p2 = pg.SpatialPE(c2, degree=0, curve='cosine')
    p3 = pg.SpatialPE(c3, degree=90, curve='cosine')

    max_dur = max(p1.extent().duration(),
                  p2.extent().duration(),
                  p3.extent().duration())
    return (pg.MixPE(p1, p2, p3), max_dur)

def peace():
    delay = 0
    segments = []
    pe, duration = trio("N_01", "R_01", "N2_01")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_02", "R_02", "N2_02")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_03", "R_03", "N2_03")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_04", "R_04", "N2_04")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_05", "R_05", "N2_05")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_06", "R_06", "N2_06")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_07", "R_07", "N2_07")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_08", "R_08", "N2_08")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_09", "R_09", "N2_09")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_10", "R_10", "N2_10")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_11", "R_11", "N2_11")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_12", "R_12", "N2_12")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_13", "R_13", "N2_13")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_14", "R_14", "N2_14")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_15", "R_15", "N2_15")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    pe, duration = trio("N_16", "R_16", "N2_16")
    segments.append(pg.TimeShiftPE(pe, delay))
    delay += duration
    return pg.MixPE(*segments)

# mix = ingest("R_01");
mix = peace()
mix.pygplay("TWSRM")
