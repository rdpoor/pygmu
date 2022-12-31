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

    def __init__(self,
                 src_pe,
                 kernel_pe):
        """
        Convolution - convolve two signals

        src_pe: Sound source
        kernel_pe: signal with which to convolve
        """
        # Enforce mono sources until we expand the code to handle other cases...
        if src_pe.channel_count() != 1:
            raise pyx.ChannelCountMismatch('src_pe channel_count must equal 1')
        if kernel_pe.channel_count() != 1:
            raise pyx.ChannelCountMismatch('kernel_pe channel_count must equal 1')

        self._src_pe = src_pe
        self._kernel_pe = kernel_pe
        self._kernel_frames = kernel_pe.render(kernel_pe.extent())
        # normalize kernel amplitude
        kernel_rms = np.sqrt(np.mean(np.square(self._kernel_frames)))
        self._kernel_frames = self._kernel_frames / kernel_rms
        # Note: the code assumes kernel_pe starts at 0
        kernel_dur = kernel_pe.extent().duration()
        self._extent = Extent(src_pe.extent().start(), src_pe.extent().end() + kernel_dur -1)

    def render(self, requested:Extent):

        s = requested.start()
        e = requested.end()
        N = self._kernel_pe.extent().duration()
        # We ask the src_pe to render from s-N to e, where N is the length of the kernel.  
        # This lets the convolve function compute all the state leading up to s...e.
        src_request = Extent(s-N, e)

        overlap = src_request.intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, requested.duration(), self.channel_count())

        src = self._src_pe.render(src_request)

        # reshape frames into rows as required by signal.convolve()
        # TODO: handle multi-channel
        sig = src[:,0]
        win = self._kernel_frames[:,0]
        flt = signal.convolve(sig, win, mode='full') / 50  # what is the right nomalization?
        flt_rms = np.sqrt(np.mean(np.square(flt)))
        flt_peak = max(np.abs(flt))
        # At this point:
        #  sig has frames from [s-N ... e] (length e-s+N)
        #  win has frames from [0 ... N] (length N)
        #  flt has frames from [s-N ... e + 2N -1] (length e - s + N + N - 1)
        # We want to return the frames corresponding to [s ... e] (length e-s)  
        # Trim and shape back into frames
        flt = flt[N:N+(e-s)]
        dst = flt.reshape(-1, 1)
        return dst

    def extent(self):
        return self._extent

    def channel_count(self):
        return max(self._src_pe.channel_count(), self._kernel_pe.channel_count())

    def frame_rate(self):
        return self._src_pe.frame_rate()

