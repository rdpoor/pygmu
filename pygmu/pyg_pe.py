import numpy as np
from extent import Extent

class PygPE(object):
    """
    PygPE is the abstract base class for all Processing Elements.
    """

    DEFAULT_FRAME_RATE = 48000
    DEFAULT_CHANNEL_COUNT = 2

    def render(self, requested:Extent) -> (np.ndarray, int):
        """
        Instructs this Processing ELement to return an np.ndarray of sample data
        that falls within the requested Extent, and an offset that aligns the
        resulting data with the request.  May return

        Rules of render:

        [1] The caller may not modify the data returned by render(): it is owned
        by the callee.

        [2] The caller MAY request frames outside of the callee's extent.  The
        callee will normally return 0's for such frames.
        """
        return None

    def extent(self) -> Extent:
        """
        Return the time span of this processing element.  Unless overridden,
        subclasses of PygPE will return the indefinite extent.
        """
        return Extent()

    def frame_rate(self):
        """
        Return the frame rate of this PE.  If the PE has an input, it will 
        typically override this method and return the frame rate of its 
        input, but it's free to override this method as needed.
        """        
        return PygPE.DEFAULT_FRAME_RATE

    def channel_count(self):
        """
        Return the number of channels produced by this PE.  If the PE has an 
        input, it will typically override this method and return the channel
        count of its input, but it's free to override this method as needed.
        """        
        return PygPE.DEFAULT_CHANNEL_COUNT

    # is there a way to migrate these to a different file?

    def abs(self):
        return pg.AbsPE(self, delay)

    def biquad(self,gain,freq,q,type):
        return pg.BiquadPE(self, gain, freq, q, type)

    def lowpass(self, freq):
        return pg.BiquadPE(self, 0.0, freq, 6, "lowpass")

    def crop(self, extent):
        return pg.CropPE(self, extent)

    def delay(self, delay):
        return pg.DelayPE(self, delay)

    def mul(self, fac):
        return pg.MulPE(self, fac)

    def gain(self, fac):
        return pg.MulPE(self, pg.ConstPE(fac))

    def env(self, up_dur, dn_dur):
        return pg.EnvPE(self, up_dur, dn_dur)

    def fts_play(self):
        return pg.FtsTransport(self).play()

    def gain(self, ratio):
        return pg.GainPE(self, ratio)

    def interpolate(self, speed_mult):
        return pg.InterpolatePE(self, speed_mult)

    def limit_a(self, threshold_db=-10, headroom_db=3):
        return pg.LimiterAPE(self, threshold_db=threshold_db, headroom_db=headroom_db)

    def loop(self, loop_length):
        return pg.LoopPE(self, loop_length)

    def mono(self, attenuation=1.0):
        return pg.MonoPE(self, attenuation=attenuation)

    def pan(self, degree=0):
        return pg.SpatialAPE(self, degree=degree)

    def play(self):
        return pg.Transport(self).play()

    def reverse(self, infinite_end):
        return pg.ReversePE(self, infinite_end)

    def timewarp(self, timeline_pe):
        return pg.TimewarpPE(self, timeline_pe)
        
    def tralfam(self):
        return pg.TralfamPE(self)

    def wav_writer(self, filename):
        return pg.WavWriterPE(self, filename)

import pygmu as pg #down here to avoid a circular dependency
