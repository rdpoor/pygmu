import unittest
import numpy as np
import os
import sys

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pyg_exceptions as pyx
from pygmu import (ConstPE, PwmPE, Extent, PygPE)

class TestPwmPE(unittest.TestCase):

    def test_init(self):
        pe = PwmPE(10, 0.5)
        self.assertIsInstance(pe, PwmPE)

        pe = PwmPE(ConstPE(10), 0.5)
        self.assertIsInstance(pe, PwmPE)

        pe = PwmPE(10, ConstPE(0.5))
        self.assertIsInstance(pe, PwmPE)

        with self.assertRaises(pyx.ChannelCountMismatch):
            PwmPE(ConstPE(10).spread(2), 0.5)

        with self.assertRaises(pyx.ChannelCountMismatch):
            PwmPE(10, ConstPE(0.5).spread(2))


    def test_render(self):
        e = Extent(0, 12)
        pe = PwmPE(10, 0.1)
        expect = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = PwmPE(10, 0.2)
        expect = np.array([[1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = PwmPE(10, 0.5)
        expect = np.array([[1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = PwmPE(10, 0.9)
        expect = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = PwmPE(4, 0.5)
        expect = np.array([[1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = PwmPE(4, 0.25)
        expect = np.array([[1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = PwmPE(period=10, duty_cycle=ConstPE(0.5))
        expect = np.array([[1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        # Period is forced to min(period, 1.0)
        pe = PwmPE(period=ConstPE(0), duty_cycle=1.0)
        expect = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        pe = PwmPE(4, 0.5)
        self.assertTrue(Extent().equals(pe.extent()))

    def test_frame_rate(self):
        pe = PwmPE(4, 0.5)
        self.assertIsNone(pe.frame_rate())
        pe = PwmPE(4, 0.5, frame_rate=1234)
        self.assertEqual(pe.frame_rate(), 1234)

    def test_channel_count(self):
        pe = PwmPE(4, 0.5)
        self.assertEqual(pe.channel_count(), 1)
