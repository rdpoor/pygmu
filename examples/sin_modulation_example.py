
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

FRAME_RATE = 48000
DURATION_SECS = 5

def stof(seconds):
    '''Convert seconds to frames (samples)'''
    return int(seconds * FRAME_RATE)

frame_rate = 48000
extent = pg.Extent(0, stof(DURATION_SECS))

vibrato_rate = 6.1
vibrato_width = 20
center_freq = 180

tremolo_rate = 11
tremolo_width = 0.55

freq = pg.SinPE(vibrato_rate, frame_rate=FRAME_RATE).gain(vibrato_width).add(pg.ConstPE(center_freq))
amp = pg.SinPE(tremolo_rate, frame_rate=FRAME_RATE).gain(tremolo_width).add(pg.ConstPE(1 - (tremolo_width / 2)))

sine_osc = pg.SinPE(freq, frame_rate=FRAME_RATE).mul(amp).crop(extent, 500)

# Render 1 second of audio
pg.Transport(sine_osc).play()

ut.plot_pes([sine_osc, freq, amp.mul(pg.ConstPE(200))], plot_types=["raw", "spectrogram", "waterfall", "peak"])

