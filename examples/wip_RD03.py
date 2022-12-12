import numpy as np
import os
import sys
import random
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

beat = pg.WavReaderPE("samples/BigBeat120bpm10.wav")
beat_bpm = 120
beat_duration = 176552    # eight beats
beat_loop = beat.loop(beat_duration)

quarter_dur = beat_duration / 8

durs = {
	"w.": quarter_dur * 4.5,        # dotted whole note
	"w": quarter_dur * 4,           # whole note
	"h.": quarter_dur * 2.5,        # dotted half note
	"h": quarter_dur * 2,           # half note
	"q.": quarter_dur * 1.5,        # dotted quarter note
	"q": quarter_dur * 1,           # quarter note
	"e.": quarter_dur * 0.75,       # dotted eighth note
	"e": quarter_dur * 0.5,         # eighth note
	"s.": quarter_dur * 0.375,      # dotted sixteenth note
	"s": quarter_dur * 0.25,        # sixteenth note
	"tw": quarter_dur * (4 / 3),    # whole note triplet
	"th": quarter_dur * (2 / 3),    # half note triplet
	"tq": quarter_dur * (1 / 3),    # quarter note triplet
	"te": quarter_dur * (0.5 / 3),  # eighth note triplet
	"ts": quarter_dur * (0.25 / 3), # sixteenth note triplet
}

pits = {
	'c1':24,'cs1':25,'df1':25,'d1':26,'ds1':27,'ef1':27,'e1':28,'f1':29,'fs1':30,'gf1':30,'g1':31,'gs1':32,'af1':32,'a1':33,'as1':34,'bf1':34,'b1':35,
	'c2':36,'cs2':37,'df2':37,'d2':38,'ds2':39,'ef2':39,'e2':40,'f2':41,'fs2':42,'gf2':42,'g2':43,'gs2':44,'af2':44,'a2':45,'as2':46,'bf2':46,'b2':47,
	'c3':48,'cs3':49,'df3':49,'d3':50,'ds3':51,'ef3':51,'e3':52,'f3':53,'fs3':54,'gf3':54,'g3':55,'gs3':56,'af3':56,'a3':57,'as3':58,'bf3':58,'b3':59,
	'c4':60,'cs4':61,'df4':61,'d4':62,'ds4':63,'ef4':63,'e4':64,'f4':65,'fs4':66,'gf4':66,'g4':67,'gs4':68,'af4':68,'a4':69,'as4':70,'bf4':70,'b4':71,
	'c5':72,'cs5':73,'df5':73,'d5':74,'ds5':75,'ef5':75,'e5':76,'f5':77,'fs5':78,'gf5':78,'g5':79,'gs5':80,'af5':80,'a5':81,'as5':82,'bf5':82,'b5':83,
	'c6':84,'cs6':85,'df6':85,'d6':86,'ds6':87,'ef6':87,'e6':88,'f6':89,'fs6':90,'gf6':90,'g6':91,'gs6':92,'af6':92,'a6':93,'as6':94,'bf6':94,'b6':95,
	'c7':96,'cs7':97,'df7':97,'d7':98,'ds7':99,'ef7':99,'e7':100,'f7':101,'fs7':102,'gf7':102,'g7':103,'gs7':104,'af7':104,'a7':105,'as7':106,'bf7':106,'b7':107,
}

def combify(notes):
	pes = []
	s = 0
	for pit, dur, q in notes:
		e = s + durs[dur]
		if pit != '':
			freq = ut.note_to_freq(pits[pit])
			snip = beat_loop.crop(pg.Extent(int(s), int(e)))
			if q == 0:
				pes.append(snip)
			else:
				pes.append(pg.CombPE(snip, f0=freq, q=q))
		else:
			# blank pitch => rest
			pass
		s = e
	return pg.MixPE(*pes)

def quadify(notes):
	pes = []
	s = 0
	for pit, dur, q in notes:
		e = s + durs[dur]
		if pit != '':
			freq = ut.note_to_freq(pits[pit])
			snip = beat_loop.crop(pg.Extent(int(s), int(e)))
			if q == 0:
				pes.append(snip)
			else:
				pes.append(pg.Biquad2PE(snip, f0=freq, q=q))
		else:
			# blank pitch => rest
			pass
		s = e
	return pg.MixPE(*pes)

