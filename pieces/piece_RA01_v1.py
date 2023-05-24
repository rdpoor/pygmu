import numpy as np
import os
import sys
import random
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

def monofy(frames):
    # Convert stero frames (2 column, N rows) into mono (one row)
    return np.dot(frames, [[0.5], [0.5]]).reshape(-1)

def sterofy(frames):
    # convert horizontal mono array into stero frames (2 columns, N rows)
    return np.dot(frames.reshape(-1, 1), [[1.0, 1.0]])

def choose_snip():
	ret = random.choice(snips)
	ret.name = retrieve_name(ret)
	return ret
	
def choose_dur():
	return random.choice([0.5,0.5,0.5,0.5,1,1,1,1,1.5,2,3])

def choose_interp():
	return random.choice([0.5,0.75,1,1.5,2])

import inspect

def retrieve_name(var):
        """
        Gets the name of var. Does it from the out most frame inner-wards.
        :param var: variable to get name from.
        :return: string
        """
        for fi in reversed(inspect.stack()):
            names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
            if len(names) > 0:
                return names[0]

n_frames = 89576 / 4
semitone = pow(2.0, 1/12)
def make_timeline(pitches):
    timeline = np.ndarray([0, 1], dtype=np.float32)
    start_frame = 0
    for p in pitches:
        freq = semitone**p
        ramp_dur = int(n_frames / freq)
        ramp = pg.utils.ramp_frames(0, n_frames, ramp_dur, 1)
        timeline = np.concatenate((timeline, ramp))
    return pg.ArrayPE(timeline, channel_count=1)

words = pg.WavReaderPE("samples/spoken/Tamper_TVFrame4_mono.wav")
bass = pg.WavReaderPE("samples/loops/F9THbass90bpmDmin.wav")
drum_bap = pg.WavReaderPE("samples/loops/PED_95_BapBeat_Full_Drums.wav")
swing = pg.WavReaderPE("samples/music/Swing_Hallet.wav")

bpm = 116

# duration of a quarter note
q_note_dur = words.frame_rate() * 60.0 / bpm

b_dur = int(q_note_dur * 16)
w_dur = int(q_note_dur * 4)
h_dur = int(q_note_dur * 2)
q_dur = int(q_note_dur)
e_dur = int(q_note_dur / 2)
s_dur = int(q_note_dur / 4)

def beat_to_frame(b):
	return int(b * q_note_dur)

def frame_to_beat(f):
	return float(f / q_note_dur)

def round_to_2(x):
	return round(x, -2)

def snip(pe, s, e, gain=1):
	return pe.crop(pg.Extent(int(s), int(e))).time_shift(int(-s)).gain(gain)

and_the = snip(words, 0, 25208,9)
typical = snip(words, 25208, 55196,6)
mediterranean = snip(words, 56934, 95615,7)
diet = snip(words, 95615, 121257,7)
so_in = snip(words, 128211, 153853,7)
so = snip(words, 135599, 144726,7)
in_ = snip(words, 147728, 154365,9)
crease = snip(words, 154299, 169406,5)
your = snip(words, 169406, 177700,7)
crease_your = snip(words, 153961, 176344,7)
intake_of = snip(words, 176670, 206441,7)
olive_oil = snip(words, 206767, 244361,5)
fresh = snip(words, 244361, 258051,5)
vegetables = snip(words, 258051, 294450,5)

began = snip(swing,1362656,1416044)
troubled = snip(swing,1606714,1639753)
mars = snip(swing,1775000,1802468)
bump = snip(swing,1803422,1820900)
know = snip(swing,2213998,2240056)

bass_a = snip(bass, 0, 103250)
bass_b = snip(bass, 103250, 146752)
bass_c = snip(bass, 146752, 235200)
bass_d = snip(bass, 235200, 308305)
bass_e = snip(bass, 308305, 337908)
bass_f = snip(bass, 337908, 382132)
bass_g = snip(bass, 382132, 440616)
bass_h = snip(bass, 440616, 468620)

