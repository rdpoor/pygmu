import pygmu as pg

freq_f = 174.614
freq_b = 246.942
freq_ds = 311.127
freq_gs = 415.305

sin_f = pg.CropPE(pg.SinPE(frequency = freq_f, amplitude = 0.2),
    pg.Extent(int(pg.Transport.FRAME_RATE * 0.5)))
sin_b = pg.CropPE(pg.SinPE(frequency = freq_b, amplitude = 0.2),
    pg.Extent(int(pg.Transport.FRAME_RATE * 1.0)))
sin_ds = pg.CropPE(pg.SinPE(frequency = freq_ds, amplitude = 0.2),
    pg.Extent(int(pg.Transport.FRAME_RATE * 1.5)))
sin_gs = pg.CropPE(pg.SinPE(frequency = freq_gs, amplitude = 0.2),
    pg.Extent(int(pg.Transport.FRAME_RATE * 2.0)))

tristan = pg.MixPE(sin_f, sin_b, sin_ds, sin_gs)

pg.Transport().play(tristan)
