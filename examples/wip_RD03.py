import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

beat = pg.WavReaderPE("samples/BigBeat120bpm10.wav")
beat_bpm = 120
eight_beat_duration = 176552  # eight beats
beat_duration = eight_beat_duration / 8
beat_loop = beat.loop(0, int(eight_beat_duration))

def beats(b):
    return int(b * beat_duration)

durs = {
    "w.": beats(4.5),  # dotted whole note
    "w": beats(4),  # whole note
    "h.": beats(2.5),  # dotted half note
    "h": beats(2),  # half note
    "q.": beats(1.5),  # dotted quarter note
    "q": beats(1),  # quarter note
    "e.": beats(0.75),  # dotted eighth note
    "e": beats(0.5),  # eighth note
    "s.": beats(0.375),  # dotted sixteenth note
    "s": beats(0.25),  # sixteenth note
    "tw": beats(4 / 3.0),  # whole note triplet
    "th": beats(2 / 3.0),  # half note triplet
    "tq": beats(1 / 3.0),  # quarter note triplet
    "te": beats(0.5 / 3.0),  # eighth note triplet
    "ts": beats(0.25 / 3.0),  # sixteenth note triplet
}

pits = {
    "c1": 24,
    "cs1": 25,
    "df1": 25,
    "d1": 26,
    "ds1": 27,
    "ef1": 27,
    "e1": 28,
    "f1": 29,
    "fs1": 30,
    "gf1": 30,
    "g1": 31,
    "gs1": 32,
    "af1": 32,
    "a1": 33,
    "as1": 34,
    "bf1": 34,
    "b1": 35,
    "c2": 36,
    "cs2": 37,
    "df2": 37,
    "d2": 38,
    "ds2": 39,
    "ef2": 39,
    "e2": 40,
    "f2": 41,
    "fs2": 42,
    "gf2": 42,
    "g2": 43,
    "gs2": 44,
    "af2": 44,
    "a2": 45,
    "as2": 46,
    "bf2": 46,
    "b2": 47,
    "c3": 48,
    "cs3": 49,
    "df3": 49,
    "d3": 50,
    "ds3": 51,
    "ef3": 51,
    "e3": 52,
    "f3": 53,
    "fs3": 54,
    "gf3": 54,
    "g3": 55,
    "gs3": 56,
    "af3": 56,
    "a3": 57,
    "as3": 58,
    "bf3": 58,
    "b3": 59,
    "c4": 60,
    "cs4": 61,
    "df4": 61,
    "d4": 62,
    "ds4": 63,
    "ef4": 63,
    "e4": 64,
    "f4": 65,
    "fs4": 66,
    "gf4": 66,
    "g4": 67,
    "gs4": 68,
    "af4": 68,
    "a4": 69,
    "as4": 70,
    "bf4": 70,
    "b4": 71,
    "c5": 72,
    "cs5": 73,
    "df5": 73,
    "d5": 74,
    "ds5": 75,
    "ef5": 75,
    "e5": 76,
    "f5": 77,
    "fs5": 78,
    "gf5": 78,
    "g5": 79,
    "gs5": 80,
    "af5": 80,
    "a5": 81,
    "as5": 82,
    "bf5": 82,
    "b5": 83,
    "c6": 84,
    "cs6": 85,
    "df6": 85,
    "d6": 86,
    "ds6": 87,
    "ef6": 87,
    "e6": 88,
    "f6": 89,
    "fs6": 90,
    "gf6": 90,
    "g6": 91,
    "gs6": 92,
    "af6": 92,
    "a6": 93,
    "as6": 94,
    "bf6": 94,
    "b6": 95,
    "c7": 96,
    "cs7": 97,
    "df7": 97,
    "d7": 98,
    "ds7": 99,
    "ef7": 99,
    "e7": 100,
    "f7": 101,
    "fs7": 102,
    "gf7": 102,
    "g7": 103,
    "gs7": 104,
    "af7": 104,
    "a7": 105,
    "as7": 106,
    "bf7": 106,
    "b7": 107,
}


