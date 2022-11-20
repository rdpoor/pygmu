from pyg_pe import PygPE
from extent import Extent
from array_pe import ArrayPE
import utils as ut
import numpy as np

class GaneshPE(PygPE):
	"""
	Use the phase info from one PE and the magnitude into from another PE to 
	create an 'elephant head on a human body' (or any other combination).  

	NOTE: Since it is performing FFT of entire PEs in memory, the extent
	of the input PEs can't be too large...
	"""

	def __init__(self, head_pe, body_pe, extend=True):
		"""
		Extract the magnitude information from head and the phase info from
		body, then combine them to make a new sound.  If extend is true, then
		zero pad the shorter of the two inputs before processing, else truncate
		the longer to match the length of the shorter.
		"""
		super(GaneshPE, self).__init__()
		self._head_pe = head_pe
		self._body_pe = body_pe
		head_frames = head_pe.render(head_pe.extent())
		body_frames = body_pe.render(body_pe.extent())
		ganesh_frames = self.ganeshify(head_frames, body_frames, extend)
		# Create an ArrayPE to render the results.
		self._array_pe = ArrayPE(ganesh_frames, self.channel_count())

	def render(self, requested:Extent):
		return self._array_pe.render(requested)

	def extent(self):
		return self._array_pe.extent()

	def channel_count(self):
		# TODO: check head_pe.channel_count() == body_pe.channel_count()
		return self._head_pe.channel_count()

	def ganeshify(self, head_frames, body_frames, extend):
		delta = len(head_frames) - len(body_frames)
		if delta < 0:
			if extend:
				# head is shorter than body: zero pad head
				head_frames = np.concatenate(
					(head_frames, ut.const_frames(0.0, -delta, head_frames.shape[1])))
			else:
				# head is shorter than body: truncate body
				body_frames = body_frames[0:-delta,:]
		elif delta > 0:
			if extend:
				# head is longer than body: zero pad body
				body_frames = np.concatenate(
					(body_frames, ut.const_frames(0.0, delta, body_frames.shape[1])))
			else:
				# head is longer than body: truncate head
				head_frames = head_frames[0:delta,:]
		# We now have two equally sized arrays.  process them...
		head_magnitudes, _ = self.analyze(head_frames)
		_, body_phases = self.analyze(body_frames)
		return self.synthesize(head_magnitudes, body_phases)

	def analyze(self, frames):
		"""
		Take the FFT of the given frames, return a duple of (magnitudes, phases)
		"""
		analysis = np.fft.fft(frames.transpose())
		return ut.complex_to_magphase(analysis)

	def synthesize(self, magnitudes, phases):
		"""
		Given an array of magnitudes and phases, take the iFFT and return the
		real component.
		"""
		analysis = ut.magphase_to_complex(magnitudes, phases)
		return np.real(np.fft.ifft(analysis)).transpose()
