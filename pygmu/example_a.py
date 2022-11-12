import pygmu as pg

freq_f = 174.614
freq_b = 246.942
freq_ds = 311.127
freq_gs = 415.305

# Start calling render() on the "root" processing element.
sin_pe = pg.SinPE(frequency = freq_f, amplitude = 0.2)
pg.Transport().play(sin_pe)
