import os
import sys
import unittest
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
from pygmu import (Extent, MonoPE, IdentityPE, SinPE)

class TestMonoPE(unittest.TestCase):

    def test_init(self):
        src = IdentityPE();
        pe = MonoPE(src, 1.0)
        self.assertIsInstance(pe, MonoPE)

    def test_render(self):

        src = IdentityPE(channel_count=1)
        pe = MonoPE(src)
        expect = np.array([[0, 1, 2, 3, 4]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        src = IdentityPE(channel_count=2)
        pe = MonoPE(src)
        expect = np.array([[0, 2, 4, 6, 8]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        src = IdentityPE(channel_count=2)
        pe = MonoPE(src, attenuation = 0.5)
        expect = np.array([[0, 1, 2, 3, 4]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        src = IdentityPE(channel_count=1)
        expected_extent = Extent(2, 4)

        pe = MonoPE(src)
        self.assertTrue(pe.extent().equals(Extent()))  # infinite extent

        pe = MonoPE(src.crop(expected_extent))
        self.assertTrue(pe.extent().equals(expected_extent)) # src limited


    def test_frame_rate(self):
        src = SinPE(frame_rate=1234)
        pe = MonoPE(src, 1.0)
        self.assertEqual(pe.frame_rate(), 1234)

    def test_channel_count(self):
        src = IdentityPE(channel_count=2)
        pe = MonoPE(src)
        self.assertEqual(pe.channel_count(), 1)

