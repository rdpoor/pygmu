import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

FRAME_RATE = 48000

def sin_at(at_s, freq_hz, amp):
    """
    Play a sine tone starting at the given # of seconds.  More accurately:
    Create a Processing Element such that when you call render(), it produces
    a sine tone.

    This function is intended to show that it is easy to compose different PEs
    together to create more complex (or more bespoke) functions.
    """
    # Create a sine generator with given frequency and ampltude
    sin = pg.SinPE(frequency = freq_hz, amplitude = amp, frame_rate=FRAME_RATE)
    # Crop the output to start and the given time, but last forever...
    return pg.CropPE(sin, pg.Extent(int(sin.frame_rate() * at_s)))

freq_f = 174.614
freq_b = 246.942
freq_ds = 311.127
freq_gs = 415.305

# Mix the output of four sinewaves, each with its own frequency and start time.
tristan = pg.MixPE(
    sin_at(0.5, freq_f, 0.2),
    sin_at(1.0, freq_b, 0.2),
    sin_at(1.5, freq_ds, 0.2),
    sin_at(2.0, freq_gs, 0.2))

# Start calling render() on the "root" processing element.
pg.Transport(tristan).play()
