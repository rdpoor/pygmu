import numpy as np
import extent as Extent
import sys
import utils as ut

class FtsTransport(object):
    """
    Render frames as fast as possible without audio playback.
    """

    def __init__(self, src_pe):
        self._src_pe = src_pe
        self._use_ansi = ut.terminal_has_ansi_support()

    def play(self):
        extent = self._src_pe.extent()
        frame_rate = self._src_pe.frame_rate()
        dur_str = 'file duration: {0:.2f} '.format(extent.end() / frame_rate)
        if extent.is_indefinite():
            s = 0
        else:
            s = int(extent.start())
        ut.show_cursor(False)
        while s < extent.end():
            e = int(min(extent.end(), s + frame_rate)) # render up to 1 second
            prog_str = '{0:.0%} '.format(float(s) / extent.end())
            if self._use_ansi:
                print(dur_str,prog_str, end="\r")
            else:
                print('{0:.0%} '.format(float(s) / extent.end()),end="")
            sys.stdout.flush()
            self._src_pe.render(Extent.Extent(s, e))
            s = e
        ut.show_cursor(True)
        print("100%", end="\r" if self._use_ansi else "\n")
