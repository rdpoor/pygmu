import pygmu as pg

def sin_at(at_s, freq_hz, amp):
    """
    Cartoon sounding version of example_01, using AbsPE to rectify sine tones.
    """
    # Create a sine generator with given frequency and ampltude
    sin = pg.SinPE(frequency = freq_hz, amplitude = amp)
    # Crop the output to start and the given time, but last forever...
    return pg.AbsPE(pg.CropPE(sin, pg.Extent(int(pg.Transport.FRAME_RATE * at_s))))

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
pg.Transport().play(tristan)
