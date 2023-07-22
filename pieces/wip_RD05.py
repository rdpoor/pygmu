import numpy as np
import os
import re
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

class Pitched(object):

	def __init__(self, orig_pitch, path):
		self._orig_pitch = orig_pitch
		self._path = path


	def orig_pitch(self):
		return self._orig_pitch

	def path(self):
		return self.path

	def retune(self, new_pitch):
		"""
		Return a PE that plays the original sound file at a new pitch.
		"""
		ratio = ut.mtof(new_pitch) / ut.mtof(self._orig_pitch)
		return pg.WarpSpeedPE(pg.WavReaderPE(self._path), ratio)

class PitchedLib(object):

	def __init__(self):
		self._pitched = {}

	def add_file(self, orig_pitch, path):
		self._pitched[path] = Pitched(orig_pitch, path)


def name_to_midi(name):
	"""
	Convert a string to a MIDI pitch number:
	  'A4' => 69     or 'a4' (case insensitive)
	  'a#4' => 70    # or s signifies sharp (yes, e#4 == f4)
	  'As4' => 70
	  'Ab4' => 68    b or f signifies flat (yes, ff4 == e4)
	  'Af4' => 68
	"""
	name = name.lower()
	try:
		if len(name) < 2 or len(name) > 3:
			raise ArgumentError("Note name must be 2 or 3 chars")
		else:
			pitch = {'c':0, 'd':2, 'e':4, 'f':5, 'g':7, 'a':9, 'b':11}[name[0]]
			octave = (int(name[-1]) + 1) * 12
			if len(name) == 3:
				accidental = {'#':1, 's':1, 'b':-1, 'f':-1}[name[1]]
			elif len(name) == 2:
				accidental = 0
			return pitch + octave + accidental
	except (KeyError, ValueError, ArgumentError) as e:
		print(e)

