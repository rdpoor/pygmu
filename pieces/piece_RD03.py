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
beat_loop = beat.loop(int(eight_beat_duration))

FRAME_RATE = beat.frame_rate()

def beats(b):
    return int(b * beat_duration)

middle_8_beat = beat.time_shift(beats(-7)).crop(pg.Extent(0, beats(1))).loop(beats(1))

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
# v5: 16 beats: v4 + (motif, motif+9, motif+12, motif+21).time_shift(0.25)
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
        snip = pg.SpatialPE(snip, degree=pan_degree)
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
    (65-12, beats(2.5)),
    (60-12, beats(1.5)),
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
        snip = beat_loop.crop(pg.Extent(s, e))
        snip = pg.SpatialPE(snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))
        s = e
    s = beats(3 * 8)
    for pitch, n_frames in motif_a + motif_a:
        e = s + n_frames
        freq = ut.pitch_to_freq(pitch+12)
        snip = beat_loop.mono().crop(pg.Extent(s, e))
        snip = pg.SpatialPE(snip, degree = 45).gain(0.75)
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
        snip_l = pg.SpatialPE(snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip_l, f0=freq_l, q=20))

        freq_r = ut.pitch_to_freq(pitch+12)
        snip_r = pg.SpatialPE(snip, degree = 45).gain(0.75)
        pes.append(pg.CombPE(snip_r, f0=freq_r, q=20))
        s = e

    s = 0
    for pitch, n_frames in motif_bass:
        e = s + n_frames
        snip = beat_loop.mono().crop(pg.Extent(s, e))
        freq = ut.pitch_to_freq(pitch)
        snip = pg.CombPE(snip, f0=freq, q=50).gain(0.5)
        pes.append(snip)
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
        snip = pg.SpatialPE(beat_snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+12)
        snip = pg.SpatialPE(beat_snip, degree = 45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+24+2)
        snip = pg.SpatialPE(beat_snip, degree = 85).gain(0.85)
        pes.append(pg.CombPE(snip, f0=freq, q=40))

        freq = ut.pitch_to_freq(pitch+12+7)
        snip = pg.SpatialPE(beat_snip, degree = -75).gain(0.80)
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
        snip = pg.SpatialPE(beat_snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+12)
        snip = pg.SpatialPE(beat_snip, degree = 45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+24+2)
        snip = pg.SpatialPE(beat_snip, degree = 85).gain(0.75).time_shift(beats(0.5))
        pes.append(pg.CombPE(snip, f0=freq, q=40))

        freq = ut.pitch_to_freq(pitch+12+7)
        snip = pg.SpatialPE(beat_snip, degree = -75).gain(0.72).time_shift(beats(0.25))
        pes.append(pg.CombPE(snip, f0=freq, q=40))
        s = e

    s = 0
    for pitch, n_frames in motif_bass:
        e = s + n_frames
        snip = beat_loop.mono().crop(pg.Extent(s, e))
        freq_comb = ut.pitch_to_freq(pitch)
        pes.append(pg.CombPE(snip, f0=freq_comb, q=50).gain(0.5))
        # Biquad2PE is generating crackles...need to fix...
        # freq_biquad = ut.pitch_to_freq(pitch-12)
        # pes.append(pg.Biquad2PE(snip.gain(0.1), f0=freq_biquad, q=50))
        s = e

    return pg.MixPE(*pes)

motif_bridge = [
    (79, beats(1.0)),  # tricky, since orignal sample has two hits
    (79, beats(0.5)),
    (79, beats(1.0)),
    (79, beats(0.5)),
    (79, beats(0.5)),
    (78, beats(0.5)),

    (79, beats(0.5)),
    (79, beats(0.25)),
    (79, beats(0.75)),
    (79, beats(1.0)),
    (79, beats(1.0)),
    (81, beats(0.5)),
    ]


def gen_bridge():
    bridge_snip = beat_loop.time_shift(beats(1))
    pes = []
    s = 0
    for pitch, n_frames in motif_bridge + motif_bridge + motif_bridge + motif_bridge:
        e = s + n_frames
        freq = ut.pitch_to_freq(pitch)
        snip = bridge_snip.crop(pg.Extent(0, n_frames)).time_shift(s).gain(0.5)
        pes.append(pg.CombPE(snip, f0=freq, q=40))
        s = e
    # kick enters partway through the bridge
    s = beats(8)
    for i in range(24):
        kick = beat_loop.crop(pg.Extent(0, beats(0.25))).time_shift(s + beats(i)).gain(0.1)
        pes.append(kick)
    return pg.MixPE(*pes)

BRIDGE_PITCHES = [
    60, 62, 64, 65, 67, 69, 71, 
    72, 74, 76, 77, 79, 81, 83,
    84, 86, 88, 89, 91, 93, 95,
    96, 98, 100, 101, 103, 105, 107,
    108
]

random.seed(14)


