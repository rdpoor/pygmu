import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import numpy as np
import pygmu as pg
"""
Test TimewarpPE
"""

n_frames = 89576

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

timeline = make_timeline([0, 2, 4, 5])
source = pg.WavReaderPE("samples/Fox48.wav")
pe = pg.TimewarpPE(source, timeline)
pg.Transport(pe).play()