sound_lib = [
    ("samples/multisamples/Amanda/Amanda_Aa_1_G3.wav", name_to_midi('G3')),
    ("samples/multisamples/Amanda/Amanda_Aa_3_A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Amanda/Amanda_Aa_3_G4.wav", name_to_midi('G4')),
    ("samples/multisamples/Ambibell/Ambibell-036-c1.wav", name_to_midi('c1')),
    ("samples/multisamples/Ambibell/Ambibell-042-f#1.wav", name_to_midi('f#1')),
    ("samples/multisamples/Ambibell/Ambibell-048-c2.wav", name_to_midi('c2')),
    ("samples/multisamples/Ambibell/Ambibell-054-f#2.wav", name_to_midi('f#2')),
    ("samples/multisamples/Ambibell/Ambibell-060-c3.wav", name_to_midi('c3')),
    ("samples/multisamples/Ambibell/Ambibell-066-f#3.wav", name_to_midi('f#3')),
    ("samples/multisamples/Ambibell/Ambibell-072-c4.wav", name_to_midi('c4')),
    ("samples/multisamples/Ambibell/Ambibell-078-f#4.wav", name_to_midi('f#4')),
    ("samples/multisamples/Ambibell/Ambibell-084-c5.wav", name_to_midi('c5')),
    ("samples/multisamples/Ambibell/Ambibell-090-f#5.wav", name_to_midi('f#5')),
    ("samples/multisamples/Ambibell/Ambibell-096-c6.wav", name_to_midi('c6')),
    ("samples/multisamples/Anklung_Hit/Anklung_Hit_1-C2.wav", name_to_midi('C3')),
    ("samples/multisamples/Anklung_Hit/Anklung_Hit_3-F2.wav", name_to_midi('F3')),
    ("samples/multisamples/Anklung_Hit/Anklung_Hit_6-A#2.wav", name_to_midi('A#3')),
    ("samples/multisamples/Anklung_Hit/Anklung_Hit_8-C#3.wav", name_to_midi('C#4')),
    ("samples/multisamples/Autoharp_Binaural/Autoharp_Binaural_B4.wav", name_to_midi('B3')),
    ("samples/multisamples/Autoharp_Binaural/Autoharp_Binaural_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Autoharp_Binaural/Autoharp_Binaural_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Autoharp_Binaural/Autoharp_Binaural_D2.wav", name_to_midi('D2')),
    ("samples/multisamples/Autoharp_Binaural/Autoharp_Binaural_E4.wav", name_to_midi('E4')),
    ("samples/multisamples/Autoharp_Binaural/Autoharp_Binaural_F3.wav", name_to_midi('F3')),
    ("samples/multisamples/Autoharp_Binaural/Autoharp_Binaural_G2.wav", name_to_midi('G2')),
    ("samples/multisamples/Autoharp_Binaural/Autoharp_Binaural_G4.wav", name_to_midi('G4')),
    ("samples/multisamples/Autoharp_Mute/Autoharp_Mute_C2.wav", name_to_midi('C1')),
    ("samples/multisamples/Autoharp_Mute/Autoharp_Mute_C3.wav", name_to_midi('C2')),
    ("samples/multisamples/Autoharp_Mute/Autoharp_Mute_C5.wav", name_to_midi('C4')),
    ("samples/multisamples/Autoharp_Mute/Autoharp_Mute_G3.wav", name_to_midi('G2')),
    ("samples/multisamples/Autoharp_Mute/Autoharp_Mute_G4.wav", name_to_midi('G3')),
    ("samples/multisamples/Autoharp_Mute/Autoharp_Mute_G5.wav", name_to_midi('G4')),
    ("samples/multisamples/Bandura_Soft/Bandura_Soft_A1.wav", name_to_midi('A1')),
    ("samples/multisamples/Bandura_Soft/Bandura_Soft_A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Bandura_Soft/Bandura_Soft_A3.wav", name_to_midi('A3')),
    ("samples/multisamples/Bandura_Soft/Bandura_Soft_E2.wav", name_to_midi('E2')),
    ("samples/multisamples/Bandura_Soft/Bandura_Soft_E3.wav", name_to_midi('E3')),
    ("samples/multisamples/Bandura_Soft/Bandura_Soft_E4.wav", name_to_midi('E4')),
    ("samples/multisamples/Bell_1/Bell_1_C1.wav", name_to_midi('d2')),
    ("samples/multisamples/Bell_1/Bell_1_C2.wav", name_to_midi('d3')),
    ("samples/multisamples/Bell_1/Bell_1_C3.wav", name_to_midi('d4')),
    ("samples/multisamples/Bell_1/Bell_1_C4.wav", name_to_midi('d5')),
    ("samples/multisamples/Bell_1/Bell_1_C5.wav", name_to_midi('d6')),
    ("samples/multisamples/Cheng_Hard/Cheng_Hard_1-C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Cheng_Hard/Cheng_Hard_2-G2.wav", name_to_midi('G2')),
    ("samples/multisamples/Cheng_Hard/Cheng_Hard_3-C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Cheng_Hard/Cheng_Hard_4-G3.wav", name_to_midi('G3')),
    ("samples/multisamples/Cheng_Hard/Cheng_Hard_5-C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Cheng_Hard/Cheng_Hard_6-G4.wav", name_to_midi('G4')),
    ("samples/multisamples/Cheng_Hard/Cheng_Hard_7-C5.wav", name_to_midi('C5')),
    ("samples/multisamples/Choir_Female_Ah/Choir_Female_Ah_pp_1_B2.wav", name_to_midi('B2')),
    ("samples/multisamples/Choir_Female_Ah/Choir_Female_Ah_pp_1_B3.wav", name_to_midi('B3')),
    ("samples/multisamples/Choir_Female_Ah/Choir_Female_Ah_pp_1_F4.wav", name_to_midi('F4')),
    ("samples/multisamples/Daphne/Daphne_C2.wav", name_to_midi('C1')),
    ("samples/multisamples/Daphne/Daphne_C3.wav", name_to_midi('C2')),
    ("samples/multisamples/Daphne/Daphne_C4.wav", name_to_midi('C3')),
    ("samples/multisamples/Daphne/Daphne_C5.wav", name_to_midi('C4')),
    ("samples/multisamples/Daphne/Daphne_F#2.wav", name_to_midi('F#1')),
    ("samples/multisamples/Daphne/Daphne_F#3.wav", name_to_midi('F#2')),
    ("samples/multisamples/Daphne/Daphne_F#4.wav", name_to_midi('F#3')),
    ("samples/multisamples/Duduk/Duduk_A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Duduk/Duduk_A3.wav", name_to_midi('A3')),
    ("samples/multisamples/Duduk/Duduk_D3.wav", name_to_midi('D3')),
    ("samples/multisamples/Duduk/Duduk_F3.wav", name_to_midi('F3')),
    ("samples/multisamples/Eguitar/Eguitar_A1.wav", name_to_midi('A1')),
    ("samples/multisamples/Eguitar/Eguitar_A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Eguitar/Eguitar_A3.wav", name_to_midi('A3')),
    ("samples/multisamples/Eguitar/Eguitar_A4.wav", name_to_midi('A4')),
    ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_01-G2.wav", name_to_midi('G2')),
    ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_03-A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_05-B2.wav", name_to_midi('B2')),
    ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_07-C#3.wav", name_to_midi('C#3')),
    ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_10-E3.wav", name_to_midi('E3')),
    ("samples/multisamples/Ghost_Siren/Ghost_Siren_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Ghost_Siren/Ghost_Siren_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Ghost_Siren/Ghost_Siren_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Ghost_Siren/Ghost_Siren_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/GridPad/GridPad_C1.wav", name_to_midi('C0')),
    ("samples/multisamples/GridPad/GridPad_C2.wav", name_to_midi('C1')),
    ("samples/multisamples/GridPad/GridPad_C3.wav", name_to_midi('C2')),
    ("samples/multisamples/GridPad/GridPad_C4.wav", name_to_midi('C3')),
    ("samples/multisamples/HarmonicGuitar/HarmonicGuitar-A1.wav", name_to_midi('A1')),
    ("samples/multisamples/HarmonicGuitar/HarmonicGuitar-A3.wav", name_to_midi('A3')),
    ("samples/multisamples/HarmonicGuitar/HarmonicGuitar-C1.wav", name_to_midi('C1')),
    ("samples/multisamples/HarmonicGuitar/HarmonicGuitar-C3.wav", name_to_midi('C3')),
    ("samples/multisamples/HarmonicGuitar/HarmonicGuitar-D#2.wav", name_to_midi('D#2')),
    ("samples/multisamples/HarmonicGuitar/HarmonicGuitar-D#4.wav", name_to_midi('D#4')),
    ("samples/multisamples/Harmonica/Harmonica_C0.wav", name_to_midi('C1')),
    ("samples/multisamples/Harmonica/Harmonica_C1.wav", name_to_midi('C2')),
    ("samples/multisamples/Harmonica/Harmonica_C2.wav", name_to_midi('C3')),
    ("samples/multisamples/Harmonica/Harmonica_C3.wav", name_to_midi('C4')),
    ("samples/multisamples/Harmonica/Harmonica_C4.wav", name_to_midi('C5')),
    ("samples/multisamples/Hiroto_/Hiroto_C0.wav", name_to_midi('C0')),
    ("samples/multisamples/Hiroto_/Hiroto_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Hiroto_/Hiroto_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Hiroto_/Hiroto_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Hiroto_/Hiroto_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Hiroto_/Hiroto_F#0.wav", name_to_midi('F#0')),
    ("samples/multisamples/Hiroto_/Hiroto_F#1.wav", name_to_midi('F#1')),
    ("samples/multisamples/Hiroto_/Hiroto_F#2.wav", name_to_midi('F#2')),
    ("samples/multisamples/Hiroto_/Hiroto_F#3.wav", name_to_midi('F#3')),
    ("samples/multisamples/Hiroto_/Hiroto_F#4.wav", name_to_midi('F#4')),
    ("samples/multisamples/Kalimba/Kalimba_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Kalimba/Kalimba_D2.wav", name_to_midi('D2')),
    ("samples/multisamples/Kalimba/Kalimba_F3.wav", name_to_midi('F3')),
    ("samples/multisamples/LOA_Hammond/LOA_Hammond_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/LOA_Hammond/LOA_Hammond_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/LOA_Hammond/LOA_Hammond_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/LOA_Hammond/LOA_Hammond_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/LOA_Hammond/LOA_Hammond_C5.wav", name_to_midi('C5')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_A1.wav", name_to_midi('A1')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_A2.wav", name_to_midi('A2')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_A3.wav", name_to_midi('A3')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_A4.wav", name_to_midi('A4')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_C5.wav", name_to_midi('C5')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_D#1.wav", name_to_midi('D#1')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_D#2.wav", name_to_midi('D#2')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_D#3.wav", name_to_midi('D#3')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_D#4.wav", name_to_midi('D#4')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_F#1.wav", name_to_midi('F#1')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_F#2.wav", name_to_midi('F#2')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_F#3.wav", name_to_midi('F#3')),
    ("samples/multisamples/LOA_Piano/LOA_Piano_F#4.wav", name_to_midi('F#4')),
    ("samples/multisamples/Marimba/Marimba_C2.wav", name_to_midi('C1')),
    ("samples/multisamples/Marimba/Marimba_C3.wav", name_to_midi('C2')),
    ("samples/multisamples/Marimba/Marimba_C4.wav", name_to_midi('C3')),
    ("samples/multisamples/Marimba/Marimba_C5.wav", name_to_midi('C4')),
    ("samples/multisamples/Marimba/Marimba_C6.wav", name_to_midi('C5')),
    ("samples/multisamples/Marimba/Marimba_C7.wav", name_to_midi('C6')),
    ("samples/multisamples/Mellotron_Flute/Mellotron_Flute_A#2.wav", name_to_midi('A#2')),
    ("samples/multisamples/Mellotron_Flute/Mellotron_Flute_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Mellotron_Flute/Mellotron_Flute_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Mellotron_Flute/Mellotron_Flute_D5.wav", name_to_midi('D5')),
    ("samples/multisamples/Mellotron_Flute/Mellotron_Flute_F#3.wav", name_to_midi('F#3')),
    ("samples/multisamples/Mellotron_Flute/Mellotron_Flute_F#4.wav", name_to_midi('F#4')),
    ("samples/multisamples/Mellotron_Flute/Mellotron_Flute_F5.wav", name_to_midi('F5')),
    ("samples/multisamples/Nephele/Nephele_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Nephele/Nephele_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Nephele/Nephele_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Nephele/Nephele_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Philipos/Philipos_C1.wav", name_to_midi('C0')),
    ("samples/multisamples/Philipos/Philipos_C2.wav", name_to_midi('C1')),
    ("samples/multisamples/Philipos/Philipos_C3.wav", name_to_midi('C2')),
    ("samples/multisamples/Philipos/Philipos_C4.wav", name_to_midi('C3')),
    ("samples/multisamples/Philipos/Philipos_C5.wav", name_to_midi('C4')),
    ("samples/multisamples/Philipos/Philipos_F#1.wav", name_to_midi('F#0')),
    ("samples/multisamples/Philipos/Philipos_F#2.wav", name_to_midi('F#1')),
    ("samples/multisamples/Philipos/Philipos_F#3.wav", name_to_midi('F#2')),
    ("samples/multisamples/Philipos/Philipos_F#4.wav", name_to_midi('F#3')),
    ("samples/multisamples/Piano1/Piano1-A0.wav", name_to_midi('A0')),
    ("samples/multisamples/Piano1/Piano1-A1.wav", name_to_midi('A1')),
    ("samples/multisamples/Piano1/Piano1-A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Piano1/Piano1-A3.wav", name_to_midi('A3')),
    ("samples/multisamples/Piano1/Piano1-A4.wav", name_to_midi('A4')),
    ("samples/multisamples/Piano1/Piano1-A5.wav", name_to_midi('A5')),
    ("samples/multisamples/Piano1/Piano1-C0.wav", name_to_midi('C0')),
    ("samples/multisamples/Piano1/Piano1-C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Piano1/Piano1-C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Piano1/Piano1-C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Piano1/Piano1-C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Piano1/Piano1-C5.wav", name_to_midi('C5')),
    ("samples/multisamples/Piano1/Piano1-D#0.wav", name_to_midi('D#0')),
    ("samples/multisamples/Piano1/Piano1-D#1.wav", name_to_midi('D#1')),
    ("samples/multisamples/Piano1/Piano1-D#2.wav", name_to_midi('D#2')),
    ("samples/multisamples/Piano1/Piano1-D#3.wav", name_to_midi('D#3')),
    ("samples/multisamples/Piano1/Piano1-D#4.wav", name_to_midi('D#4')),
    ("samples/multisamples/Piano1/Piano1-D#5.wav", name_to_midi('D#5')),
    ("samples/multisamples/Piano1/Piano1-F#0.wav", name_to_midi('F#0')),
    ("samples/multisamples/Piano1/Piano1-F#1.wav", name_to_midi('F#1')),
    ("samples/multisamples/Piano1/Piano1-F#2.wav", name_to_midi('F#2')),
    ("samples/multisamples/Piano1/Piano1-F#3.wav", name_to_midi('F#3')),
    ("samples/multisamples/Piano1/Piano1-F#4.wav", name_to_midi('F#4')),
    ("samples/multisamples/Piano1/Piano1-F#5.wav", name_to_midi('F#5')),
    ("samples/multisamples/Piano_St/Piano_St_A0.wav", name_to_midi('A0')),
    ("samples/multisamples/Piano_St/Piano_St_A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Piano_St/Piano_St_C0.wav", name_to_midi('C0')),
    ("samples/multisamples/Piano_St/Piano_St_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Piano_St/Piano_St_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Piano_St/Piano_St_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Piano_St/Piano_St_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Piano_St/Piano_St_C5.wav", name_to_midi('C5')),
    ("samples/multisamples/Piano_St/Piano_St_C6.wav", name_to_midi('C6')),
    ("samples/multisamples/Piano_St/Piano_St_F1.wav", name_to_midi('F1')),
    ("samples/multisamples/Piano_St/Piano_St_F5.wav", name_to_midi('F5')),
    ("samples/multisamples/Santur/Santur_1-D4.wav", name_to_midi('D3')),
    ("samples/multisamples/Santur/Santur_3-F#4.wav", name_to_midi('F#3')),
    ("samples/multisamples/Santur/Santur_5-B4.wav", name_to_midi('B3')),
    ("samples/multisamples/Santur/Santur_7-D#5.wav", name_to_midi('D#4')),
    ("samples/multisamples/Santur/Santur_9-A#5.wav", name_to_midi('A#4')),
    ("samples/multisamples/Saraya/Saraya_C2.wav", name_to_midi('C0')),
    ("samples/multisamples/Saraya/Saraya_C3.wav", name_to_midi('C1')),
    ("samples/multisamples/Saraya/Saraya_C4.wav", name_to_midi('C2')),
    ("samples/multisamples/Saraya/Saraya_F#2.wav", name_to_midi('F#0')),
    ("samples/multisamples/Saraya/Saraya_F#3.wav", name_to_midi('F#1')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_A5.wav", name_to_midi('A5')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_C6.wav", name_to_midi('C6')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_D3.wav", name_to_midi('D3')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_D5.wav", name_to_midi('D5')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_F1.wav", name_to_midi('F1')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_F2.wav", name_to_midi('F2')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_F4.wav", name_to_midi('F4')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_G#2.wav", name_to_midi('G#2')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_G3.wav", name_to_midi('G3')),
    ("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_G5.wav", name_to_midi('G5')),
    ("samples/multisamples/SirinSqPad/SirinSqPad_C0.wav", name_to_midi('C0')),
    ("samples/multisamples/SirinSqPad/SirinSqPad_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/SirinSqPad/SirinSqPad_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/SirinSqPad/SirinSqPad_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Sitar/Sitar_01-C#3.wav", name_to_midi('C#2')),
    ("samples/multisamples/Sitar/Sitar_01-D2.wav", name_to_midi('D2')),
    ("samples/multisamples/Sitar/Sitar_02-G2.wav", name_to_midi('G2')),
    ("samples/multisamples/Sitar/Sitar_03-A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Sitar/Sitar_04-D3.wav", name_to_midi('D3')),
    ("samples/multisamples/Sitar/Sitar_05-E3.wav", name_to_midi('E3')),
    ("samples/multisamples/Sitar/Sitar_06-F3.wav", name_to_midi('F3')),
    ("samples/multisamples/Sitar/Sitar_07-G3.wav", name_to_midi('G3')),
    ("samples/multisamples/Sitar/Sitar_08-A3.wav", name_to_midi('A3')),
    ("samples/multisamples/Sitar/Sitar_09-B3.wav", name_to_midi('B3')),
    ("samples/multisamples/Sitar/Sitar_10-C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Sitar/Sitar_11-D4.wav", name_to_midi('D4')),
    ("samples/multisamples/SoloVln/SoloVln_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/SoloVln/SoloVln_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/SoloVln/SoloVln_C5.wav", name_to_midi('C5')),
    ("samples/multisamples/Strings/Strings--A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Strings/Strings-C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Strings/Strings-C5.wav", name_to_midi('C5')),
    ("samples/multisamples/Strings/Strings-D#4.wav", name_to_midi('D#4')),
    ("samples/multisamples/Strings/Strings-F#3.wav", name_to_midi('F#3')),
    ("samples/multisamples/Supersaw_1/Supersaw_1_036_c1.wav", name_to_midi('c1')),
    ("samples/multisamples/Supersaw_1/Supersaw_1_045_a1.wav", name_to_midi('a1')),
    ("samples/multisamples/Supersaw_1/Supersaw_1_054_f#2.wav", name_to_midi('f#2')),
    ("samples/multisamples/Supersaw_1/Supersaw_1_063_d#3.wav", name_to_midi('d#3')),
    ("samples/multisamples/Supersaw_1/Supersaw_1_072_c4.wav", name_to_midi('c4')),
    ("samples/multisamples/Supersaw_1/Supersaw_1_078_f#4.wav", name_to_midi('f#4')),
    ("samples/multisamples/Supersaw_1/Supersaw_1_084_c5.wav", name_to_midi('c5')),
    ("samples/multisamples/Supersaw_1/Supersaw_1_090_f#5.wav", name_to_midi('f#5')),
    ("samples/multisamples/Supersaw_1/Supersaw_1_096_c6.wav", name_to_midi('c6')),
    ("samples/multisamples/T8_Strings_/T8_Strings_C1.wav", name_to_midi('C0')),
    ("samples/multisamples/T8_Strings_/T8_Strings_C2.wav", name_to_midi('C1')),
    ("samples/multisamples/T8_Strings_/T8_Strings_C3.wav", name_to_midi('C2')),
    ("samples/multisamples/T8_Strings_/T8_Strings_C4.wav", name_to_midi('C3')),
    ("samples/multisamples/T8_Strings_/T8_Strings_C5.wav", name_to_midi('C4')),
    ("samples/multisamples/T8_Strings_/T8_Strings_C7.wav", name_to_midi('C6')),
    ("samples/multisamples/T8_Strings_/T8_Strings_G6.wav", name_to_midi('C5')),
    ("samples/multisamples/T8_Sync_/T8_Sync_C1.wav", name_to_midi('C0')),
    ("samples/multisamples/T8_Sync_/T8_Sync_C2.wav", name_to_midi('C1')),
    ("samples/multisamples/T8_Sync_/T8_Sync_C3.wav", name_to_midi('C2')),
    ("samples/multisamples/T8_Sync_/T8_Sync_C4.wav", name_to_midi('C3')),
    ("samples/multisamples/T8_Sync_/T8_Sync_C5.wav", name_to_midi('C4')),
    ("samples/multisamples/T8_Sync_/T8_Sync_C6.wav", name_to_midi('C5')),
    ("samples/multisamples/Thumpy/Thumpy_A0.wav", name_to_midi('A0')),
    ("samples/multisamples/Thumpy/Thumpy_A1.wav", name_to_midi('A1')),
    ("samples/multisamples/Thumpy/Thumpy_A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Thumpy/Thumpy_A3.wav", name_to_midi('A3')),
    ("samples/multisamples/Thumpy/Thumpy_A4.wav", name_to_midi('A4')),
    ("samples/multisamples/Thumpy/Thumpy_C0.wav", name_to_midi('C0')),
    ("samples/multisamples/Thumpy/Thumpy_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Thumpy/Thumpy_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Thumpy/Thumpy_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Thumpy/Thumpy_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Thumpy/Thumpy_E0.wav", name_to_midi('E0')),
    ("samples/multisamples/Thumpy/Thumpy_E1.wav", name_to_midi('E1')),
    ("samples/multisamples/Thumpy/Thumpy_E2.wav", name_to_midi('E2')),
    ("samples/multisamples/Thumpy/Thumpy_E3.wav", name_to_midi('E3')),
    ("samples/multisamples/Thumpy/Thumpy_E4.wav", name_to_midi('E4')),
    ("samples/multisamples/Thumpy/Thumpy_F0.wav", name_to_midi('F0')),
    ("samples/multisamples/Thumpy/Thumpy_F1.wav", name_to_midi('F1')),
    ("samples/multisamples/Thumpy/Thumpy_F2.wav", name_to_midi('F2')),
    ("samples/multisamples/Thumpy/Thumpy_F3.wav", name_to_midi('F3')),
    ("samples/multisamples/Thumpy/Thumpy_F4.wav", name_to_midi('F4')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_A1.wav", name_to_midi('A1')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_A2.wav", name_to_midi('A2')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_A4.wav", name_to_midi('A4')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_C5.wav", name_to_midi('C5')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_Eb1.wav", name_to_midi('Eb1')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_Eb2.wav", name_to_midi('Eb2')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_Eb3.wav", name_to_midi('Eb3')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_Eb4.wav", name_to_midi('Eb4')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_F#1.wav", name_to_midi('F#1')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_F#2.wav", name_to_midi('F#2')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_F#3.wav", name_to_midi('F#3')),
    ("samples/multisamples/Tutti_Pizz/Tutti_Pizz_F#4.wav", name_to_midi('F#4')),
    ("samples/multisamples/Twin_Strings/Twin_Strings_C0.wav", name_to_midi('C0')),
    ("samples/multisamples/Twin_Strings/Twin_Strings_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Twin_Strings/Twin_Strings_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Twin_Strings/Twin_Strings_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Twin_Strings/Twin_Strings_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Twin_Strings/Twin_Strings_C5.wav", name_to_midi('C5')),
    ("samples/multisamples/Unstabler_Pad/Unstabler_Pad_C0.wav", name_to_midi('C0')),
    ("samples/multisamples/Unstabler_Pad/Unstabler_Pad_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Unstabler_Pad/Unstabler_Pad_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Unstabler_Pad/Unstabler_Pad_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Unstabler_Pad/Unstabler_Pad_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/VC_pizz_f/VC_pizz_f_A#2.wav", name_to_midi('A#1')),
    ("samples/multisamples/VC_pizz_f/VC_pizz_f_A#3.wav", name_to_midi('A#2')),
    ("samples/multisamples/VC_pizz_f/VC_pizz_f_A#4.wav", name_to_midi('A#3')),
    ("samples/multisamples/VC_pizz_f/VC_pizz_f_D2.wav", name_to_midi('D1')),
    ("samples/multisamples/VC_pizz_f/VC_pizz_f_D3.wav", name_to_midi('D2')),
    ("samples/multisamples/VC_pizz_f/VC_pizz_f_D4.wav", name_to_midi('D3')),
    ("samples/multisamples/Violin_Undul/Violin_Undul_C3_RM.wav", name_to_midi('C3')),
    ("samples/multisamples/Violin_Undul/Violin_Undul_C4_RM.wav", name_to_midi('C4')),
    ("samples/multisamples/Violin_Undul/Violin_Undul_C5_RM.wav", name_to_midi('C5')),
    ("samples/multisamples/Violin_Undul/Violin_Undul_C6_RM.wav", name_to_midi('C6')),
    ("samples/multisamples/Wurly_Trem/Wurly_Trem_C1.wav", name_to_midi('C1')),
    ("samples/multisamples/Wurly_Trem/Wurly_Trem_C2.wav", name_to_midi('C2')),
    ("samples/multisamples/Wurly_Trem/Wurly_Trem_C3.wav", name_to_midi('C3')),
    ("samples/multisamples/Wurly_Trem/Wurly_Trem_C4.wav", name_to_midi('C4')),
    ("samples/multisamples/Wurly_Trem/Wurly_Trem_C5.wav", name_to_midi('C5')),
    ("samples/multisamples/Wurly_Trem/Wurly_Trem_C6.wav", name_to_midi('C6')),
    ("samples/multisamples/Zissis/Zissis_C1.wav", name_to_midi('C2')),
    ("samples/multisamples/Zissis/Zissis_C2.wav", name_to_midi('C3')),
    ("samples/multisamples/Zissis/Zissis_C3.wav", name_to_midi('C4')),
    ("samples/multisamples/Zissis/Zissis_C4.wav", name_to_midi('C5')),
    ("samples/multisamples/Zissis/Zissis_F#1.wav", name_to_midi('F#2')),
    ("samples/multisamples/Zissis/Zissis_F#2.wav", name_to_midi('F#3')),
    ("samples/multisamples/Zissis/Zissis_F#3.wav", name_to_midi('F#4')),
    ("samples/multisamples/Zissis/Zissis_F#4.wav", name_to_midi('F#5')),
    ("samples/multisamples/uke/A#4.wav", name_to_midi('A4')),
    ("samples/multisamples/uke/A4.wav", name_to_midi('Ab4')),
    ("samples/multisamples/uke/B4.wav", name_to_midi('Bb4')),
    ("samples/multisamples/uke/C#4.wav", name_to_midi('C4')),
    ("samples/multisamples/uke/C4.wav", name_to_midi('B3')),
    ("samples/multisamples/uke/C4_a.wav", name_to_midi('B3')),
    ("samples/multisamples/uke/D#4.wav", name_to_midi('D4')),
    ("samples/multisamples/uke/D4.wav", name_to_midi('Db4')),
    ("samples/multisamples/uke/E4.wav", name_to_midi('Eb4')),
    ("samples/multisamples/uke/F#4.wav", name_to_midi('F4')),
    ("samples/multisamples/uke/F4.wav", name_to_midi('E4')),
    ("samples/multisamples/uke/G#4.wav", name_to_midi('G4')),
    ("samples/multisamples/uke/G4.wav", name_to_midi('Gb4')),
]

def make_snip(retuned_pitch, duration):
	"""
	Pick a random sound.  Retune it to retuned_pitch, shift it so its midpoint
	happens at duration/2 and apply a splice to fade in and out...
	"""
	path, orig_pitch = random.choice(sound_lib)
	pe = Pitched(orig_pitch, path).retune(retuned_pitch)
	midpoint = int(pe.extent().duration()/2)
	# shift midpoint - duration/2 to be at t=0
	pe = pg.TimeShiftPE(pe, int(duration/2 - midpoint)).crop(pg.Extent(0, duration))
	# pe now starts at time 0, ends a duration.
	print(midpoint, pe.extent())
	pe = pg.SplicePE(pe, int(duration/3), int(duration/3))
	# pe now starts at t=0, fades in over duration/4, full volume for duration/2
	# fades out over duration/4 and ends at duration.
	return pe

def notary_pe(pe, duration, legato, splice_dur):
    """
    Apply a duration and 'legato' to an existing pe, where a legato of 1.0 means
    to fill out the entire duration.  Assumes that the source note starts at t=0
    (or before), creates a splice that is 50% ramped up at t=0 and 50% ramped
    down at t=(duration * legato)
    """
    s = 0 - (splice_dur / 2.0)
    e = (duration * legato) + (splice_dur / 2.0)
    return pe.crop(pg.Extent((int)s, (int)e)).splice(splice_dur, splice_dur)

def thrumm_pe(duration, midi_pitch):
    """
    Create a nice deep bass note that varies with each rendering.
    """
    #    ("samples/multisamples/Ambibell/Ambibell-048-c2.wav", name_to_midi('c2')),
    #    ("samples/multisamples/Autoharp_Binaural/Autoharp_Binaural_C1.wav", name_to_midi('C1')),
    #    ("samples/multisamples/Autoharp_Mute/Autoharp_Mute_C2.wav", name_to_midi('C1')),
    #    ("samples/multisamples/Bandura_Soft/Bandura_Soft_A1.wav", name_to_midi('A1')),
    #    ("samples/multisamples/Cheng_Hard/Cheng_Hard_1-C2.wav", name_to_midi('C2')),
    # ("samples/multisamples/Choir_Female_Ah/Choir_Female_Ah_pp_1_B2.wav", name_to_midi('B2')),
    # ("samples/multisamples/Choir_Female_Ah/Choir_Female_Ah_pp_1_B3.wav", name_to_midi('B3')),
    # ("samples/multisamples/Choir_Female_Ah/Choir_Female_Ah_pp_1_F4.wav", name_to_midi('F4')),
    # ("samples/multisamples/Daphne/Daphne_C2.wav", name_to_midi('C1')),
    # ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_01-G2.wav", name_to_midi('G2')),
    # ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_03-A2.wav", name_to_midi('A2')),
    # ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_05-B2.wav", name_to_midi('B2')),
    # ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_07-C#3.wav", name_to_midi('C#3')),
    # ("samples/multisamples/Fiddle_Multi/Fiddle_Multi_10-E3.wav", name_to_midi('E3')),

    # kick candidates:
    # DP2_118_House_Pistol_Warm_Kicks
    # DP2_177_Fit_Drums
    # DTP1_Madness_HunterKick_01_127
    # Node_Drums_176_1_141bpm








    pass

class Obstinato(object):

    def __init__(self):
        pass

    def generate(self):
        t = 0
        pes = []
        return pes



piece = []
duration = int(48000*4)
retuned_pitch = name_to_midi('c1')
t = 0
for _ in range(200):
	pe = make_snip(retuned_pitch, duration)
	if pe.channel_count() == 1:
		pe = pg.SpreadPE(pe)
	piece.append(pe.time_shift(t))
	t += int(48000/8)

mix = pg.MixPE(*piece)

pg.Transport(mix).play()
