import numpy as np
from scipy import signal
from extent import Extent
from pyg_pe import PygPE
import utils as ut
import pyg_exceptions as pyx

class ConvolvePE(PygPE):
    """
    Convolution
    """

    def __init__(self, src_pe, filter_pe):
        """
        Convolution - convolve two signals

        src_pe: Sound source
        filter_pe: filter (e.g. impulse) with which to convolve
        """
        # Validate channel counts
        if src_pe.channel_count() > 2:
            raise pyx.ChannelCountMismatch('src_pe channel_count must be 1 or 2')
        if filter_pe.channel_count() > 2:
            raise pyx.ChannelCountMismatch('filter_pe channel_count must be 1 or 2')

        self._src_pe = src_pe
        self._filter_pe = filter_pe
        # The filter is constant, so fetch its data at initialization
        self._filter_frames = filter_pe.render(filter_pe.extent())
        # normalize filter amplitude
        filter_rms = np.sqrt(np.mean(np.square(self._filter_frames)))
        self._filter_frames = self._filter_frames / filter_rms
        filter_dur = filter_pe.extent().duration()
        self._extent = Extent(src_pe.extent().start(), src_pe.extent().end() + filter_dur -1)

    def render(self, requested:Extent):

        s = requested.start()
        e = requested.end()
        N = self._filter_pe.extent().duration()
        # We ask the src_pe to render from s-N to e, where N is the length of the filter.  
        # This lets the convolve function compute all the state leading up to s...e.
        src_request = Extent(s-N, e)

        overlap = src_request.intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, requested.duration(), self.channel_count())

        src_frames = self._src_pe.render(src_request)

        if self._src_pe.channel_count() == 1 and self._filter_pe.channel_count() == 1:
            # mono source, mono filter: mono result
            dst_frames = self.process(src_frames[:,0], self._filter_frames[:,0]).reshape(-1, 1)

        elif self._src_pe.channel_count() == 2 and self._filter_pe.channel_count() == 1:
            # stereo source, mono filter: stereo result
            l_frames = self.process(src_frames[:,0], self._filter_frames[:,0])
            r_frames = self.process(src_frames[:,1], self._filter_frames[:,0])
            dst_frames = np.vstack((l_frames, r_frames)).T

        elif self._src_pe.channel_count() == 1 and self._filter_pe.channel_count() == 2:
            # mono source, stereo filter: stereo result
            l_frames = self.process(src_frames[:,0], self._filter_frames[:,0])
            r_frames = self.process(src_frames[:,0], self._filter_frames[:,1])
            dst_frames = np.vstack((l_frames, r_frames)).T

        else:
            # stereo source, stereo filter: stereo result
            l_frames = self.process(src_frames[:,0], self._filter_frames[:,0])
            r_frames = self.process(src_frames[:,1], self._filter_frames[:,1])
            dst_frames = np.vstack((l_frames, r_frames)).T

        # At this point, dst_Frames contains N samples before the requested start (the length
        # of the filter, and frames past the requested end.  slice to the requested size.
        return dst_frames[N:N+(e-s),:]

    def extent(self):
        return self._extent

    def channel_count(self):
        return max(self._src_pe.channel_count(), self._filter_pe.channel_count())

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def process(self, src_samples, filter_samples):
        """
        Convolve source with filter.
        src_samples: a 1D array of source samples (shape = (M,))
        filter_samples: a 1D array of filter samples (shape = (N,))
        returns a 1D array of convolved data (shape = (D,))

        Note 1: We use the parameter name "src_samples" and "filter_samples" (rather than frames)
        to reflect the fact that these are 1D arrays, not pygmu frames.
        """
        filtered_samples = signal.convolve(src_samples, filter_samples, mode='full')
        filtered_samples /= 50      # what is the right normalization?
        return filtered_samples

