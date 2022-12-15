import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class GravyPE(PygPE):
	"""
	Loop source from loop_start to loop_start + loop_duration
	"""

	def __init__(self, src_pe, window_start:float, window_duration:float, walk_rate:float, flip_flag: bool):
		super(GravyPE, self).__init__()
		self._src_pe = src_pe
		self._insk = window_start
		self._dur = window_duration
		self._walk_rate = walk_rate
		self._flip_flag = flip_flag

	def render(self, requested:Extent):
		dst_buf = ut.uninitialized_frames(requested.duration(), self.channel_count())
		dst_ndx = 0
		dst_size = requested.duration()
		nloops_so_far = np.trunc(requested.start() / self._dur)
		walk_offset = nloops_so_far * self._walk_rate
		src_ndx = requested.start() % self._dur
		while dst_ndx < dst_size:
			src_buf = self._src_pe.render(Extent(int(self._insk + walk_offset), int((self._insk + walk_offset + self._dur))))
			# limit the size of this pass to the smaller of remaining requested frames or remaining frames in the source loop
			src_size = min(dst_size - dst_ndx,min(self._dur - src_ndx, dst_size)) 
			dst_buf[dst_ndx:dst_ndx + src_size, :] = src_buf[src_ndx:src_ndx + src_size, :]
			dst_ndx += src_size
			src_ndx = 0
			#self._insk += self._walk_rate
			#print(self._insk,self._insk/self.frame_rate())
		return dst_buf

	def extent(self):
		return Extent()

	def frame_rate(self):
		return self._src_pe.frame_rate()

	def channel_count(self):
		return self._src_pe.channel_count()