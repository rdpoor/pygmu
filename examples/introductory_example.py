# This bit of boilerplate allows Python to find the pygmu library
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

SRATE = 48000  # Define the frame rate for the piece.

def s_to_f(seconds):
    '''Convert seconds to frames (samples)'''
    return int(seconds * SRATE)

def generate_note(start_time, duration, hz, amp):
    """
    Return a Processing Element such that when you call render(), it produces
    a tone at the desired time with a given duration, frequency and amplitude.
    """
    # Use an Extent to define the start and end times of the note
    extent = pg.Extent(s_to_f(start_time), s_to_f(start_time + duration))

    # We use a BlitSaw (bandwidth limited sawtooth wave generator) to generate 
    # the tone, passing its output through a gain stage to adjust the amplitude 
    # and then through a "CropPE" to specify the start and end times.

    # We could chain together the processing elements like this...
    # saw_pe = pg.BlitSawPE(frequency=hz, frame_rate=SRATE)
    # saw_pe = pg.GainPE(saw_pe, amp)          # Adjust the amplitude
    # saw_pe = pg.CropPE(saw_pe, extent)       # Crop start and end times
    # return saw_pe                            # Return the result

    # ... but PygMu provides shorthand chaining methods for many common
    # functions, so you can write the whole thing in one line if you prefer:
    return pg.BlitSawPE(frequency=hz, frame_rate=SRATE).gain(amp).crop(extent)

# Mix the output of four tones to Generate Wagner's famous opening chord.
# Note that we use the `utils` module's `pitch_to_freq()` functon to convert
# MIDI style pitch numbers to frequencies.  
tristan = pg.MixPE(
    generate_note(0.5, 4.5, ut.pitch_to_freq(53), 0.2),
    generate_note(1.0, 4.0, ut.pitch_to_freq(59), 0.2),
    generate_note(1.5, 3.5, ut.pitch_to_freq(63), 0.2),
    generate_note(2.0, 3.0, ut.pitch_to_freq(68), 0.2))

# At this point, we have defined HOW the final piece will be generated, but it 
# hasn't been generated yet.  The Transport `play()` method will repeatedly call
# `tristan.render()` to request samples, sending the result to the DAC on your
# computer.
pg.Transport(tristan).play()
