import pygmu as pg

freq_f = 174.614
freq_b = 246.942
freq_ds = 311.127
freq_gs = 415.305

# Start calling render() on the "root" processing element.
sin_pe = pg.SinPE(frequency = freq_f, amplitude = 0.2)
crop_pe = pg.CropPE(sin_pe, pg.Extent(int(pg.Transport.FRAME_RATE * 5.5)))
pg.Transport().play(crop_pe)
