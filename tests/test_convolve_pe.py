import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import utils as ut
import numpy as np
from scipy import signal
from pygmu import (ArrayPE, ConvolvePE, ConstPE, Extent, PygPE)

class TestConvolvePE(unittest.TestCase):

    def setUp(self):
        # Use a rectangular signal and a Hann impulse to compute a full-length convolution.
        # See https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.convolve.html
        sig = np.repeat([0., 1., 0.], 25) # len = 75
        win = signal.windows.hann(50)     # len = 50
        flt = signal.convolve(sig, win, mode='full') / sum(win) # len = 75 + 50 - 1 = 124
        # print('sig.shape=', sig.shape, 'win.shape=', win.shape, 'flt.shape=', flt.shape)


        # mono signal, mono kernel
        self.sig_1 = ArrayPE(sig.reshape(-1, 1))
        self.win_1 = ArrayPE(win.reshape(-1, 1))
        # for ease of testing, wrap the convolved result in an ArrayPE
        self.flt_1 = ArrayPE(flt.reshape(-1, 1))


    def test_init(self):
        pe = ConvolvePE(self.sig_1, self.win_1)
        self.assertIsInstance(pe, ConvolvePE)

    def test_render(self):
        # mono + mono

        # Verify that convolving the entire sig + win is correct
        requested = self.flt_1.extent()
        pe = ConvolvePE(self.sig_1, self.win_1)
        got = pe.render(requested)
        expect = self.flt_1.render(requested)
        np.testing.assert_array_almost_equal(got, expect)

        # verify that successive slices are correct
        requested = Extent(-45, 0)
        pe = ConvolvePE(self.sig_1, self.win_1)
        got = pe.render(requested)
        expect = self.flt_1.render(requested)
        np.testing.assert_array_almost_equal(got, expect)

        requested = Extent(0, 45)
        pe = ConvolvePE(self.sig_1, self.win_1)
        got = pe.render(requested)
        expect = self.flt_1.render(requested)
        np.testing.assert_array_almost_equal(got, expect)

        requested = Extent(45, 90)
        pe = ConvolvePE(self.sig_1, self.win_1)
        got = pe.render(requested)
        expect = self.flt_1.render(requested)
        np.testing.assert_array_almost_equal(got, expect)

        requested = Extent(90, 135)
        pe = ConvolvePE(self.sig_1, self.win_1)
        got = pe.render(requested)
        expect = self.flt_1.render(requested)
        np.testing.assert_array_almost_equal(got, expect)

    def test_channel_count(self):
        pe = ConvolvePE(self.sig_1, self.win_1)
        self.assertEqual(pe.channel_count(), 1)
