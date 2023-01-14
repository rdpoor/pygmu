import os
import sys
import unittest
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
from pygmu import (Extent, GainPE, IdentityPE, SinPE)

class TestGainPE(unittest.TestCase):

    def test_init(self):
        src = IdentityPE();
        pe = GainPE(src, 1.0)
        self.assertIsInstance(pe, GainPE)

    def test_render(self):
        src = IdentityPE()

        pe = GainPE(src, 1.0)
        expect = np.array([[0, 1, 2, 3, 4]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, -2.0)
        expect = np.array([[0, -2, -4, -6, -8]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, 1.0).crop(Extent(2, 4))
        expect = np.array([[0, 0, 2, 3, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src.crop(Extent(2, 4)), 1.0)
        expect = np.array([[0, 0, 2, 3, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, src)
        expect = np.array([[0, 1, 4, 9, 16]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src.crop(Extent(2, 4)), src)
        expect = np.array([[0, 0, 4, 9, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, src.crop(Extent(2, 4)))
        expect = np.array([[0, 0, 4, 9, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        src = IdentityPE()
        expected_extent = Extent(2, 4)

        pe = GainPE(src, 1.0)
        self.assertTrue(pe.extent().equals(Extent()))  # infinite extent

        pe = GainPE(src.crop(expected_extent), 1.0)
        self.assertTrue(pe.extent().equals(expected_extent)) # src limited

        pe = GainPE(src.crop(expected_extent), src)
        self.assertTrue(pe.extent().equals(expected_extent)) # src limited

        pe = GainPE(src, src.crop(expected_extent))
        self.assertTrue(pe.extent().equals(expected_extent)) # gain limited


    def test_frame_rate(self):
        src = SinPE(frame_rate = 1234)
        pe = GainPE(src, 1.0)
        self.assertEqual(pe.frame_rate(), 1234)

    def test_channel_count(self):
        src = IdentityPE().spread(2)
        pe = GainPE(src, 1.0)
        self.assertEqual(pe.channel_count(), 2)