intro = [
	['a5', 'w', 230], ['a5', 'w', 230], 
	['a5', 'e', 230], ['a5', 'e', 165], ['a5', 'e', 114], ['a5', 'e', 80], 
	['a5', 'e', 55], ['a5', 'e', 38], ['a5', 'e', 26], ['a5', 'e', 18],
	['a5', 'e', 12], ['a5', 'e', 8], ['a5', 'e', 6], ['a5', 'e', 4], 
	['a5', 'e', 2], ['a5', 'e', 2], ['a5', 'e', 1], ['a5', 'e', 1]
	]

ostinato = beat_loop

motif = [
	['d5', 'q', 10], ['f5', 'e', 10], ['e5', 'e', 10], ['f5', 'q', 10], ['d5', 'q', 10],
	['d5', 'q', 10], ['f5', 'e', 10], ['e5', 'e', 10], ['f5', 'q', 10], ['d5', 'q', 10],
	]

motif12 = [
	['d6', 'q', 20], ['f6', 'e', 20], ['e6', 'e', 20], ['f6', 'q', 20], ['d6', 'q', 20],
	['d6', 'q', 20], ['f6', 'e', 20], ['e6', 'e', 20], ['f6', 'q', 20], ['d6', 'q', 20],
	]

motif19 = [
	['a6', 'q', 20], ['c7', 'e', 20], ['b6', 'e', 20], ['c7', 'q', 20], ['a6', 'q', 20],
	['a6', 'q', 20], ['c7', 'e', 20], ['b6', 'e', 20], ['c7', 'q', 20], ['a6', 'q', 20],
	]

motif24 = [
	['d7', 'q', 20], ['f7', 'e', 20], ['e7', 'e', 20], ['f7', 'q', 20], ['d7', 'q', 20],
	['d7', 'q', 20], ['f7', 'e', 20], ['e7', 'e', 20], ['f7', 'q', 20], ['d7', 'q', 20],
	]

bass = [
	['d4', 'w', 64], ['b3', 'w', 64], ['c4', 'w', 64], ['f3', 'h', 64], ['c3', 'h', 64]
]

bass_m12 = [
	['d2', 'w', 64], ['b1', 'w', 64], ['c2', 'w', 64], ['f2', 'h', 64], ['c2', 'h', 64]
]

mix = pg.MixPE(combify(intro).gain(0.25), 
			   ostinato.crop(pg.Extent(int(quarter_dur*12),int(quarter_dur * 96))).gain(0.25),
			   combify(motif12).delay(int(quarter_dur * 16)),
			   combify(bass).delay(int(quarter_dur * 32)).gain(0.8),
			   combify(motif).delay(int(quarter_dur * 32)),
			   combify(motif).delay(int(quarter_dur * 40)),

			   combify(bass).delay(int(quarter_dur * 48)).gain(0.8),
			   quadify(bass_m12).delay(int(quarter_dur * 48)).gain(0.0625),
			   combify(motif).delay(int(quarter_dur * 48)),
			   combify(motif).delay(int(quarter_dur * 56)),

			   combify(bass).delay(int(quarter_dur * 64)).gain(0.8),
			   quadify(bass_m12).delay(int(quarter_dur * 64)).gain(0.0625),
			   combify(motif19).delay(int(quarter_dur * 64)),
			   combify(motif).delay(int(quarter_dur * 64)).gain(0.7),
			   combify(motif19).delay(int(quarter_dur * 72)),
			   combify(motif).delay(int(quarter_dur * 72)).gain(0.7),
               # needs "middle eight" (and an ending)
			   combify(bass).delay(int(quarter_dur * 80)).gain(0.8),
			   quadify(bass_m12).delay(int(quarter_dur * 80)).gain(0.0625),
			   )

dst = pg.WavWriterPE(mix, "examples/wip_RD03.wav")
pg.FtsTransport(dst).play()
