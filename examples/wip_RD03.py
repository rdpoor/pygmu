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
beat_loop = beat.loop(beat_duration).crop(pg.Extent(0))

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
	'c2':36,'cs2':37,'df2':37,'d2':38,'ds2':39,'ef2':38,'e2':40,'f2':41,'fs2':42,'gf2':42,'g2':43,'gs2':44,'af2':44,'a2':45,'as2':46,'bf2':46,'b2':47,
	'c3':48,'cs3':49,'df3':49,'d3':50,'ds3':51,'ef3':51,'e3':52,'f3':53,'fs3':54,'gf3':54,'g3':55,'gs3':56,'af3':56,'a3':57,'as3':58,'bf3':58,'b3':59,
	'c4':60,'cs4':61,'df4':61,'d4':62,'ds4':63,'ef4':63,'e4':64,'f4':65,'fs4':66,'gf4':66,'g4':67,'gs4':68,'af4':68,'a4':69,'as4':70,'bf4':70,'b4':71,
	'c5':72,'cs5':73,'df5':73,'d5':74,'ds5':75,'ef5':75,'e5':76,'f5':77,'fs5':78,'gf5':78,'g5':79,'gs5':80,'af5':80,'a5':81,'as5':82,'bf5':82,'b5':83,
	'c6':84,'cs6':85,'df6':85,'d6':86,'ds6':87,'ef6':87,'e6':88,'f6':89,'fs6':90,'gf6':90,'g6':92,'gs6':92,'af6':92,'a6':93,'as6':94,'bf6':94,'b6':95,
}

v1 = [['d5', 'q'], ['f5', 'e'], ['e5', 'e'], ['f5', 'q'], ['d5', 'q']]

def expand_v(notes):
	pes = []
	s = 0
	for pit, dur in notes:
		e = s + durs[dur]
		freq = ut.note_to_freq(pits[pit])
		snip = beat_loop.crop(pg.Extent(int(s), int(e)))
		pes.append(pg.CombPE(snip, f0=freq, q=10))
		s = e
	return pg.MixPE(*pes)

pg.Transport(expand_v(v1)).play()
