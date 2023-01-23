import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test MapPE.  Use MapPE to create a limiter: Audio is first boosted by
input_gain db, then any audio louder than out_limit is limited to that
value.
"""

input_gain = 60
out_limit = -10

def limiter_fn(db_in):
    db_out = db_in + input_gain            # add gain to input
    limited = np.where(db_out > out_limit) # anywhere out_db > out_limit...
    db_out[limited] = out_limit            # ... clamp to out_limit
    return db_out - db_in                  # convert gain

# source = pg.WavReaderPE("samples/BellyOfAnArchitect_Clip01.wav")
# source = pg.WavReaderPE("samples/BigBeat4_BigBeat5drumloops120bpm.04.wav")
# source = pg.WavReaderPE("samples/F9THbass90bpmDmin.wav")
source = pg.WavReaderPE("samples/PrettyGirl_Gleason.wav")
env_db = pg.EnvDetectPE(source.mono(), attack=0.9999, release=0.5, units='db')
gain_db = pg.MapPE(env_db, limiter_fn)
limited = pg.GainPE(source, gain_db, units='db')
pg.Transport(limited).play()

