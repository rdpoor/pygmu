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

BPM = 128
BPS = BPM/60.0

class Tobin(object):

	def __init__(self, duration, *tobins):
		self._duration = duration
		self._tobins = tobins

	def duration(self):
		return self._duration

	def gen_pes(self):
		pes = []
		for start_time, tobin in tobins:
			if isinstance(tobin, pg.PygPE):
				pe = tobin
			else:
				pe = tobin.gen_pes()
			pes.append(pe.time_shift(start_time * self._duration))
		return pg.Mix(*pes)


BPM_RE = re.compile(r".*?(\d+)bpm")

def one_beat(wavfile_name, n):
	"""
	Extract the n'th beat from a .wav file, using NNNbpm in the filename and the
	sampling rate of the file to determine the crop values.  If the bpm cannot
	be determined, return None.
	"""
	print(wavfile_name)
	m = BPM_RE.match(wavfile_name)
	if m is None:
		return None   # unknown BPM
	bpm = int(m[1])

	wav_pe = pg.WavReaderPE(wavfile_name)
	frames_per_beat = wav_pe.frame_rate() * 60 / bpm
	return wav_pe.crop(pg.Extent(int(n*frames_per_beat), 
		                         int((n+1)*frames_per_beat))).cache()

def load_up():
	files = (
        'samples/04_TP2_Hats_130bpm.wav',
        'samples/09a07tek147bpm.wav',
        'samples/09c02nse179bpm.wav',
        'samples/09c03nse179bpm.wav',
        'samples/09e03prc158bpm.wav',
        'samples/09r02tek143bpm.wav',
        'samples/09v06vfx150bpm.wav',
        'samples/AcousticDrumLoopsSiggi_Track22_92bpm.wav',
        'samples/AcousticDrumLoopsSiggi_Track47_104bpm.wav',
        'samples/BigBeat120bpm10.wav',
        'samples/BigBeat4_BigBeat5drumloops120bpm.04.wav',
        'samples/Clicky Pitched Kick Loop 105bpm.wav',
        'samples/Clicky Sticks 94bpm.wav',
        'samples/Elements 01_120bpm.wav',
        'samples/Elements 07_115bpm.wav',
        'samples/F9_TH_Live_Hat_60bpm_B.wav',
        'samples/F9THbass90bpmDmin.wav',
        'samples/LFO Clicky Kick 94bpm.wav',
        'samples/Node_Drums_147_1_159bpm.wav',
        'samples/Node_Drums_154_1_120bpm.wav',
        'samples/Node_Drums_158_4_165bpm.wav',
        'samples/Node_Drums_176_1_141bpm.wav',
        'samples/Odd Resonant Triplets 128bpm.wav',
        'samples/ping pong percs 120bpm.wav',
        'samples/Pitched Kick Loop 105bpm.wav',
        'samples/PRSM_Perc_Loop_21_120bpm.wav',
        'samples/Shifting Hats 94bpm.wav',
        'samples/SSOW_80bpm_DrumLoops10_FullLoop1.wav',
        'samples/SSOW_80bpm_DrumLoops9_TopLoop1.wav',
        'samples/SSOW_80bpm_FXLoop_NiceDelats.wav',
        'samples/SSOW_D_80bpm_BassLoops_ButterBass.wav',
        'samples/SSOW_E_80bpm_BassLoops_TickyTickySub.wav',
        'samples/Tock Spring 92bpm.wav',
        'samples/Tock Spring FX 92bpm.wav',
        'samples/TPT_Agogo_128bpm_Loop_20.wav',
        'samples/TPT_Agogo_128bpm_Loop_22.wav',
        'samples/TPT_Berimbau Gunga_125bpm_Loop_01.wav',
        'samples/TPT_Berimbau Gunga_125bpm_Loop_10.wav',
        'samples/TPT_Congas_128bpm_Loop_28.wav',
        'samples/TPT_Congas_128bpm_Loop_29.wav',
        'samples/TPT_Congas_130bpm_Loop_58.wav',
        'samples/TPT_Congas_130bpm_Loop_59.wav',
        'samples/TPT_Cow Bell_126bpm_Loop_10.wav',
        'samples/TPT_Cow Bell_126bpm_Loop_14.wav',
        'samples/TPT_Cuica_128bpm_Loop_22.wav',
        'samples/TPT_Cuica_128bpm_Loop_23.wav',
        'samples/TPT_Djembe_125bpm_Loop_04.wav',
        'samples/TPT_Djembe_125bpm_Loop_05.wav',
        'samples/TPT_Djembe_125bpm_Loop_10.wav',
        'samples/TPT_Djembe_125bpm_Loop_11.wav',
        'samples/TPT_Dynamite Shaker_128bpm_Loop_25.wav',
        'samples/TPT_Dynamite Shaker_130bpm_Loop_41.wav',
        'samples/TPT_Egg Shaker_126bpm_Loop_12.wav',
        'samples/TPT_Egg Shaker_126bpm_Loop_13.wav',
        'samples/TPT_Jam Block_126bpm_Loop_11.wav',
        'samples/TPT_Jam Block_128bpm_Loop_17.wav',
        'samples/TPT_Pandeiro Synthetic_125bpm_Loop_08.wav',
        'samples/TPT_Pandeiro Synthetic_128bpm_Loop_40.wav',
        'samples/TPT_Pandeiro Synthetic_128bpm_Loop_44.wav',
        'samples/TPT_Talking Drum_130bpm_Loop_60.wav',
        'samples/TPT_Talking Drum_130bpm_Loop_61.wav',
        'samples/Xstatic3_RaveTechno_02HouseLoops112bpm.20.wav')
	t = 0
	pes = []
	for f in files:
		pe = one_beat(f, 0)
		pes.append(pe.time_shift(t))
		t += pe.extent().duration()
	for f in files:
		pe = one_beat(f, 1)
		pes.append(pe.time_shift(t))
		t += pe.extent().duration()
	return pg.MixPE(*pes)

pg.Transport(load_up()).play()

