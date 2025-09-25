"""
TimeShiftPE - time varying delay
"""

import numpy as np
from extent import Extent
from pyg_pe import PygPE
import pyg_exceptions as pyx

class TimeShiftPE(PygPE):
	"""
	Delay by a fixed or variable number of frames.
	"""

	def __init__(self, src_pe:PygPE, delay=0):
	    super(TimeShiftPE, self).__init__()
	    self._src_pe = src_pe
	    self._delay = delay
	    if isinstance(delay, PygPE):
	    	# With variable delay, the resulting extent is indefinite
	    	self._extent = Extent()
	    	if delay.channel_count() != 1:
	    		raise pyx.ChannelCountMismatch("delay input must be single channel")
	    		pass
	    else:
			# With a fixed delay, the resulting extent is src extent shifted.
	    	self._extent = src_pe.extent().offset(delay)

	def render(self, requested:Extent):
		if isinstance(self._delay, int):
			# fixed, integer delay requires no interpolation
			return self._src_pe.render(requested.offset(-self._delay)) 

		elif isinstance(self._delay, PygPE):
			# time-varying delay
			delays = self._delay.render(requested).reshape(-1)

		else:
			# fixed, but fractional delay
			delays = self._delay

		times = np.arange(requested.start(), requested.end()) - delays
		t0 = int(np.floor(min(times)))
		t1 = int(np.floor(max(times))) + 1
		src_frames = self._src_pe.render(Extent(t0, t1+1))
		dst_channels = []
		for channel in src_frames:
			delayed_channel = np.interp(times, np.arange(t0, t1+1), channel)
			dst_channels.append(delayed_channel)
		dst_frames = np.hstack(dst_channels)
		# d1 = dst_frames.shape
		dst_frames = dst_frames.reshape(self.channel_count(), -1)
		# d2 = dst_frames.shape
		# print("d1, d2", d1, d2)
		return dst_frames

	def extent(self):
	    return self._extent

	def frame_rate(self):
	    return self._src_pe.frame_rate()

	def channel_count(self):
	    return self._src_pe.channel_count()
