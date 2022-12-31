import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (Extent, IdentityPE, LinearRampPE, MixPE, PygPE, TimewarpPE)


class TestTimewarpPE(unittest.TestCase):

    def setUp(self):
        self.extent = Extent(0, 10)
        self.identity = IdentityPE(channel_count = 1)
        ramp = LinearRampPE(0, 10, self.extent, channel_count = 1) # normal speed
        self.pe = TimewarpPE(self.identity, ramp)

    def test_init(self):
        ramp = LinearRampPE(0, 10, self.extent, channel_count = 1) # normal speed
        pe = TimewarpPE(self.identity, ramp)
        self.assertIsInstance(pe, TimewarpPE)

    def test_render(self):
        ramp = LinearRampPE(0, 10, self.extent, channel_count = 1) # normal speed
        pe = TimewarpPE(self.identity, ramp)
        expect = np.array([[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

        ramp = LinearRampPE(0, 20, self.extent, channel_count = 1) # double speed
        pe = TimewarpPE(self.identity, ramp)
        expect = np.array([[0], [2], [4], [6], [8], [10], [12], [14], [16], [18]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

        ramp = LinearRampPE(0, 5, self.extent, channel_count = 1)  # half speed
        pe = TimewarpPE(self.identity, ramp)
        expect = np.array([[0], [0.5], [1], [1.5], [2], [2.5], [3], [3.5], [4], [4.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

        ramp = LinearRampPE(10, 0, self.extent, channel_count = 1) # deeps lamron
        pe = TimewarpPE(self.identity, ramp)
        expect = np.array([[10], [9], [8], [7], [6], [5], [4], [3], [2], [1]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        self.assertTrue(self.extent.equals(self.pe.extent()))

    def test_frame_rate(self):
        self.assertEqual(self.pe.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

    def test_channel_count(self):
        self.assertEqual(self.pe.channel_count(), 1)

