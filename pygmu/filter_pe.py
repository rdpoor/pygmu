import numpy as np
import scipy.signal
from extent import Extent
from pyg_pe import PygPE

def monofy(frames):
    # Convert stero frames (2 column, N rows) into mono (one row)
    return np.dot(frames, [[0.5], [0.5]]).reshape(-1)

def sterofy(frames):
    # convert horizontal mono array into stero frames (2 columns, N rows)
    return np.dot(frames.reshape(-1, 1), [[1.0, 1.0]])


class FilterPE(PygPE):
    """
   

    """

    def __init__(self, src_pe, num_poles:int, freq:np.float32):
        super(FilterPE, self).__init__()
        self._src_pe = src_pe
        frac = freq / 22020
        self._b, self._a = scipy.signal.butter(num_poles, frac)


    def render(self, requested:Extent):
        src_buf = self._src_pe.render(requested)
        frames = scipy.signal.filtfilt(self._b, self._a, monofy(src_buf))
        f2 =sterofy(frames)
        return f2
       
    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        """
        With no inputs, default to the class definition.  With one or more inputs,
        use the frame_rate of the first input.
        """
        return self._src_pe.frame_rate()

    def channel_count(self):
        """
        With no inputs, default to the class definition.  With one or more inputs,
        use the channel_count of the first input.
        """
        return self._src_pe.channel_count()