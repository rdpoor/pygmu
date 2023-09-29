import numpy as np
from pyg_pe import PygPE
from extent import Extent

class PygGen(PygPE):
    """
    PygGen is the abstract base class for all Generator Processing Elements.
    """

    def __init__(self, frame_rate=None):
        super(PygGen, self).__init__()
        self._frame_rate = frame_rate

    def frame_rate(self):
        """
        Return the frame rate of this PE.
        """        
        return self._frame_rate

class FrequencyMixin:
    def set_frequency(self, frequency):
        if isinstance(frequency, PygGen):
            if frequency.channel_count() != 1:
                raise pyx.ChannelCountMismatch("dynamic frequency source must be single channel")
            self._dynamic_frequency = frequency
            self._static_frequency = None
        else:
            self._dynamic_frequency = None
            self._static_frequency = frequency

    def get_frequency(self, requested=None):
        if self._dynamic_frequency is not None:
            return self._dynamic_frequency.render(requested).reshape(-1)  # convert to 1D array
        return self._static_frequency
