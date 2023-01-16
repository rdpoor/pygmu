import os
import sys
import unittest
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
from pygmu import (Extent, GainDbPE, IdentityPE, RampPE)

class TestGainDbPE(unittest.TestCase):

    def test_init(self):
        src = IdentityPE();
        pe = GainDbPE(src, 1.0)
        self.assertIsInstance(pe, GainDbPE)

    def test_render(self):
        src = IdentityPE()

        pe = GainDbPE(src, 0)
        expect = np.array([[0, 1, 2, 3, 4]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainDbPE(src, -20.00)
        expect = np.array([[0, .1, .2, .3, .4]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainDbPE(src, 20.00)
        expect = np.array([[0, 10, 20, 30, 40]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        # GainDbPE extent is shorter than src
        pe = GainDbPE(src, 0).crop(Extent(2, 4))
        expect = np.array([[0, 0, 2, 3, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        # GainDbPE extent is longer than src
        pe = GainDbPE(src.crop(Extent(2, 4)), 0)
        expect = np.array([[0, 0, 2, 3, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        # dynamic gain input
        gain_pe = RampPE(-40, 60, Extent(0, 5))  # [-40, -20, 0, 20, 40]
        pe = GainDbPE(src, gain_pe)
        expect = np.array([[0, .1, 2, 30, 400]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        # dynamic gain with no overlap
        gain_pe = RampPE(-40, 60, Extent(0, 5))  # [-40, -20, 0, 20, 40]
        pe = GainDbPE(src.crop(Extent(0, 5)), gain_pe)
        expect = np.array([[0, 0, 0, 0, 0]])
        got = pe.render(Extent(5, 10))
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        src = IdentityPE()
        expected_extent = Extent(2, 4)

        pe = GainDbPE(src, 1.0)
        self.assertTrue(pe.extent().equals(Extent()))  # infinite extent

        pe = GainDbPE(src.crop(expected_extent), 1.0)
        self.assertTrue(pe.extent().equals(expected_extent)) # src limited

        pe = GainDbPE(src.crop(expected_extent), src)
        self.assertTrue(pe.extent().equals(expected_extent)) # src limited

        pe = GainDbPE(src, src.crop(expected_extent))
        self.assertTrue(pe.extent().equals(expected_extent)) # gain limited


    def test_frame_rate(self):
        src = IdentityPE(frame_rate = 1234)
        pe = GainDbPE(src, 0)
        self.assertEqual(pe.frame_rate(), 1234)

        src = IdentityPE()
        pe = GainDbPE(src, 0)
        self.assertIsNone(pe.frame_rate())

    def test_channel_count(self):
        src = IdentityPE().spread(2)
        pe = GainDbPE(src, 1.0)
        self.assertEqual(pe.channel_count(), 2)