def combify(notes):
    pes = []
    s = 0
    for pit, dur, Q in notes:
        e = s + durs[dur]
        if pit != "":
            freq = ut.pitch_to_freq(pits[pit])
            snip = beat_loop.crop(pg.Extent(int(s), int(e)))
            if Q == 0:
                pes.append(snip)
            else:
                pes.append(pg.CombPE(snip, f0=freq, q=Q))
        else:
            # blank pitch => rest
            pass
        s = e
    return pg.MixPE(*pes)


def biquadify(notes):
    pes = []
    s = 0
    for pit, dur, Q in notes:
        e = s + durs[dur]
        if pit != "":
            freq = ut.pitch_to_freq(pits[pit])
            snip = beat_loop.crop(pg.Extent(int(s), int(e)))
            if Q == 0:
                pes.append(snip)
            else:
                pes.append(pg.Biquad2PE(snip, f0=freq, q=Q))
        else:
            # blank pitch => rest
            pass
        s = e
    return pg.MixPE(*pes)


intro_motif = [
    ["a5", "w", 230], # 0
    ["a5", "w", 230], # 4
    ["a5", "e", 230], # 8
    ["a5", "e", 165],
    ["a5", "e", 114],
    ["a5", "e", 80],
    ["a5", "e", 55],
    ["a5", "e", 38],
    ["a5", "e", 26],
    ["a5", "e", 18],
    ["a5", "e", 12], #12
    ["a5", "e", 8],
    ["a5", "e", 6],
    ["a5", "e", 4],
    ["a5", "e", 2],
    ["a5", "e", 2],
    ["a5", "e", 1],
    ["a5", "e", 1],
                     #16
]

ostinato = beat_loop

motif = [
    ["d5", "q", 10],
    ["f5", "e", 10],
    ["e5", "e", 10],
    ["f5", "q", 10],
    ["d5", "q", 10],
    ["d5", "q", 10],
    ["f5", "e", 10],
    ["e5", "e", 10],
    ["f5", "q", 10],
    ["d5", "q", 10],
]

motif12 = [
    ["d6", "q", 20], # 0
    ["f6", "e", 20],
    ["e6", "e", 20],
    ["f6", "q", 20],
    ["d6", "q", 20],
    ["d6", "q", 20], # 4
    ["f6", "e", 20],
    ["e6", "e", 20],
    ["f6", "q", 20],
    ["d6", "q", 20],
                     # 8
]

motif19 = [
    ["a6", "q", 20],
    ["c7", "e", 20],
    ["b6", "e", 20],
    ["c7", "q", 20],
    ["a6", "q", 20],
    ["a6", "q", 20],
    ["c7", "e", 20],
    ["b6", "e", 20],
    ["c7", "q", 20],
    ["a6", "q", 20],
]

motif24 = [
    ["d7", "q", 20],
    ["f7", "e", 20],
    ["e7", "e", 20],
    ["f7", "q", 20],
    ["d7", "q", 20],
    ["d7", "q", 20],
    ["f7", "e", 20],
    ["e7", "e", 20],
    ["f7", "q", 20],
    ["d7", "q", 20],
]

bass = [
    ["d4", "w", 64],
    ["b3", "w", 64],
    ["c4", "w", 64],
    ["f3", "h", 64],
    ["c4", "h", 64],
]

bass_m12 = [
    ["d2", "w", 64],
    ["b1", "w", 64],
    ["c2", "w", 64],
    ["f2", "h", 64],
    ["c2", "h", 64],
]

middle_8_beat = beat.delay(beats(-7)).crop(pg.Extent(0, beats(1))).loop(0, beats(1))

