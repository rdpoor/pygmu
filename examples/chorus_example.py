
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

DURATION_SECS = 15

src = pg.WavReaderPE("/Users/andy/Dev/gitlab/nudoh/disrupterbox/apps/golden/live_coding/pygmu/samples/music/TamperFrame_TooGoodToBeTrue_Edit.wav").crop(pg.Extent(0, 480000))

# rate=1.5, depth=0.5, mix=0.5
chorused = pg.ChorusPE(src.gain(0.2), rate=0.2, depth=0.27, mix=0.3).gain(3)

# Render 1 second of audio
pg.Transport(chorused).play()
