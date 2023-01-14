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
