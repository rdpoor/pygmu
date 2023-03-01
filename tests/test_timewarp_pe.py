import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (Extent, IdentityPE, RampPE, MixPE, PygPE, TimewarpPE)


class TestTimewarpPE(unittest.TestCase):

    def setUp(self):
        self.extent = Extent(0, 10)
        self.identity = IdentityPE(frame_rate=1234)
        ramp = RampPE(0, 10, self.extent) # normal speed
        self.pe = TimewarpPE(self.identity, ramp)

    def test_init(self):
        ramp = RampPE(0, 10, self.extent) # normal speed
        pe = TimewarpPE(self.identity, ramp)
        self.assertIsInstance(pe, TimewarpPE)

    def test_render(self):
        ramp = RampPE(0, 10, self.extent) # normal speed
        pe = TimewarpPE(self.identity, ramp)
        expect = np.array([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

        ramp = RampPE(0, 20, self.extent) # double speed
        pe = TimewarpPE(self.identity, ramp)
        expect = np.array([[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

        ramp = RampPE(0, 5, self.extent)  # half speed
        pe = TimewarpPE(self.identity, ramp)
        expect = np.array([[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

        ramp = RampPE(10, 0, self.extent) # deeps lamron
        pe = TimewarpPE(self.identity, ramp)
        expect = np.array([[10, 9, 8, 7, 6, 5, 4, 3, 2, 1]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        self.assertTrue(self.extent.equals(self.pe.extent()))

    def test_frame_rate(self):
        self.assertEqual(self.pe.frame_rate(), 1234)

    def test_channel_count(self):
        self.assertEqual(self.pe.channel_count(), 1)

