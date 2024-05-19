import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut
import numpy as np
import pygmu as pg
import utils as ut

def distortion_function(x):
    return np.tanh(x * 20) / 20

def cubic_distortion_function(x):
    bigx = x * 1
    return (bigx - (bigx ** 3) / 3) / 1

# Define the sample rate
SRATE = 48000

# Convert seconds to frames (samples)
def s_to_f(seconds):
    return int(seconds * SRATE)

src = pg.WavReaderPE("/Users/andy/Dev/gitlab/nudoh/disrupterbox/apps/golden/live_coding/pygmu/samples/music/TamperFrame_TooGoodToBeTrue_Edit.wav").crop(pg.Extent(0, 450000)).exp_lim()
    
# Apply wave shaping with the distortion function
processed = pg.WaveShapePE(src, distortion_function)
processed2 = pg.WaveShapePE(src, cubic_distortion_function)
mosh = pg.MixPE(processed,processed2).exp_lim(0.8)
pg.Transport(mosh).play()