kik = snip(drum_bap, 0, 22915)
snare = snip(drum_bap, 28040, 41555)
bell1 = snip(drum_bap, 55064, 65667)
bell2 = snip(drum_bap, 65667, 76269)

snips = [
	and_the, 
	typical, 
	mediterranean, 
	diet, 
	so,
	in_,
	crease,
	your,
	intake_of, 
	olive_oil, 
	fresh, 
	vegetables,
	began,
	troubled,
	mars,
	bump,
	know]

def boop(t, snip, g, degree):
	return snip.time_shift(t).gain(g).pan(degree)

def doop(t, snip, g, degree, speed_mult):
	#return snip.env(2000,2000).gain(g).pan(degree).time_shift(t)
	return snip.splice(2000,2000).gain(g).warp_speed(speed_mult).time_shift(t)


def ostinato(s, dur):
	pes = []
	t = s
	while t < beat_to_frame(dur):
		pes.append(boop(t, so, 1.0, -90))
		t += beat_to_frame(1)
		pes.append(boop(t, in_, 1.0, -30))
		t += beat_to_frame(1)
		pes.append(boop(t, crease, 1.0, 30))
		t += beat_to_frame(1)
		pes.append(boop(t, your, 1.0, 90))
		t += beat_to_frame(1)
	return pg.MixPE(*pes)

def ostinato2(s, dur):
	pes = []
	t = s
	while t < beat_to_frame(dur):
		pes.append(boop(t, fresh, 1.0, -90))
		t += beat_to_frame(1)
		pes.append(boop(t, and_the, 1.0, -30))
		t += beat_to_frame(1)
		pes.append(boop(t, crease_your, 1.0, 30))
		t += beat_to_frame(1)
		pes.append(boop(t, typical, 1.0, 90))
		t += beat_to_frame(1)
	return pg.MixPE(*pes)

def ostinato3(s, dur):
	pes = []
	t = s
	while t < beat_to_frame(dur):
		pes.append(doop(t, fresh, 1.0, -90, 0.5))
		t += beat_to_frame(1)
		pes.append(doop(t, and_the, 1.0, -30, 0.5))
		t += beat_to_frame(1)
		pes.append(doop(t, crease_your, 1.0, 30, 1.5))
		t += beat_to_frame(1)
		pes.append(doop(t, typical, 1.0, 90, 0.5))
		t += beat_to_frame(1)
	return pg.MixPE(*pes)

def random_ostinato(start_beat, dur_beat, seed):
	ut.print_warn('random ostinato seed:',beat_to_frame(start_beat),beat_to_frame(dur_beat),seed)
	pes = []
	random.seed(seed)
	t = beat_to_frame(start_beat)
	if random.randint(0,9) < 3:
		t += beat_to_frame(choose_dur())
	while t < beat_to_frame(start_beat) + beat_to_frame(dur_beat):
		a_snip = choose_snip()
		a_dur = beat_to_frame(choose_dur()) / 2
		a_interp = choose_interp()
		#print(f"{frame_to_beat(t):.2f}",retrieve_name(a_snip))
		print("pes.append(doop(",f"{frame_to_beat(t):.2f}",", ",retrieve_name(a_snip),", 1.0, -90,",a_interp,"))")
		pes.append(doop(t, a_snip, 1.0, -10, a_interp))
		t += a_dur
		t = round(t)
	return pg.MixPE(*pes)

def bass1(s, dur):
	pes = []
	t = s
	while t < beat_to_frame(dur):
		pes.append(boop(t, bass_a, 0.62, -20))
		t += beat_to_frame(3)
		pes.append(boop(t, bass_b, 0.62, 20))
		t += beat_to_frame(1)
	return pg.MixPE(*pes)

