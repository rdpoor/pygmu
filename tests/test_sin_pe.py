import unittest
import numpy as np
import os
import sys

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pyg_exceptions as pyx
from pygmu import (SinPE, Extent, PygPE)


FRAME_RATE = 48000

class TestSinPE(unittest.TestCase):

    def test_init(self):
        pe = SinPE(frame_rate=FRAME_RATE)
        self.assertIsInstance(pe, SinPE)
        self.assertTrue(pe.extent().is_indefinite())
        self.assertEqual(pe.frame_rate(), FRAME_RATE)
        self.assertEqual(pe.channel_count(), 1)

        with self.assertRaises(pyx.FrameRateMismatch):
            # Frame rate is required
            SinPE()

    def test_render(self):
        e = Extent(0, 5)
        # DC
        pe = SinPE(frequency=0, frame_rate=FRAME_RATE)
        expect = np.array([[0, 0, 0, 0, 0]])
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(0, 5)
        # Nyquist
        pe = SinPE(frequency=FRAME_RATE/2, frame_rate=FRAME_RATE)
        expect = np.array([[0, 0, 0, 0, 0]])
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(0, 5)
        # Nyqyist/2
        pe = SinPE(frequency=FRAME_RATE/4, frame_rate=FRAME_RATE)
        expect = np.array([[0, 1.0, 0, -1.0, 0]])
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(0, 5)
        # Nyqyist/2, amplitude = 0.5
        pe = SinPE(frequency=FRAME_RATE/4, amplitude=0.5, frame_rate=FRAME_RATE)
        expect = np.array([[0, 0.5, 0, -0.5, 0]])
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(0, 5)
        # Nyqyist/2, phase = pi/2 (cosine)
        pe = SinPE(frequency=FRAME_RATE/4, phase=np.pi/2, frame_rate=FRAME_RATE)
        expect = np.array([[1.0, 0., -1.0, 0, 1.0]])
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        # already tested
        pass

    def test_frame_rate(self):
        # already tested
        pass

    def test_channel_count(self):
        # alredy tested
        pass
