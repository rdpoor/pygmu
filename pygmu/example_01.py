import pygmu as pg

def sin_at(at_s, freq_hz, amp):
    """
    Play a sine tone starting at the given # of seconds.
    """
    sin = pg.SinPE(frequency = freq_hz, amplitude = amp)
    return pg.CropPE(sin, pg.Extent(int(pg.Transport.FRAME_RATE * at_s)))

freq_f = 174.614
freq_b = 246.942
freq_ds = 311.127
freq_gs = 415.305

tristan = pg.MixPE(
    sin_at(0.5, freq_f, 0.2),
    sin_at(1.0, freq_b, 0.2),
    sin_at(1.5, freq_ds, 0.2),
    sin_at(2.0, freq_gs, 0.2))

pg.Transport().play(tristan)
