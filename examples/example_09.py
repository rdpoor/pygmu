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

n_frames = 89576 / 4

semitone = pow(2.0, 1/12)

def make_timeline(pitches):
    timeline = np.ndarray([0, 1], dtype=np.float32)
    start_frame = 0
    for p in pitches:
        freq = semitone**p
        ramp_dur = int(n_frames / freq)
        ramp = pg.utils.ramp_frames(0, n_frames, ramp_dur, 1)
        timeline = np.concatenate((timeline, ramp))
    return pg.ArrayPE(timeline, channel_count=1)

print("hit return after each example to hear the next")

# plain warping
timeline = pg.MixPE(pg.IdentityPE(channel_count = 1), pg.SinPE(frequency=4, amplitude=100.0, channel_count=1))
source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
warped = pg.TimewarpPE(source, timeline)
pg.Transport(warped).play()

# mixing with original == flanging
timeline = pg.MixPE(pg.IdentityPE(channel_count = 1), pg.SinPE(frequency=0.5, amplitude=200.0, channel_count=1))
source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
warped = pg.TimewarpPE(source, timeline)
pg.Transport(pg.MixPE(source, warped)).play()

# just being silly...
timeline = make_timeline([0, 2, 4, 5, 7, 9, 11, 12, 12, 12, 12])
source = pg.WavReaderPE("samples/Fox48.wav")
pe = pg.TimewarpPE(source, timeline)
pg.Transport(pe).play()

