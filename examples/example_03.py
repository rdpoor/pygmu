import pygmu as pg

def trem_sin_at(at_s, freq_hz, trem_freq, amp):
    """
    example_02 with different tremolo on each note
    """
    # Create a rectified sine generator with given frequency and ampltude
    sin_osc = pg.AbsPE(pg.SinPE(frequency = freq_hz, amplitude = amp))
    # Create a tremolo oscillator.
    tremolo = pg.SinPE(frequency = trem_freq, amplitude = 1.0)
    # multiply the two
    trem_osc = pg.MulPE(sin_osc, tremolo)
    # Crop the output to start and the given time, but last forever...
    return pg.CropPE(trem_osc, pg.Extent(int(sin_osc.frame_rate() * at_s)))

freq_f = 174.614 / 2
freq_b = 246.942  / 2
freq_ds = 311.127 / 2
freq_gs = 415.305 / 2

# Mix the output of four sinewaves, each with its own frequency and start time.
vib_tristan = pg.MixPE(
    trem_sin_at(0.5, freq_f, 1.9, 0.2),
    trem_sin_at(1.0, freq_b, 2.5, 0.2),
    trem_sin_at(1.5, freq_ds, 3.1, 0.2),
    trem_sin_at(2.0, freq_gs, 3.6, 0.2))

# Start calling render() on the "root" processing element.
pg.Transport(vib_tristan).play()
