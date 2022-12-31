# This bit of boilerplate allows Python to find the pygmu library
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

def sin_at(at_s, dur_s, freq_hz, amp):
    """
    Play a sine tone starting at the given # of seconds.  More accurately:
    Create a Processing Element such that when you call render(), it produces
    a sine tone.

    This function is intended to show that it is easy to compose different PEs
    together to create more complex (or more bespoke) functions.
    """
    # Exploit Python's support of nested functions
    def s_to_f(seconds):
    	'''Convert seconds to frames (samples)'''
    	return int(seconds * sin_pe.frame_rate())

    # Create a sine generator with given frequency and ampltude
    sin_pe = pg.SinPE(frequency = freq_hz, amplitude = amp)
    # Crop the output to to start and end at the desired times.
    return pg.CropPE(sin_pe, pg.Extent(s_to_f(at_s), s_to_f(at_s + dur_s)))

# Generate Wagner's famous opening chord...
# Mix the output of four sinewaves, each with its own frequency and start time.
mix = pg.MixPE(
    sin_at(0.5, 3.5, ut.pitch_to_freq(53), 0.2),
    sin_at(1.0, 3.0, ut.pitch_to_freq(59), 0.2),
    sin_at(1.5, 2.5, ut.pitch_to_freq(63), 0.2),
    sin_at(2.0, 2.0, ut.pitch_to_freq(68), 0.2))

# Start calling render() on the "mix" processing element to play in real-time
pg.Transport(mix).play()
