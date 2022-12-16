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

# reboot:
# fade-in: 16 beats wanders Center - Left - Center - Right - Center during fade in
# intro 40 beats: "call and response" 8va apart:
#   drums only: 8 beats
#   motif+12: 8 beats (panned slightly left)
#   drums only: 8 beats
#   motif+0: 8 beats (panned slightly right)
#   drums only: 8 beats
# v1: 16 beats: motif+12, motif+0, comb filter bass
# v2: 16 beats: add biquad bass
# v3: 16 beats: add motif+9, +21 panned hockets (delayed 0.25 beat)
# bridge_a: 16 beats just repeated note, bridge_motif
# bridge_b: 16 beats: add plucked melody
# v4: 16 beats: same as v3
# v5: 16 beats: v4 + (motif, motif+9, motif+12, motif+21).delay(0.25)
# fade_out: "clock running down", panned center - left - right...

frames_per_quarter = beat_duration

def gen_fade_in():
    pes = []
    freq = ut.pitch_to_freq(93)
    dur = int(frames_per_quarter / 2) # each note lasts one eighth beat
    n_beats = 16

    s = int(0)
    q = 256
    for eighths in range(2 * n_beats):
        e = s + beats(0.5)
        u = eighths / (2 * n_beats)    # ramp from 0.0 to 1.0
        # pan goes through one cycle, damped...
        pan_degree = 75 * (1-u) * np.sin(np.pi * 2 * u)
        q = max(1, q * 0.85)
        snip = beat_loop.mono().crop(pg.Extent(int(s), int(e)))
        snip = pg.CombPE(snip, f0 = freq, q = q)
        snip = pg.SpatialAPE(snip, degree=pan_degree)
        pes.append(snip)
        s = e
    return pg.MixPE(*pes).gain(0.25)

motif_a = [
    (62, beats(1)),
    (65, beats(0.25)),
    (64, beats(0.75)),
    (65, beats(1.0)),
    (62, beats(1))
    ]

motif_b = [
    (62, beats(1)),
    (64, beats(0.25)),
    (65, beats(0.25)),
    (69, beats(0.5)),
    (65, beats(1.0)),
    (62, beats(1))
    ]

motif_bass = [
    (62-12, beats(4)),
    (59-12, beats(4)),
    (60-12, beats(4)),
    (65-12, beats(1)),
    (60-12, beats(3)),
    ]

def gen_intro():
    pes = []
    s = 0
    pes.append(beat_loop.crop(pg.Extent(s, s + beats(5 * 8))).gain(0.25))
    s = beats(8)
    # motif_a lasts 4 beats.  motif_a + mofit_a lasts 8 beats...
    for pitch, n_frames in motif_a + motif_a:
        e = s + n_frames
        freq = ut.pitch_to_freq(pitch+24)
        snip = beat_loop.mono().crop(pg.Extent(s, e))
        snip = pg.SpatialAPE(snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))
        s = e
    s = beats(3 * 8)
    for pitch, n_frames in motif_a + motif_a:
        e = s + n_frames
        freq = ut.pitch_to_freq(pitch+12)
        snip = beat_loop.mono().crop(pg.Extent(s, e))
        snip = pg.SpatialAPE(snip, degree = 45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))
        s = e
    return pg.MixPE(*pes)

def gen_verse_1():
    pes = []
    s = 0
    pes.append(beat_loop.crop(pg.Extent(s, s + beats(2 * 8))).gain(0.25))
    for pitch, n_frames in motif_a + motif_a + motif_a + motif_a:
        e = s + n_frames
        snip = beat_loop.mono().crop(pg.Extent(s, e))

        freq_l = ut.pitch_to_freq(pitch+24)
        snip_l = pg.SpatialAPE(snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip_l, f0=freq_l, q=20))

        freq_r = ut.pitch_to_freq(pitch+12)
        snip_r = pg.SpatialAPE(snip, degree = 45).gain(0.75)
        pes.append(pg.CombPE(snip_r, f0=freq_r, q=20))
        s = e

    s = 0
    for pitch, n_frames in motif_bass:
        e = s + n_frames
        snip = beat_loop.mono().crop(pg.Extent(s, e))
        freq = ut.pitch_to_freq(pitch)
        pes.append(pg.CombPE(snip, f0=freq, q=50).gain(0.5))
        s = e
    return pg.MixPE(*pes)

