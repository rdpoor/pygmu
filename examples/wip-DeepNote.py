import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

"""
>> "I set up some synthesis programs for the ASP that made it behave like a huge
    digital music synthesizer. I used the waveform from a digitized cello tone
    as the basis waveform for the oscillators. I recall that it had 12
    harmonics. I could get about 30 oscillators running in real-time on the
    device. Then I wrote the "score" for the piece.
>> "The score consists of a C program of about 20,000 lines of code. The output
    of this program is not the sound itself, but is the sequence of parameters
    that drives the oscillators on the ASP. That 20,000 lines of code produce
    about 250,000 lines of statements of the form "set frequency of oscillator
    X to Y Hertz".
>> "The oscillators were not simple - they had 1-pole smoothers on both
    amplitude and frequency. At the beginning, they form a cluster from 200 to
    400 Hz. I randomly assigned and poked the frequencies so they drifted up
    and down in that range. At a certain time (where the producer assured me
    that the THX logo would start to come into view), I jammed the frequencies
    of the final chord into the smoothers and set the smoothing time for the
    time that I was told it would take for the logo to completely materialize
    on the screen. At the time the logo was supposed to be in full view, I set
    the smoothing times down to very low values so the frequencies would
    converge to the frequencies of the big chord (which had been typed in by
    hand - based on a 150-Hz root), but not converge so precisely that I would
    lose all the beats between oscillators. All followed by the fade-out. It
    took about 4 days to program and debug the thing. The sound was produced
    entirely in real-time on the ASP.

https://www.youtube.com/watch?v=uYMpMcmpfkI
https://www.youtube.com/watch?v=FLMLPuO_H8w
https://www.youtube.com/watch?v=014NtrT-Qhg
https://youtu.be/QYU8zydUqD8?t=44
https://www.youtube.com/watch?v=sPY3Y2qhyXk (not as good?)
https://www.thx.com/wp-content/uploads/2020/03/Deepnote-Panel-A-1024x490.jpg (score)

          seq -> theta -v
 seq -> freq -v         |
             blit. => spatial => mix() => gain


"""

FRAME_RATE = 48000
PIECE_DURATION = 28.0 # seconds

N_HARMONICS = 12   # number of harmonics in each BlitsigPE

TONIC = 50.2         # midi style pitch: not quite 150 Hz, not quite D...
PITCH_EPSILON = 0.1  # how close we get to our target pitch

FINAL_PITCHES = [
	TONIC-24, TONIC-24, TONIC-24, TONIC-24, 
	TONIC-12, TONIC-12, TONIC-12, TONIC-12, 
	TONIC-5, TONIC-5, 
	TONIC, TONIC, TONIC, TONIC, 
	TONIC+7, TONIC+7, TONIC+7, TONIC+7, 
	TONIC+12, TONIC+12, 
	TONIC+19, TONIC+19, 
	TONIC+24, TONIC+24, 
	TONIC+31, TONIC+31,  
	TONIC+36, TONIC+36]

N_OSCILLATORS = len(FINAL_PITCHES)

AMPLITUDE_BPTS = [[0.0, 0.0], [12.0, 1.0], [20.0, 1.0], [PIECE_DURATION, 0.0]]
# DAMPING_BPTS = [[0.0, 0.5*DS], [8.0, 3.0], [16.0, 2.0], [20.0, 1.0]]
# OBEDIENCE_BPTS = [[0.0, 0.0], [8.0, 0.0], [16.0, 1.0], [28.0, 1.0]]

# Create SequencePE, converting seconds to frames
AMPLITUDE_PE = pg.SequencePE([[t*FRAME_RATE, v] for t, v in AMPLITUDE_BPTS])
# DAMPING_PE = SequencePE([[t*FRAME_RATE, v] for t, v in DAMPING_BPTS])
# OBEDIENCE_PE = SequencePE([[t*FRAME_RATE, v] for t, v in OBEDIENCE_BPTS])

RNG = np.random.default_rng()

def semitones_per_second(seconds):
	"""
	Return semitones per second glissando as a function of time.
	"""
	if seconds < 8.0:
		return ut.lerp(seconds, 0, 8, 0.5, 3.0)
	elif seconds < 16.0:
		return ut.lerp(seconds, 8, 16, 3.0, 2.0)
	elif seconds < PIECE_DURATION:
		return ut.lerp(seconds, 16, 28, 2.0, 1.0)
	else:
		return 1.0

def obedience_fn(seconds):
	"""
	Return how closely pitch must hew to the final frequency as a function of
	time.
	"""
	if seconds < 8.0:
		return 0.0
	elif seconds < 16.0:
		return ut.lerp(seconds, 8.0, 16.0, 0.0, 1.0)
	else:
		return 1.0

RND_PITCH_LO = ut.ftom(200)
RND_PITCH_HI = ut.ftom(400)

def pick_random_pitch():
	return RNG.uniform(RND_PITCH_LO, RND_PITCH_HI)

def choose_target_pitch(seconds, final_pitch):
	"""
	If obedience_fn(seconds) == 0, return a random pitch between 200 and 400 hz.
	If obedience_fn(seconds) == 1.0, return final_pitch +/- PITCH_EPSILON.
	For intermediate values of obedience, imterpolate between the two.
	"""
	pitch_a = RNG.uniform(ut.ftom(200), ut.ftom(400))
	pitch_b = final_pitch + RNG.uniform(-PITCH_EPSILON, PITCH_EPSILON)
	obedience = obedience_fn(seconds)
	return pitch_a * (1 - obedience) + final_pitch * obedience


DT = 0.05

def gen_pitch_sequence(final_pitch):
	target_pitch = pick_random_pitch()
	current_pitch = target_pitch
	t = 0
	bpts = [[t, current_pitch]]

	while t <= PIECE_DURATION:
		if abs(target_pitch - current_pitch) < PITCH_EPSILON:
			# current pitch has arrived (near) target_pitch: 
			random_pitch = pick_random_pitch()

		# obedience of 0 => use the randomly chosen pitch.
		# obedience of 1 => use final pitch
		# otherwise interpolate between random and final pitch
		obedience = obedience_fn(t)
		target_pitch = random_pitch * (1 - obedience) + final_pitch * obedience

		# move current pitch towards target pitch at a rate determined by
		# damping_fn(t) [semitones per second]
		damping = semitones_per_second(t) * DT
		current_pitch = current_pitch * (1.0 - damping) + target_pitch * damping

		t += DT
		# print(f'{t:.2f} {current_pitch:.2f} {target_pitch:.2f} {obedience:.2f} {damping:.2f}')
		bpts.append([t, current_pitch])
		if obedience == 1.0 and abs(current_pitch-final_pitch) < 0.1:
			break

	return pg.SequencePE([[t*FRAME_RATE, ut.mtof(v)] for t, v in bpts])

def gen_note(final_pitch):
	freq_pe = gen_pitch_sequence(final_pitch)
	blit_pe = pg.BlitSigPE(frequency=freq_pe, 12, channel_count=1, frame_rate=FRAME_RATE)
	return blit_pe

def 
gen_pitch_sequence(25)

