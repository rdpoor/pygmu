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
orig_beat = pg.WavReaderPE("samples/BigBeat120bpm10.wav")
orig_bpm = 120 * 48000 / 44100   # higher srate
orig_duration = 176865

bpm = 100
beat_dur = int(orig_duration*orig_bpm/bpm)
beat = pg.TimewarpPE(orig_beat, pg.IdentityPE(channel_count=1).gain(bpm/orig_bpm)).loop(beat_dur).crop(pg.Extent(0))

q_note = words.frame_rate() * 60.0 / bpm

#   and the typical mediterranian diet.   so increase your intake of olive oil,   fresh vegetables
# ^         ^       ^             ^     ^      ^           ^         ^          ^       ^  

def beat_to_frame(b):
	return int(b * q_note)

def snip(pe, s, e):
	return pe.crop(pg.Extent(int(s), int(e))).delay(int(-s))

and_the = snip(words, 0, 25208)
typical = snip(words, 25208, 55196)
mediterranean = snip(words, 56934, 95615)
diet = snip(words, 95615, 121257)
so_in = snip(words, 128211, 153853)
crease_your = snip(words, 153961, 176344)
intake_of = snip(words, 176670, 206441)
olive_oil = snip(words, 206767, 244361)
fresh = snip(words, 244361, 258051)
vegetables = snip(words, 258051, 294450)

snips = [typical, mediterranean, diet, crease_your, intake_of, olive_oil, fresh, vegetables]

def choose_snip():
	return random.choice(snips)


def tuned_snip(snip, beat, pitch, q):
	f0 = ut.note_to_freq(pitch)
	if q > 0:
		pe = pg.BiquadPE(snip, 0, f0, q, "lowpass")
	else:
		pe = snip
	return pe.delay(int(beat * q_note))

mix = pg.MixPE(
	beat.delay(beat_to_frame(4)).gain(0.25).crop(pg.Extent(0, int(24 * q_note))),
	tuned_snip(typical, 0, 65, 128),
	tuned_snip(typical, 1, 65, 256),
	tuned_snip(typical, 2, 65, 128),
	tuned_snip(typical, 3, 65, 128),
	tuned_snip(typical, 4, 65, 128),
	tuned_snip(typical, 5, 72, 126),
	tuned_snip(typical, 6, 68, 128),
	tuned_snip(typical, 7, 65, 128),
	tuned_snip(typical, 8, 64, 128),
	tuned_snip(fresh, 9, 65, 128),
	tuned_snip(fresh, 9.5, 67, 128),
	tuned_snip(mediterranean, 10, 68, 128),
	tuned_snip(diet, 11.25, 70, 64),
	tuned_snip(diet, 11.5, 68, 64),
	tuned_snip(diet, 11.75, 67, 64),

	tuned_snip(typical, 12, 65, 8),
	tuned_snip(typical, 13, 65, 8),
	tuned_snip(typical, 14, 65, 8),
	tuned_snip(typical, 15, 65, 8),
	tuned_snip(typical, 16, 65, 8),
	tuned_snip(typical, 17, 72, 8),
	tuned_snip(typical, 18, 68, 8),
	tuned_snip(typical, 19, 65, 8),
	tuned_snip(typical, 20, 64, 8),
	tuned_snip(fresh, 21, 65, 8),
	tuned_snip(fresh, 21.5, 67, 8),
	tuned_snip(mediterranean, 22, 68, 8),
	tuned_snip(diet, 23.25, 70, 2),
	tuned_snip(diet, 23.5, 68, 2),
	tuned_snip(diet, 23.75, 67, 2),
	tuned_snip(olive_oil, 24.0, 65, 2),
	)

dst = pg.WavWriterPE(mix, "test.wav")
pg.FtsTransport(dst).play()
pg.Transport(pg.WavReaderPE("test.wav")).play()
