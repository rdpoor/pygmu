import warnings
import numpy as np
from scipy import signal
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class BlitsigPE(PygPE):
    """
    Comb filter, peaking or notching
    """

    PULSE = 'pulse'
    SAWTOOTH = 'sawtooth'

    def __init__(self, frequency=440.0, n_harmonics=None, channel_count=1, frame_rate=PygPE.DEFAULT_FRAME_RATE, waveform='pulse'):
        """
        Band-limited Impulse Train (BLIT) Sawtooth
        frequency sets the frequency (in conjunction with frame rate)
        n_harmonics is the number of harmonics / 2.  Defaults to frame_rate / freq.
        """
        super(BlitsigPE, self).__init__()
        self._n_harmonics = n_harmonics
        self._channel_count = channel_count
        self._frame_rate = frame_rate
        self._waveform = waveform
        self.set_frequency(frequency)
        self._y_prev = 0.0              # previous y[i-1]

    def render(self, requested:Extent):
        """
        Band limited pulse train: y(n) = (_m / _period) * sinc(_m * n / _p)
        """
        tau = np.arange(requested.start(), requested.end()).reshape(-1, 1)
        omega = np.pi * tau / self._period

        # compute BLIT (bamd-limited impulse train)
        num = np.sin(self._m * omega)
        den = self._m * np.sin(omega)
        # Compute num/den, inhibit warnings and fix up division at or near zero
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            y = num / den
            y[np.where(abs(den) < 0.00001)] = 1.0 # fix division by zero

        # At this point, y[] is a band-limited impulse train.

        if self._waveform == self.SAWTOOTH:
            # Integrate pulse train to create a band-limited sawtooth.
            # 
            # At each period, the running sum increases by a total of _period / _m.  
            # To compensate, subtract 1 / _m at each sample.  Note that self._y_prev 
            # holds y[i-1] from previous iteration
            epsilon = 1 / self._m
            for i in range(len(y)):
                y[i] = y[i] + self._y_prev - epsilon
                self._y_prev = y[i] * 0.995
            # normalize amplitude.  TODO: what is the correct normalization factor?
            y *= self._m / self._period

        # Distribute the waveform to the desired number of channels.
        y = y.repeat(self._channel_count).reshape(-1, self._channel_count)
        return y

    def channel_count(self):
        return self._channel_count

    def frame_rate(self):
        return self._frame_rate

    def set_frequency(self, frequency):
        self._period = self._frame_rate / frequency
        if self._n_harmonics is None:
            self._m = 2 * int(np.floor(0.5 * self._period)) + 1
        else:
            self._m = 2 * int(self._n_harmonics) + 1
        # print("freq=", frequency, "frame_rate=", self._frame_rate, "period=", self._period, "m=", self._m)

