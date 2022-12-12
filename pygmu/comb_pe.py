import numpy as np
from scipy import signal
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class CombPE(PygPE):
    """
    Comb filter, peaking or notching
    """

    PEAK = 'peak'
    NOTCH = 'notch'

    def __init__(self, src_pe, f0=440, q=20, filter_type='peak', pass_zero=False):
        """
        Comb filter.
        """
        super(CombPE, self).__init__()
        self._src_pe = src_pe
        fs = src_pe.frame_rate()
        # f0 must divide evenly into frame rate
        f0a = fs / round(fs / f0)
        if f0 != f0a:
            print('adjusting f0 from', f0, 'to', f0a)
        self._b, self._a = signal.iircomb(f0a, q, ftype=filter_type, fs=fs, pass_zero=pass_zero)
        # filter initial state (carried over between calls to render)
        self._zinit = np.zeros((self.channel_count(), max(len(self._b), len(self._a))-1), dtype=np.float32)

    def render(self, requested:Extent):
        overlap = self._src_pe.extent().intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, requested.duration(), self.channel_count())

        src_frames = self._src_pe.render(requested)
        x = src_frames.transpose()  # as expected by sosfilt
        y, self._zinit = signal.lfilter(self._b, self._a, x, zi=self._zinit)
        return y.transpose()

    def extent(self):
        return self._src_pe.extent()

    def channel_count(self):
        return self._src_pe.channel_count()

    def frame_rate(self):
        return self._src_pe.frame_rate()
