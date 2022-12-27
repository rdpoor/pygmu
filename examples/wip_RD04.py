import numpy as np
import os
import sys
import random
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

words = pg.WavReaderPE("samples/Tamper_TVFrame4_mono.wav")
bpm = 112

# duration of a quarter note
q_note_dur = words.frame_rate() * 60.0 / bpm

w_dur = int(q_note_dur * 4)
h_dur = int(q_note_dur * 2)
q_dur = int(q_note_dur)
e_dur = int(q_note_dur / 2)
s_dur = int(q_note_dur / 4)

def beat_to_frame(b):
	return int(b * q_note_dur)

def snip(pe, s, e):
	return pe.crop(pg.Extent(int(s), int(e))).delay(int(-s))

and_the = snip(words, 0, 25208)
typical = snip(words, 25208, 55196)
mediterranean = snip(words, 56934, 95615)
diet = snip(words, 95615, 121257)
so_in = snip(words, 128211, 153853)
so = snip(words, 135599, 144726)
in_ = snip(words, 147728, 154365)
crease = snip(words, 154299, 169406)
your = snip(words, 169406, 177700)
crease_your = snip(words, 153961, 176344)
intake_of = snip(words, 176670, 206441)
olive_oil = snip(words, 206767, 244361)
fresh = snip(words, 244361, 258051)
vegetables = snip(words, 258051, 294450)

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
	vegetables]

def boop(t, snip, g, degree):
	return snip.delay(t).gain(g).pan(degree)

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

mix = pg.MixPE(
	ostinato(0, 20),
	lead_in(beat_to_frame(8)),
	m1(beat_to_frame(8), in_),
	m1(beat_to_frame(12), in_),
	lead_in(beat_to_frame(16)),
	m1(beat_to_frame(16), in_),
	m1(beat_to_frame(20), in_),
	lead_in(beat_to_frame(24)),
)
# env = pg.EnvDetectPE(mix, attack=0.9, release=0.0001)
# compressed = pg.CompressorPE(mix, env, ratio=10.0, threshold_db=-20, post_gain_db=15)
# compressed = pg.WavWriterPE(compressed, "comp_03.wav")
# pg.Transport(compressed).play()
pg.Transport(mix).play()

