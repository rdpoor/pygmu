import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test TimewarpPE
"""

SRC_FRAMES = 89576 / 4
FRAME_RATE = 48000
SEMITONE = pow(2.0, 1/12)

def make_timeline(pitches):
    timeline = np.ndarray([1, 0], dtype=np.float32)
    start_frame = 0
    for p in pitches:
        freq = SEMITONE**p
        ramp_dur = int(SRC_FRAMES / freq)
        ramp = np.linspace(0, SRC_FRAMES, ramp_dur, endpoint=False, dtype=np.float32)
        timeline = np.append(timeline, ramp)
    # TODO: ArrayPE should accept 1D array
    return pg.ArrayPE(timeline.reshape(1, -1))

def make_timeline2(mult, nframes=44000):
    timeline = np.tile(np.linspace(0, nframes,mult).reshape(-1, 1), (1, 2))
    return pg.ArrayPE(timeline, channel_count=2)

print("hit return after each example to hear the next")

# plain warping
timeline = pg.MixPE(pg.IdentityPE(), pg.SinPE(frequency=4, amplitude=100.0, frame_rate=FRAME_RATE))
source = pg.WavReaderPE("samples/music/Tamper_MagnifyingFrame1.wav")
warped = pg.TimewarpPE(source, timeline)
pg.Transport(warped).play()

# mixing with original == flanging
timeline = pg.MixPE(pg.IdentityPE(), pg.SinPE(frequency=0.5, amplitude=200.0, frame_rate=FRAME_RATE))
source = pg.WavReaderPE("samples/music/Tamper_MagnifyingFrame1.wav")
warped = pg.TimewarpPE(source, timeline)
pg.Transport(pg.MixPE(source, warped)).play()

# plain interpolation

timeline = pg.IdentityPE().gain(1.5)
warped = pg.TimewarpPE(source, timeline)
pg.Transport(warped).play()

# just being silly...
timeline = make_timeline([0, 2, 4, 5, 7, 9, 11, 12, 12, 12, 12])
source = pg.WavReaderPE("samples/music/Fox48.wav")
pe = pg.TimewarpPE(source, timeline)
pg.Transport(pe).play()
