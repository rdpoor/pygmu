
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

FRAME_RATE = 48000
DURATION_SECS = 25

def stof(seconds):
    '''Convert seconds to frames (samples)'''
    return int(seconds * FRAME_RATE)

frame_rate = 48000
extent = pg.Extent(0, stof(DURATION_SECS))

vibrato_rate = 20
vibrato_width = 60
center_freq = 440

<<<<<<< HEAD
freq1 = pg.SinPE(vibrato_rate, frame_rate=FRAME_RATE).gain(vibrato_width)
freq2 = pg.SinPE(vibrato_rate * 1.617, frame_rate=FRAME_RATE).gain(vibrato_width)
freq3 = pg.SinPE(vibrato_rate * 0.89, frame_rate=FRAME_RATE).gain(vibrato_width / 2)
freq4 = pg.ConstPE(center_freq).add(freq1).add(freq2).add(freq3)
=======

freq1 = pg.SinPE(vibrato_rate, frame_rate=FRAME_RATE).gain(vibrato_width).add(440)
freq2 = pg.SinPE(vibrato_rate * 1.617, frame_rate=FRAME_RATE).gain(vibrato_width)
freq3 = pg.SinPE(vibrato_rate * 0.89, frame_rate=FRAME_RATE).gain(vibrato_width / 2)
#freq4 = pg.ConstPE(center_freq).add(freq1).add(freq2).add(freq3)
freq4 = freq3.add(freq1).add(freq2)
>>>>>>> 9265530 (Replace FrequencyMixin with general purpose DynamicParameterMixin, and update sin_pe and blit_saw_pe accordingly.)

sine_osc = pg.SinPE(freq4, frame_rate=FRAME_RATE).crop(extent, 500)

# Render 1 second of audio
pg.Transport(sine_osc).play()
