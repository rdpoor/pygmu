import numpy as np
from extent import Extent
from pyg_pe import PygPE

class PrintPE(PygPE):
    """
    Print out frames as they go by...
    """

    def __init__(self, src_pe:PygPE):
        super(PrintPE, self).__init__()
        self._src_pe = src_pe

    def render(self, requested:Extent, n_channels:int):
        buf = self._src_pe.render(requested, n_channels)
        print("requested=", requested, "n_channels=", n_channels)
        print(buf)
        return buf
