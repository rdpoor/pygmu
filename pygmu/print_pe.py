import numpy as np
from pygmu.extent import Extent
from pygmu.pyg_pe import PygPE

class PrintPE(PygPE):
    """
    Print out frames as they go by...
    """

    def __init__(self, src_pe:PygPE):
        super(PrintPE, self).__init__()
        self._src_pe = src_pe

    def render(self, requested:Extent):
        buf = self._src_pe.render(requested)
        print("requested=", requested, "self.channel_count()=", self.channel_count())
        print(buf)
        return buf

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
