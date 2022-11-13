import pygmu as pg

def seq(filename, at_frame, amp):
    wav = pg.WavReaderPE(filename)
    # return the wav file, delayed by at_frame and attenuated by amp
    return pg.DelayPE(pg.MulPE(wav, pg.ConstPE(amp)), int(at_frame))

one_bar = 89576 / 4
thump_offset = 3690
yeah_offset = 7904

mix = pg.MixPE(
    seq("../samples/Fox48.wav", 0 * one_bar, 0.05),
    seq("../samples/s06.wav", 1 * one_bar - thump_offset, 0.5),
    seq("../samples/14_yeah_f.wav", 3 * one_bar - yeah_offset, 1.0),
    seq("../samples/Fox48.wav", 4 * one_bar, 0.05),
    seq("../samples/s06.wav", 5 * one_bar - thump_offset, 0.5),
    seq("../samples/14_yeah_f.wav", 7 * one_bar - yeah_offset, 1.0),
    seq("../samples/Fox48.wav", 8 * one_bar, 0.05),
    seq("../samples/s06.wav", 9 * one_bar - thump_offset, 0.5),
    seq("../samples/14_yeah_f.wav", 11 * one_bar - yeah_offset, 1.0),
    seq("../samples/Fox48.wav", 12 * one_bar, 0.05),
    seq("../samples/s06.wav", 13 * one_bar - thump_offset, 0.5),
    seq("../samples/14_yeah_f.wav", 15 * one_bar - yeah_offset, 1.0))


# Start calling render() on the "root" processing element.
pg.Transport().play(mix)