middle_8_motif = [
    ["g5", "q", 20],
    ["g5", "e", 20],
    ["g5", "e", 20],
    ["g5", "q.", 20],
    ["fs5", "e", 20],
    ["g5", "q", 20],
    ["g5", "e", 20],
    ["g5", "e", 20],
    ["g5", "q.", 20],
    ["a5", "e", 20],
    ["g5", "q", 20],
    ["g5", "e", 20],
    ["g5", "e", 20],
    ["g5", "q.", 20],
    ["fs5", "e", 20],
    ["g5", "q", 20],
    ["g5", "e", 20],
    ["g5", "e", 20],
    ["g5", "q.", 20],
    ["a5", "e", 20],
]

# =================================
# rendered sections.

intro = pg.MixPE(  # beats 0-24
    combify(intro_motif).gain(0.25),  # 0 - 16
    beat_loop.crop(pg.Extent(beats(16), beats(32))).gain(0.25), # 16 - 32
    combify(motif12).delay(beats(16)), # 16 - 24
)

v1 = pg.MixPE(  # beats 24-48
    beat_loop.crop(pg.Extent(0, beats(16))).gain(0.25),
    combify(bass).gain(0.8),
    combify(motif),
    combify(motif).delay(beats(8)),
)

v2 = pg.MixPE(  # beats 48-64
    beat_loop.crop(pg.Extent(0, beats(16))).gain(0.25),
    combify(bass).gain(0.8),
    biquadify(bass_m12).gain(0.0625),
    combify(motif),
    combify(motif).delay(beats(8)),
)

v3 = pg.MixPE(  # beats 64-80
    beat_loop.crop(pg.Extent(0, beats(16))).gain(0.25),
    combify(bass).gain(0.8),
    biquadify(bass_m12).gain(0.0625),
    combify(motif19),
    combify(motif).gain(0.7),
    combify(motif12).gain(0.7).delay(beats(0.25)),
    combify(motif19).delay(beats(8)),
    combify(motif).delay(beats(8)).gain(0.7),
    combify(motif12).delay(beats(8)).gain(0.7).delay(beats(0.25)),
)

bridge_snip = beat_loop.crop(pg.Extent(beats(15.75), beats(16))).delay(
    beats(-15.75)
)

bridge = pg.MixPE(  # beats 80-96
    middle_8_beat.crop(pg.Extent(int(0), beats(16))).gain(0.4),
    combify(middle_8_motif).gain(0.8),
)

outro_snip = v3.crop(pg.Extent(beats(15.75))).delay(beats(-15.75))

outro = pg.MixPE(
    outro_snip.delay(beats(0)),
    outro_snip.delay(beats(0.25)).gain(0.900000),
    outro_snip.delay(beats(0.55)).gain(0.810000),
    outro_snip.delay(beats(0.90)).gain(0.729000),
    outro_snip.delay(beats(1.30)).gain(0.656100),
    outro_snip.delay(beats(1.75)).gain(0.590490),
    outro_snip.delay(beats(2.25)).gain(0.531441),
    outro_snip.delay(beats(2.80)).gain(0.478297),
    outro_snip.delay(beats(3.40)).gain(0.430467),
    outro_snip.delay(beats(4.05)).gain(0.387420),
    outro_snip.delay(beats(4.75)).gain(0.348678),
    outro_snip.delay(beats(5.50)).gain(0.313811),
    outro_snip.delay(beats(6.30)).gain(0.282430),
    outro_snip.delay(beats(7.15)).gain(0.254187),
    outro_snip.delay(beats(8.05)).gain(0.228768),
    outro_snip.delay(beats(9.0)).gain(0.205891),
    outro_snip.delay(beats(10.05)).gain(0.185302),
)

mix = pg.MixPE(
    intro.delay(beats(0)),
    v1.delay(beats(32)),
    v2.delay(beats(48)),
    v3.delay(beats(64)),
    bridge.delay(beats(80)),
    v3.delay(beats(96)),
    v3.delay(beats(112)),
    v3.delay(beats(112.25)).gain(0.5),
    outro.delay(beats(128)),
)

dst = pg.WavWriterPE(mix, "examples/wip_RD03.wav")
pg.FtsTransport(dst).play()

pg.Transport(pg.WavReaderPE("examples/wip_RD03.wav")).play()