def gen_verse_2():
    pes = []
    s = 0
    pes.append(beat_loop.crop(pg.Extent(s, s + beats(2 * 8))).gain(0.25))
    for pitch, n_frames in motif_a + motif_a + motif_a + motif_a:
        e = s + n_frames
        beat_snip = beat_loop.mono().crop(pg.Extent(s, e))

        freq = ut.pitch_to_freq(pitch+24)
        snip = pg.SpatialAPE(beat_snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+12)
        snip = pg.SpatialAPE(beat_snip, degree = 45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+24+2)
        snip = pg.SpatialAPE(beat_snip, degree = 85).gain(0.85)
        pes.append(pg.CombPE(snip, f0=freq, q=40))

        freq = ut.pitch_to_freq(pitch+12+7)
        snip = pg.SpatialAPE(beat_snip, degree = -75).gain(0.80)
        pes.append(pg.CombPE(snip, f0=freq, q=40))
        s = e

    s = 0
    for pitch, n_frames in motif_bass:
        e = s + n_frames
        snip = beat_loop.mono().crop(pg.Extent(s, e))
        freq_comb = ut.pitch_to_freq(pitch)
        pes.append(pg.CombPE(snip, f0=freq_comb, q=50).gain(0.5))
        # Biquad2PE is generating crackles...need to fix...
        freq_biquad = ut.pitch_to_freq(pitch-12)
        # pes.append(pg.Biquad2PE(snip.gain(0.1), f0=freq_biquad, q=50))
        s = e

    return pg.MixPE(*pes)

def gen_verse_3():
    pes = []
    s = 0
    pes.append(beat_loop.crop(pg.Extent(s, s + beats(2 * 8))).gain(0.25))
    for pitch, n_frames in motif_a + motif_a + motif_a + motif_a:
        e = s + n_frames
        beat_snip = beat_loop.mono().crop(pg.Extent(s, e))

        freq = ut.pitch_to_freq(pitch+24)
        snip = pg.SpatialAPE(beat_snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+12)
        snip = pg.SpatialAPE(beat_snip, degree = 45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+24+2)
        snip = pg.SpatialAPE(beat_snip, degree = 85).gain(0.85).delay(beats(0.25))
        pes.append(pg.CombPE(snip, f0=freq, q=40))

        freq = ut.pitch_to_freq(pitch+12+7)
        snip = pg.SpatialAPE(beat_snip, degree = -75).gain(0.80).delay(beats(0.25))
        pes.append(pg.CombPE(snip, f0=freq, q=40))
        s = e

    s = 0
    for pitch, n_frames in motif_bass:
        e = s + n_frames
        snip = beat_loop.mono().crop(pg.Extent(s, e))
        freq_comb = ut.pitch_to_freq(pitch)
        pes.append(pg.CombPE(snip, f0=freq_comb, q=50).gain(0.5))
        # Biquad2PE is generating crackles...need to fix...
        freq_biquad = ut.pitch_to_freq(pitch-12)
        # pes.append(pg.Biquad2PE(snip.gain(0.1), f0=freq_biquad, q=50))
        s = e

    return pg.MixPE(*pes)

## TODO: flange only the pitched components, not the pure drums
def gen_verse_4():
    v3 = gen_verse_3()
    pes = []
    pes.append(v3)
    timeline = pg.MixPE(pg.IdentityPE(channel_count=1), 
                        pg.SinPE(frequency=0.125, amplitude=50, channel_count=1))
    timeline = timeline.crop(pg.Extent(0, beats(16)))
    warped = pg.TimewarpPE(v3, timeline)
    pes.append(warped)
    return pg.MixPE(*pes)

