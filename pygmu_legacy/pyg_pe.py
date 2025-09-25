import numpy as np
from extent import Extent
import random

class PygPE(object):
    """
    PygPE is the abstract base class for all Processing Elements.
    """

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
        Return the frame rate of this PE.
        """        
        return None

    def channel_count(self):
        """
        Return the number of channels produced by this PE.
        """        
        return None

    # is there a way to migrate these to a different file?

    def abs(self):
        return pg.AbsPE(self, delay)

    def add(self, other_pe):
        return pg.AddPE(self, other_pe)

    def biquad(self,gain,freq,q,type):
        return pg.BiquadPE(self, gain, freq, q, type)

    def cache(self):
        return pg.CachePE(self)

    def chorus(self, rate=1.5, depth=0.5, mix=0.5):
        return pg.ChorusPE(self, rate=rate, depth=depth, mix=mix)
    
    def delays(self, secs=0.5, howmany = 1, decay = 0.8, width = 0.8):
        delay_units = []
        #amp = 1 / howmany #scale to avoid clipping
        amp = 1
        pan_degrees = 90 * width
        for i in range(1, howmany):
            delay_units.append(self.time_shift(int(i * secs * self.frame_rate())).gain(amp).pan(random.uniform(-pan_degrees,pan_degrees)))
            amp *= decay
        return pg.MixPE(self,*delay_units)
    
    def lowpass(self, f0=330, q=10):
        return pg.BQ2LowPassPE(self, f0=f0, q=q)

    def highpass(self, f0=330, q=10):
        return pg.BQ2HighPassPE(self, f0=f0, q=q)

    def bandpass(self, f0=830, q=4):
        return pg.BQ2BandPassPE(self, f0=f0, q=q)

    def crop(self, extent, fade_in=0, fade_out=0):
        if fade_in > 0:
            if fade_out == 0:
                fade_out = fade_in
            return pg.CropPE(self, extent).splice(fade_in, fade_out)
        return pg.CropPE(self, extent)

    def time_shift(self, delay):
        return pg.TimeShiftPE(self, delay)

    def mul(self, fac):
        return pg.MulPE(self, fac)

    def gain(self, fac):
        return pg.MulPE(self, pg.ConstPE(fac))

    def fts_play(self):
        return pg.FtsTransport(self).play()

    def gain(self, ratio):
        return pg.GainPE(self, ratio)

    def granular(self, grain_size=0.1, grain_overlap=0.5):
        return pg.GranularPE(self, grain_size=grain_size, grain_overlap=grain_overlap)

    def interpolate(self, speed_mult):
        return pg.InterpolatePE(self, speed_mult)

    def exp_lim(self, target_amp=1.0, release_time=0.1):
        return pg.ExpanderLimiterPE(self, target_amp=target_amp, release_time=release_time)

    def limit_a(self, threshold_db=-10, headroom_db=3):
        return pg.LimiterAPE(self, threshold_db=threshold_db, headroom_db=headroom_db)

    def loop(self, loop_length):
        return pg.LoopPE(self, loop_length)

    def mono(self, attenuation=1.0):
        return pg.MonoPE(self, attenuation=attenuation)

    def normalize(self, release_time=0.6):
        return pg.NormalizePE(self, release_time=release_time)

    def stereo(self):
        return pg.StereoPE(self)

    def pad(self, front_pad_frames=0,rear_pad_frames=0):
        if front_pad_frames > 0:
            shifted_src = pg.TimeShiftPE(self, front_pad_frames)
        else:
            shifted_src = self
        silence = pg.ArrayPE([[0]])
        shifted_silence = pg.TimeShiftPE(silence, front_pad_frames + self.extent().end() + rear_pad_frames)
        padded_audio = pg.MixPE(shifted_src, shifted_silence)
        return padded_audio


    def pan(self, degree=0):
        return pg.SpatialPE(self, degree=degree)

    def play(self):
        return pg.Transport(self).play()
    
    def pygplay(self, title=False, auto_start=True):
        dst = pg.WavWriterPE(self, "user_files/renders/pygplay_tmp.wav")
        pg.FtsTransport(dst).play()
        new_src = pg.WavReaderPE("user_files/renders/pygplay_tmp.wav")
        player = pg.PygPlayer(title=title, auto_start=auto_start)
        player.t2 = pg.T2(new_src)
        player.t2.now_playing_callback = player.now_playing_callback
        player.root.mainloop()
        if player.exit_script_flag:
            exit()

    def speed(self, speed):
        return pg.WarpSpeedPE(self, speed)
    
    def reverb(self, wetness=0.5, ir_name='Conic Long Echo Hall.wav', ir_path='samples/IR/'):
        impulse = pg.WavReaderPE(ir_path + ir_name)
        how_wet = wetness * wetness / 2
        wet = pg.ConvolvePE(self.gain(0.28), impulse).gain(how_wet)
        return pg.MixPE(self.gain(1.0 - how_wet), wet)

    def reverse(self, infinite_end):
        return pg.ReversePE(self, infinite_end)

    def splice(self, up_dur, dn_dur):
        return pg.SplicePE(self, up_dur, dn_dur)

    def spread(self, channel_count=2):
        return pg.SpreadPE(self, channel_count=channel_count)

    def timewarp(self, timeline_pe):
        return pg.TimewarpPE(self, timeline_pe)
        
    def tralfam(self):
        return pg.TralfamPE(self)

    def warp_speed(self, rate, frame=0):
        return pg.WarpSpeedPE(self, rate)
    
    def wav_writer(self, filename):
        return pg.WavWriterPE(self, filename)

    def waveshape(self, filename):
        return pg.WaveShapePE(self, filename)

import pygmu as pg # down here to avoid a circular dependency
