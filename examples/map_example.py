import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test MapPE
"""

thresh = 30

# Anything quieter than thresh db is boosted by thresh db.
# Anything louder gets a reverse compression ratio (expansion)
def compression_fn(frames):
	# print("Min:", np.min(frames), "Max:", np.max(frames))
	# start with a function: f(db) = db + 20
	compressed_db = frames.copy() + thresh
	# any input > -20 gets a slope of -1
	inverted = np.where(compressed_db > -thresh)
	compressed_db[inverted] = thresh - compressed_db[inverted]
	return compressed_db

source = pg.WavReaderPE("samples/BellyOfAnArchitect_Clip01.wav")
source = pg.WavReaderPE("samples/F9THbass90bpmDmin.wav")
source = pg.WavReaderPE("samples/PrettyGirl_Gleason.wav")
# source = pg.WavReaderPE("samples/BigBeat4_BigBeat5drumloops120bpm.04.wav")
env_db = pg.EnvDetectDbPE(source.mono(), attack=0.9999, release=0.3)
gain_db = pg.MapPE(env_db, compression_fn)
compressed = pg.GainDbPE(source, gain_db)
pg.Transport(compressed).play()

