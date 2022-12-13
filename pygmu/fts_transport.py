import numpy as np
import extent as Extent
import sys

class FtsTransport(object):
    """
    Render frames as fast as possible without audio playback.
    """

    def __init__(self, src_pe):
        self._src_pe = src_pe

    def play(self):
        extent = self._src_pe.extent()
        frame_rate = self._src_pe.frame_rate()
        if extent.is_indefinite():
            s = 0
        else:
            s = int(extent.start())

        while s < extent.end():
            e = int(min(extent.end(), s + frame_rate)) # render up to 1 second
            print('{0:.0%} '.format(float(s) / extent.end()), end="")
            sys.stdout.flush()
            self._src_pe.render(Extent.Extent(s, e))
            s = e
        print("100%")
