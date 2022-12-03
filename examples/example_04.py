import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

def seq(filename, at_frame, amp):
    wav = pg.WavReaderPE(filename)
    # return the wav file, delayed by at_frame and attenuated by amp
    return pg.DelayPE(pg.MulPE(wav, pg.ConstPE(amp)), int(at_frame))

q = 89576 / 4     # quarter note duration
mew_offset = 3000
thump_offset = 3690
yeah_offset = 7904

mix = pg.MixPE(
    seq("samples/Fox48.wav", 0 * q, 0.4),
    seq("samples/s06_stereo.wav", 1 * q - thump_offset, 0.5),
    seq("samples/Mew.wav", 3 * q - mew_offset, 1.5),
    seq("samples/Fox48.wav", 4 * q, 0.4),
    seq("samples/s06_stereo.wav", 5 * q - thump_offset, 0.5),
    seq("samples/14_yeah_f.wav", 7 * q - yeah_offset, 1.0),
    seq("samples/Fox48.wav", 8 * q, 0.4),
    seq("samples/s06_stereo.wav", 9 * q - thump_offset, 0.5),
    seq("samples/Mew.wav", 11 * q - mew_offset, 1.5),
    seq("samples/Fox48.wav", 12 * q, 0.4),
    seq("samples/s06_stereo.wav", 13 * q - thump_offset, 0.5),
    seq("samples/14_yeah_f.wav", 15 * q - yeah_offset, 1.0),
    seq("samples/s06_stereo.wav", 17 * q - thump_offset, 0.5))


# Start calling render() on the "root" processing element.
pg.Transport(mix).play()
