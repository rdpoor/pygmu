import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

# Apply pulse width modulation to a sound file.  The PWM rate
# starts at 14Hz and slows to 10Hz over the course of the file.
# The duty cycle starts "skinny" (10%) and ends "fat" (100%) 

src = pg.WavReaderPE("samples/music/Tamper_MagnifyingFrame1.wav")
rate_ramp = pg.RampPE(48000/40, 48000/10, src.extent())
duty_ramp = pg.RampPE(0.1, 1.0, src.extent())
pwm = pg.PwmPE(rate_ramp, duty_ramp)

# multiply the pwm signal with the original source before rendering
pg.Transport(pg.MulPE(src, pwm)).play()
