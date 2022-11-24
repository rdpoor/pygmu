import pygmu as pg

n_frames = 6 * 48000
ramp_fast = int(n_frames / 12)
ramp_slow = int(n_frames - ramp_fast)

dur = pg.Extent(0, n_frames)
ahs = pg.WavReaderPE("../samples/TamperClip38.wav").crop(dur).tralfam().envelope(ramp_fast, ramp_slow)
ohs = pg.WavReaderPE("../samples/Tamper_MagnifyingFrame1.wav").crop(dur).tralfam().envelope(ramp_slow, ramp_fast)
pg.MixPE(ahs, ohs).play()
