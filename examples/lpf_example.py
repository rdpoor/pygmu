
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("/Users/andy/Dev/gitlab/nudoh/disrupterbox/apps/golden/live_coding/pygmu/samples/music/TamperFrame_TooGoodToBeTrue_Edit.wav").crop(pg.Extent(0, 150000))

FRAME_RATE = 48000
DURATION_SECS = 15

def stof(seconds):
    '''Convert seconds to frames (samples)'''
    return int(seconds * FRAME_RATE)

frame_rate = 48000

# rate=1.5, depth=0.5, mix=0.5
filtered = src.gain(0.5).mono().lowpass(900, 3)

# Render 1 second of audio
pg.Transport(filtered).play()
