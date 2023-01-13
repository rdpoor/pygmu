import numpy as np
import scipy.signal
from extent import Extent
from pyg_pe import PygPE

class FilterPE(PygPE):

    def __init__(self, src_pe, num_poles:int, freq:np.float32):
        super(FilterPE, self).__init__()
        self._src_pe = src_pe
        frac = freq / 22020
        self._b, self._a = scipy.signal.butter(num_poles, frac)


    def render(self, requested:Extent):
        src_buf = self._src_pe.render(requested)
        filtered_channels = []
        for channel in src_buf:
            # channel is a single channel from src_buf
            # filtered_channel is the filtered version
            #
            # NOTE: using lfilter would work better, since it returns the
            # final values of the filter which can be applied on the next
            # call to render() to eliminate discontinuities.
            filtered_channel = scipy.signal.filtfilt(self._b, self._a, channel)
            filtered_channels.append(filtered_channel)
        dst_frames = np.hstack(filtered_channels)
        return dst_frames.reshape(self.channel_count(), -1)
       
    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()