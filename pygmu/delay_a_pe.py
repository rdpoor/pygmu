"""
DelayAPE - time varying delay

Preliminary notes:

The goal is to create a delay that supports time-varying fractional delays. 

## First thought

Implement it by creating a first order allpass section that can delay between
0.5 and 1.5 samples, use standard delay technique for the bulk delay.

Assume 0.5 <= alpha < 1.5:

eta = (1.0 - alpha) / (1.0 + alpha)
y[n] = eta * (x[n] - y[n-1]) + x(n-1)

Q: Since Y(n) is a recursive filter, how far back in time must we go get an 
accurate value for y[n-1]?

A: By brute-force simulation, the answer appears to be 5 samples.  But this 
requires recomputing eta and y[n-5, ... n] for each sample.

## Second thought

Just use linear interpolation.  Not as accurate (it's a lowpass filter), but
much faster to compute.

"""

import numpy as np
from extent import Extent
from pyg_pe import PygPE
import pyg_exceptions as pyx

class DelayAPE(PygPE):
	"""
	Delay by a fixed or variable number of frames.
	"""

	def __init__(self, src_pe:PygPE, delay=0):
	    super(DelayAPE, self).__init__()
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
	    	self._extent = src_pe.extent().offset(-delay)

	def render(self, requested:Extent):
		if isinstance(self._delay, PygPE):
			delays = self._delay.render(requested).reshape(-1)
		else:
			delays = self._delay
		times = np.arange(requested.start(), requested.end()) - delays
		min_time = min(times)
		max_time = max(times)
		t0 = int(np.floor(min(times)))
		t1 = int(np.floor(max(times))) + 1
		src_frames = self._src_pe.render(Extent(t0, t1+1))
		dst_channels = []
		for channel in src_frames.T:
			delayed_channel = np.interp(times, np.arange(t0, t1+1), channel)
			dst_channels.append(delayed_channel)
		dst_frames = np.vstack(dst_channels).T
		return dst_frames

	def extent(self):
	    return self._extent

	def frame_rate(self):
	    return self._src_pe.frame_rate()

	def channel_count(self):
	    return self._src_pe.channel_count()