def gen_verse_4():
    # regenerate just the pitched components
    pes = []
    s = 0
    for pitch, n_frames in motif_a + motif_a + motif_a + motif_a:
        e = s + n_frames
        beat_snip = beat_loop.mono().crop(pg.Extent(s, e))

        freq = ut.pitch_to_freq(pitch+24)
        snip = pg.SpatialAPE(beat_snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+12)
        snip = pg.SpatialAPE(beat_snip, degree = 45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+24+2)
        snip = pg.SpatialAPE(beat_snip, degree = 85).gain(0.85).delay(beats(0.25))
        pes.append(pg.CombPE(snip, f0=freq, q=40))

        freq = ut.pitch_to_freq(pitch+12+7)
        snip = pg.SpatialAPE(beat_snip, degree = -75).gain(0.80).delay(beats(0.25))
        pes.append(pg.CombPE(snip, f0=freq, q=40))
        s = e

    s = 0
    for pitch, n_frames in motif_bass:
        e = s + n_frames
        snip = beat_loop.mono().crop(pg.Extent(s, e))
        freq_comb = ut.pitch_to_freq(pitch)
        pes.append(pg.CombPE(snip, f0=freq_comb, q=50).gain(0.5))
        # Biquad2PE is generating crackles...need to fix...
        freq_biquad = ut.pitch_to_freq(pitch-12)
        # pes.append(pg.Biquad2PE(snip.gain(0.1), f0=freq_biquad, q=50))
        s = e

    # flange all the pitched components
    pitched_pes = pg.MixPE(*pes)
    timeline = pg.MixPE(pg.IdentityPE(channel_count=1), 
                        pg.SinPE(frequency=1.0, amplitude=100, channel_count=1))
    timeline = timeline.crop(pg.Extent(0, beats(16)))
    warped_pes = pg.TimewarpPE(pitched_pes, timeline)
    # mix plain, flanged and original drum track
    return pg.MixPE(
        pitched_pes.gain(0.85),
        warped_pes.gain(0.85),
        beat_loop.crop(pg.Extent(0, beats(2 * 8))).gain(0.25)
        )

def gen_outro():
    v3 = gen_verse_3()
    pes = []
    s = 0
    outro_snip = v3.crop(pg.Extent(beats(15.75))).delay(beats(-15.75))
    dt = 0.25
    g = 1.0
    for i in range(13):
        pes.append(outro_snip.delay(beats(s)).gain(g))
        g = g * 0.85
        dt += 0.08
        s += dt
    return pg.MixPE(*pes)

# bridge_snip = beat_loop.crop(pg.Extent(beats(15.75), beats(16))).delay(
#     beats(-15.75)
# )

# bridge = pg.MixPE(  # beats 80-96
#     middle_8_beat.crop(pg.Extent(int(0), beats(16))).gain(0.4),
#     combify(middle_8_motif).gain(0.8),
# )


mix = pg.MixPE(
    gen_fade_in().delay(beats(0)),
    gen_intro().delay(beats(16)),
    gen_verse_1().delay(beats(56)),
    gen_verse_2().delay(beats(72)),
    # bridge goes here...
    gen_verse_3().delay(beats(88)),
    gen_verse_4().delay(beats(104)),
    gen_outro().delay(beats(120)),
    )

# For testing the individual sections in isolation, uncomment one at a time.
# mix = gen_fade_in()
# mix = gen_intro()
# mix = gen_verse_1() 
# mix = gen_verse_2() 
# mix = gen_verse_3() 
# mix = gen_verse_4()
# mix = gen_outro()
dst = pg.WavWriterPE(mix, "examples/wip_RD03.wav")
pg.FtsTransport(dst).play()

pg.Transport(pg.WavReaderPE("examples/wip_RD03.wav")).play()