def gen_bridge_melody():
    """
    Generate "note ramps".  Each ramp has a starting pitch (p0) and an ending pitch (p1),
    and a fixed duration for each intervening note.

    Main characters:
    s0: starting time of a pitch ramp
    s1: ending time of a pitch ramp
    p0: starting pitch
    p1: ending pitch
    ramp_dur: time it takes to get from s0 to s1
    note_dur: the duration of each note in the ramp
    """
    pes = []
    t0 = 0                   # start time of pitch ramp
    p0 = select_pitch()      # starting pitch of pitch ramp
    while t0 < beats(32-8):
        # ramp_dur = select_ramp_dur()   # choose a duration for this pitch ramp
        ramp_dur = beats(4)
        t1 = min(beats(32-8), t0 + ramp_dur)  # ending time for this pitch ramp
        p1 = select_pitch()  # choose an ending pitch for this pitch ramp
        note_dur = select_note_dur()
        t = t0
        while t < t1:
            u = t/beats(32-8)   # ramp from 0 to 1.  could be useful
            p = ut.lerp(t, t0, t1, p0, p1)
            p = closest(p, BRIDGE_PITCHES)  # filter to permissable pitches
            pes.append(gen_bridge_note(t, p, note_dur, 0.3))
            t += note_dur
        t0 = t1
        p0 = p1
    return pg.MixPE(*pes)

def select_ramp_dur():
    return random.choice([beats(4), beats(2), beats(2), beats(1), beats(1)])

def select_pitch():
    return random.randrange(60, 108)

def select_note_dur():
    return random.choice([beats(1), beats(0.5), beats(0.25), beats(0.125), beats(0.5/3)])

def closest(x, values):
    values = np.asarray(values)
    idx = (np.abs(values - x)).argmin()
    return values[idx]

def gen_bridge_note(at, pitch, duration, legato):
    bridge_snip = beat_loop.time_shift(beats(1))
    freq = ut.pitch_to_freq(pitch)
    # snip = pg.CombPE(bridge_snip, f0=freq, q=180).crop(pg.Extent(0, int(duration * legato)))
    # snip = pg.ReversePE(snip)
    snip = pg.SinPE(frequency=freq, frame_rate=FRAME_RATE).crop(pg.Extent(0, int(duration * legato))).gain(0.1)
    snip = snip.splice(10, 1000)
    snip = snip.time_shift(at)
    degree = ut.lerp(pitch, 60, 108, -90, 90)
    unpanned = pg.SpatialPE(snip, degree=0)
    panned = pg.SpatialPE(snip, degree=degree)
    return pg.MixPE(unpanned.gain(0.4).time_shift(beats(0.2)),
                    panned.gain(0.4))

def gen_verse_4():
    # regenerate just the pitched components
    pes = []
    s = 0
    for pitch, n_frames in motif_a + motif_a + motif_a + motif_a:
        e = s + n_frames
        beat_snip = beat_loop.mono().crop(pg.Extent(s, e))

        freq = ut.pitch_to_freq(pitch+24)
        snip = pg.SpatialPE(beat_snip, degree = -45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+12)
        snip = pg.SpatialPE(beat_snip, degree = 45).gain(0.75)
        pes.append(pg.CombPE(snip, f0=freq, q=20))

        freq = ut.pitch_to_freq(pitch+24+2)
        snip = pg.SpatialPE(beat_snip, degree = 85).gain(0.75).time_shift(beats(0.5))
        pes.append(pg.CombPE(snip, f0=freq, q=40))

        freq = ut.pitch_to_freq(pitch+12+7)
        snip = pg.SpatialPE(beat_snip, degree = -75).gain(0.72).time_shift(beats(0.25))
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
    timeline = pg.MixPE(pg.IdentityPE(), 
                        pg.SinPE(frequency=1.0, amplitude=100, frame_rate=FRAME_RATE))
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
    # add one kick on the downbeat of the outro
    kick = beat_loop.crop(pg.Extent(0, beats(0.5))).gain(0.3)
    pes.append(kick)
    # "clock running down" effect with increasing delay and decreasing gain
    # use the last sixteenth note of the previous section as the snip to
    # repeat.  Note that we delay it by -15.75 so it (now) starts at t=0.
    outro_snip = v3.crop(pg.Extent(beats(15.75))).time_shift(beats(-15.75))
    s = 0       # initial snip start time
    dt = 0.25   # initial inter-snip delay 
    g = 1.0     # initial snip gain
    for i in range(17):
        # add snip to the sequence of snips...
        pes.append(outro_snip.time_shift(beats(s)).gain(g))
        g = g * 0.8   # decrease gain
        dt += 0.07    # increase delay
        s += dt       # start time of next snip
    return pg.MixPE(*pes)

mix = pg.MixPE(
    gen_fade_in().time_shift(beats(0)),
    gen_intro().time_shift(beats(16)),
    gen_verse_1().time_shift(beats(56)),
    gen_verse_2().time_shift(beats(72)),
    gen_verse_3().time_shift(beats(88)),
    gen_bridge().time_shift(beats(104)),
    gen_bridge_melody().time_shift(beats(104+8)),
    gen_verse_4().time_shift(beats(136)),
    gen_verse_4().time_shift(beats(152)),
    gen_outro().time_shift(beats(168)),
    )

# For testing the individual sections in isolation, uncomment one at a time.
# mix = gen_fade_in()
# mix = gen_intro()
# mix = gen_verse_1() 
# mix = gen_verse_2() 
# mix = gen_verse_3() 
# mix = gen_bridge()
# mix = gen_bridge_melody()
# mix = pg.MixPE(gen_bridge(), gen_bridge_melody().time_shift(beats(8)))
# mix = gen_verse_4()
# mix = gen_outro()
print("mix.extent() =", mix.extent())
filename = "examples/piece_RD03v2.wav"
dst = pg.WavWriterPE(mix, filename)
pg.FtsTransport(dst).play()

pg.Transport(pg.WavReaderPE(filename)).play()
