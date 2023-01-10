import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test BiquadPE
"""

src = pg.NoisePE(gain=0.5, channel_count=1).crop(pg.Extent(0,5*44100))

# constant f0, constant Q
# gain_db is ignored for lowpass
flt = pg.BiquadPE(src, 0.0, 330.0, 40, "lowpass")
dst = pg.WavWriterPE(flt, "test.wav")
pg.FtsTransport(dst).play()
pg.Transport(pg.WavReaderPE("test.wav")).play()

# After the noise source stops, you can hear how long this resonates!
flt = pg.BiquadPE(src.gain(0.05), 60.0, 330.0, 10, "peak")
dst = pg.WavWriterPE(flt, "test.wav")
pg.FtsTransport(dst).play()
pg.Transport(pg.WavReaderPE("test.wav")).play()

# ramped f0, constant Q
f0_ramp = pg.LinearRampPE(220, 440, src.extent())
flt = pg.BiquadPE(src, 0.0, f0_ramp, 40, "lowpass")
dst = pg.WavWriterPE(flt, "test.wav")
pg.FtsTransport(dst).play()
pg.Transport(pg.WavReaderPE("test.wav")).play()

# constant f0, ramped Q
q_ramp = pg.LinearRampPE(1, 20, src.extent())
flt = pg.BiquadPE(src, 0.0, 330.0, q_ramp, "lowpass")
dst = pg.WavWriterPE(flt, "test.wav")
pg.FtsTransport(dst).play()
pg.Transport(pg.WavReaderPE("test.wav")).play()

# mix orig with allpass?  Uninteresting, though it might be an error in impl.
# f0_ramp = pg.LinearRampPE(220, 440, src.extent())
# flt = pg.BiquadPE(src, 0.0, f0_ramp, 40, "allpass")
# mix = pg.MixPE(src, flt)
# dst = pg.WavWriterPE(flt, "test.wav")
# pg.FtsTransport(dst).play()
# pg.Transport(pg.WavReaderPE("test.wav")).play()
