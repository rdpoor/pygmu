import numpy as np
from scipy import signal
from extent import Extent
from pyg_pe import PygPE
import pyg_exceptions as pyx
import utils as ut

class CombPE(PygPE):
    """
    Comb filter, peaking or notching
    """

    PEAK = 'peak'
    NOTCH = 'notch'

    def __init__(self, 
                 src_pe, 
                 f0=440, 
                 q=20, 
                 filter_type='peak', 
                 pass_zero=False,
                 frame_rate=None):
        """
        Comb filter.
        """
        super(CombPE, self).__init__()
        self._src_pe = src_pe
        self.set_frame_rate(frame_rate, src_pe)
        fs = self.frame_rate()
        # f0 must divide evenly into frame rate
        f0a = fs / max(round(fs / f0), 1)
        # if f0 != f0a:
        #     print('adjusting f0 from', f0, 'to', f0a)
        self._b, self._a = signal.iircomb(f0a, q, ftype=filter_type, fs=fs, pass_zero=pass_zero)
        # filter initial state (carried over between calls to render)
        self._zinit = np.zeros((self.channel_count(), max(len(self._b), len(self._a))-1), dtype=np.float32)

    def render(self, requested:Extent):
        overlap = self._src_pe.extent().intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, self.channel_count(), requested.duration())

        src_frames = self._src_pe.render(requested)
        x = src_frames
        y, self._zinit = signal.lfilter(self._b, self._a, x, zi=self._zinit)
        return y

    def extent(self):
        return self._src_pe.extent()

    def channel_count(self):
        return self._src_pe.channel_count()

    def frame_rate(self):
        return self._frame_rate

    def set_frame_rate(self, frame_rate, src_pe):
        """
        Enforce setting of frame_rate, either from keyword arg or from source_pe.
        If both are specified, print a warning on mismatch but honor keyword arg.
        """
        self._frame_rate = frame_rate or src_pe.frame_rate()
        if self._frame_rate is not None:
            if src_pe.frame_rate() is not None and src_pe.frame_rate() != self._frame_rate:
                print("CompPE warning: overriding input frame_rate of {} with {}".format(
                    src_pe.frame_rate(), frame_rate))
        else:
            if src_pe.frame_rate() is None:
                # neither specifies frame rate -- cannot proceed
                raise pyx.FrameRateMismatch("frame rate must be specified")

