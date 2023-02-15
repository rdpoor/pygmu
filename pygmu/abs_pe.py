import numpy as np
from extent import Extent
from pyg_pe import PygPE

class AbsPE(PygPE):
    """
    Take the absolute value of the input PE
    """

    def __init__(self, src:PygPE):
        """
        Parameters
        ----------
        src : PygPE
            A source stream

        Returns:
        --------
        PygPE
            A stream that renders the absolute value of the source stream.
        """
        super(AbsPE, self).__init__()
        self._src_pe = src

    def render(self, requested:Extent):
        return np.abs(self._src_pe.render(requested))

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