def bass2(s, dur):
	pes = []
	t = s
	while t < beat_to_frame(dur):
		pes.append(boop(t, bass_c, 0.62, -20))
		t += beat_to_frame(1)
		pes.append(boop(t, bass_d, 0.62, 20))
		t += beat_to_frame(2)
		pes.append(boop(t, bass_e, 0.62, 20))
		t += beat_to_frame(1)
		pes.append(boop(t, bass_f, 0.62, 20))
		t += beat_to_frame(1)
		pes.append(boop(t, bass_g, 0.62, 20))
		t += beat_to_frame(1)
		pes.append(boop(t, bass_h, 0.62, 20))
		t += beat_to_frame(1)
	return pg.MixPE(*pes)

def kik1(s, dur):
	pes = []
	t = s
	while t < beat_to_frame(dur):
		pes.append(boop(t, kik, 0.5, -10))
		t += beat_to_frame(1.65)
		pes.append(boop(t, kik, 0.5, -10))
		t += beat_to_frame(.35)
	return pg.MixPE(*pes)

def snare1(s, dur):
	pes = []
	t = s + beat_to_frame(1)
	while t < beat_to_frame(dur):
		pes.append(boop(t, snare, 0.5, 30))
		t += beat_to_frame(2)
	return pg.MixPE(*pes)

def hat1(s, dur):
	pes = []
	t = s + beat_to_frame(1)
	while t < beat_to_frame(dur):
		pes.append(boop(t, bell2, 0.6, -30))
		t += beat_to_frame(0.6)
		pes.append(boop(t, bell1, 0.71, -30))
		t += beat_to_frame(0.4)
	return pg.MixPE(*pes)



def lead_in(s):
	"""
	Notice that s defines when this snippet ends, not starts.
	"""
	pes = []
	t = s - int(3 * e_dur)
	pes.append(boop(t, diet, 1.0, 0))
	t += e_dur
	pes.append(boop(t, diet, 1.0, 0))
	t += e_dur
	pes.append(boop(t, diet, 1.0, 0))
	t += e_dur
	return pg.MixPE(*pes)

def m1(s, snip):
	pes = []
	t = s
	pes.append(boop(t, snip, 0.3, -30))
	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))
	t += s_dur
	pes.append(boop(t, snip, 1.0, 30))
	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))

	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))
	t += s_dur
	pes.append(boop(t, snip, 1.0, 30))
	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))
	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))

	t += s_dur
	pes.append(boop(t, snip, 1.0, 30))
	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))
	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))
	t += s_dur
	pes.append(boop(t, snip, 1.0, 30))

	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))
	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))
	t += s_dur
	pes.append(boop(t, snip, 1.0, 30))
	t += s_dur
	pes.append(boop(t, snip, 0.3, -30))

	return pg.MixPE(*pes)

troubled.play()
troubled.warp_speed(0.5).play()
doop(0, troubled, 1, 22, 0.5).play()


explore_seed = input("Enter seed: ")

while len(explore_seed) != 0:
	mix_explore = pg.MixPE(
		random_ostinato(0, 4, explore_seed),
		random_ostinato(4, 4, explore_seed),
		kik1(0, 16),
		snare1(0, 16),
	)
	pg.Transport(mix_explore).play()
	explore_seed = input("Enter seed: ")


# mix = pg.MixPE(
# 	ostinato(0, 32),
# 	snare1(beat_to_frame(16), 40),
# 	lead_in(beat_to_frame(8)),
# 	m1(beat_to_frame(8), in_),
# 	m1(beat_to_frame(12), in_),
# 	lead_in(beat_to_frame(16)),
# 	m1(beat_to_frame(16), in_),
# 	m1(beat_to_frame(20), in_),
# 	lead_in(beat_to_frame(24)),
# )


# pg.Transport(mix).play()


mix2 = pg.MixPE(
	ostinato(0, 40),
	bass2(0, 40),
	kik1(0, 40),
	snare1(0, 40),
	hat1(0,40),
	lead_in(beat_to_frame(8)),
	m1(beat_to_frame(8), in_),
	m1(beat_to_frame(12), in_),
	lead_in(beat_to_frame(16)),
	m1(beat_to_frame(16), in_),
	m1(beat_to_frame(20), in_),
	lead_in(beat_to_frame(24)),
)	

pg.Transport(mix2).play()
