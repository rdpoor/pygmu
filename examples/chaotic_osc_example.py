
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut


FRAME_RATE = 48000
DURATION_SECS = 15

def stof(seconds):
    '''Convert seconds to frames (samples)'''
    return int(seconds * FRAME_RATE)

frame_rate = 48000
extent = pg.Extent(0, stof(DURATION_SECS))

chaotic_osc = pg.ChaoticOscPE(rho=28.0, sigma=30.0, beta=8.0/3.0, scale=0.3).gain(20).add(pg.ConstPE(220))
sine_osc = pg.SinPE(chaotic_osc, frame_rate=frame_rate).crop(extent)

# Render 1 second of audio
pg.Transport(sine_osc).play()
