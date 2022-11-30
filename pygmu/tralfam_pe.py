from pygmu.pyg_pe import PygPE
from pygmu.extent import Extent
import pygmu.utils as ut
import numpy as np

class TralfamPE(PygPE):
    """
    Tralfamadorians are beings who exist in all times simultaneously.  This PE
    takes a (finite) PE and spreads it spectrum randomly across the entire time
    span of the PE.

    Tip of the hat to James "Andy" Moorer for suggesting the name.

    NOTE: Since it is performing an FFT of the whole PE in memory, the extent
    of the input PE can't be too large...
    """

    def __init__(self, src_pe):
        super(TralfamPE, self).__init__()
        self._src_pe = src_pe
        self.mangled_frames = None

    def render(self, requested:Extent):
        intersection = requested.intersect(self.extent())
        r0 = requested.start()
        r1 = requested.end()
        t0 = self.extent().start()
        t1 = self.extent().end()
        mogrified_frames = self.mogrify(self.channel_count())

        if intersection.is_empty():
            dst_frames = ut.const_frames(0.0, r1-r0, self.channel_count())

        elif self.extent().spans(requested):
            dst_frames = mogrified_frames[r0:r1,:]

        else:
            dst_frames = ut.uninitialized_frames(r1-r0, self.channel_count())
            dst_index = 0

            s = r0
            e = min(r1, t0)
            n = max(0, e - s)
            # generate silence before t0 starts
            if n > 0:
                dst_frames[dst_index:dst_index+n,:] = pg.const_frames(0.0, n, self.channel_count())
                dst_index += n

            s = max(r0, t0)
            e = min(r1, t1)
            n = max(0, e - s)
            # copy samples from mogrified
            if n > 0:
                dst_frames[dst_index:dst_index+n,:] = mogrified_frames[s:e,:]
                dst_index += n

            s = max(r0, t1)
            e = r1
            n = max(0, e - s)
            if n > 0:
                dst_frames[dst_index:dst_index+n,:] = ut.const_frames(0.0, n, self.channel_count())
                dst_index += n

        return dst_frames

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()

    def mogrify(self):
        if self.mangled_frames is None:
            # slurp the entirety of src_pe's data (better not be infinite!)
            frames = self._src_pe.render(self._src_pe.extent(), self.channel_count())
            n_frames = self.extent().duration()
            analysis = np.fft.fft(frames.transpose())
            magnitudes = np.abs(analysis)
            mangled_phases = np.random.default_rng().random(n_frames) * 2 * np.pi
            mangled_analysis = ut.magphase_to_complex(magnitudes, mangled_phases)
            self.mangled_frames = np.real(np.fft.ifft(mangled_analysis)).transpose()
        return self.mangled_frames
