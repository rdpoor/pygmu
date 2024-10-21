import os
import sys
import numpy as np

# Boilerplate to find the pygmu library
script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, '..', 'pygmu')
sys.path.append(pygmu_dir)

import pygmu as pg


SRATE = 48000

def s_to_f(seconds):
    return int(seconds * SRATE)

def dynamic_pan(pe, start_pan, end_pan):
    extent = pg.Extent(0, 10000)
    pan_values = np.linspace(start_pan, end_pan, extent.end() - extent.start())
    return pg.MapPE(pe, lambda frames: frames * pan_values[:, np.newaxis])

def convolution_reverb(input_pe, ir_file):
    ir_pe = pg.WavReaderPE(ir_file)
    ir_frames = ir_pe.render(pg.Extent(0, ir_pe.duration()))

    def convolution_function(frames):
        output = np.convolve(frames[0], ir_frames[0], mode='full')
        return np.array([output[:len(frames[0])]])

    return pg.MapPE(input_pe, convolution_function)

# Input audio file
input_pe = pg.WavReaderPE("input.wav")

# Apply spatial panning and delay
panned_output = dynamic_pan(input_pe, 0.0, 1.0)
delayed_output = pg.DelayPE(panned_output, delay_time=s_to_f(0.5), feedback=0.7)

# Apply convolution reverb with impulse response
reverb_output = convolution_reverb(delayed_output, "impulse_response.wav")

# Play the generated complex audio effect
pg.Transport(reverb_output).play()
