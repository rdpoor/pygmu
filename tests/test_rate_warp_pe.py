import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ConstPE, Extent, IdentityPE, RateWarpPE)


class TestRateWarpPE(unittest.TestCase):

    def setUp(self):
        self.extent = Extent(0, 10)
        self.identity = IdentityPE(frame_rate=1234)

    def test_init(self):
        # with constant rate
        rate = 2.0
        pe = RateWarpPE(self.identity, rate)
        self.assertIsInstance(pe, RateWarpPE)

        # with dynamic rate
        rate = ConstPE(2.0)
        pe = RateWarpPE(self.identity, rate)
        self.assertIsInstance(pe, RateWarpPE)

    def test_render_p0r5_f0(self):
        # constant rate, default starting frame
        rate = 0.5
        pe = RateWarpPE(self.identity, rate)
        expect = np.array([[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p1r0_f0(self):
        # constant rate, default starting frame
        rate = 1.0
        pe = RateWarpPE(self.identity, rate)
        expect = np.array([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p2r0_f0(self):
        # constant rate, default starting frame
        rate = 2.0
        pe = RateWarpPE(self.identity, rate)
        expect = np.array([[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p4r0_f0(self):
        # constant rate, default starting frame
        rate = 4.0
        pe = RateWarpPE(self.identity, rate)
        expect = np.array([[0, 4, 8, 12, 16, 20, 24, 28, 32, 36]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m0r5_f0(self):
        # constant rate, default starting frame
        rate = -0.5                       # deeps flah
        pe = RateWarpPE(self.identity, rate)
        expect = np.array([[0, -0.5, -1, -1.5, -2, -2.5, -3, -3.5, -4, -4.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m1r0_f0(self):
        # constant rate, default starting frame
        rate = -1.0                       # deeps lamron
        pe = RateWarpPE(self.identity, rate)
        expect = np.array([[0, -1, -2, -3, -4, -5, -6, -7, -8, -9]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m2r0_f0(self):
        # constant rate, default starting frame
        rate = -2.0
        pe = RateWarpPE(self.identity, rate)
        expect = np.array([[0, -2, -4, -6, -8, -10, -12, -14, -16, -18]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m4r0_f0(self):
        # constant rate, default starting frame
        rate = -4.0
        pe = RateWarpPE(self.identity, rate)
        expect = np.array([[0, -4, -8, -12, -16, -20, -24, -28, -32, -36]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p0r5_f100p5(self):
        # constant rate, starting frame=100.5
        rate = 0.5
        pe = RateWarpPE(self.identity, rate, frame=100.5)
        expect = np.array([[100.5, 101, 101.5, 102, 102.5, 103, 103.5, 104, 104.5, 105]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p1r0_f100p5(self):
        # constant rate, starting frame=100.5
        rate = 1.0
        pe = RateWarpPE(self.identity, rate, frame=100.5)
        expect = np.array([[100.5, 101.5, 102.5, 103.5, 104.5, 105.5, 106.5, 107.5, 108.5, 109.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p2r0_f100p5(self):
        # constant rate, starting frame=100.5
        rate = 2.0
        pe = RateWarpPE(self.identity, rate, frame=100.5)
        expect = np.array([[100.5, 102.5, 104.5, 106.5, 108.5, 110.5, 112.5, 114.5, 116.5, 118.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p4r0_f100p5(self):
        # constant rate, starting frame=100.5
        rate = 4.0
        pe = RateWarpPE(self.identity, rate, frame=100.5)
        expect = np.array([[100.5, 104.5, 108.5, 112.5, 116.5, 120.5, 124.5, 128.5, 132.5, 136.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m0r5_f100p5(self):
        # constant rate, starting frame=100.5
        rate = -0.5                       # deeps flah
        pe = RateWarpPE(self.identity, rate, frame=100.5)
        expect = np.array([[100.5, 100, 99.5, 99, 98.5, 98, 97.5, 97, 96.5, 96]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m1r0_f100p5(self):
        # constant rate, starting frame=100.5
        rate = -1.0                       # deeps lamron
        pe = RateWarpPE(self.identity, rate, frame=100.5)
        expect = np.array([[100.5, 99.5, 98.5, 97.5, 96.5, 95.5, 94.5, 93.5, 92.5, 91.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m2r0_f100p5(self):
        # constant rate, starting frame=100.5
        rate = -2.0
        pe = RateWarpPE(self.identity, rate, frame=100.5)
        expect = np.array([[100.5, 98.5, 96.5, 94.5, 92.5, 90.5, 88.5, 86.5, 84.5, 82.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m4r0_f100p5(self):
        # constant rate, starting frame=100.5
        rate = -4.0
        pe = RateWarpPE(self.identity, rate, frame=100.5)
        expect = np.array([[100.5, 96.5, 92.5, 88.5, 84.5, 80.5, 76.5, 72.5, 68.5, 64.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p0r5_f0p5_a(self):
        # constant rate, frame is properly carried over multiple renders
        rate = 0.5
        pe = RateWarpPE(self.identity, rate, frame=0.5)
        expect = np.array([[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)
        expect = np.array([[5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p2r0_f0p5_a(self):
        # constant rate, frame is properly carried over multiple renders
        rate = 2.0
        pe = RateWarpPE(self.identity, rate, frame=0.5)
        expect = np.array([[0.5, 2.5, 4.5, 6.5, 8.5, 10.5, 12.5, 14.5, 16.5, 18.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)
        expect = np.array([[20.5, 22.5, 24.5, 26.5, 28.5, 30.5, 32.5, 34.5, 36.5, 38.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m0r5_f0p5_a(self):
        # constant rate, frame is properly carried over multiple renders
        rate = -0.5                       # deeps flah
        pe = RateWarpPE(self.identity, rate, frame=0.5)
        expect = np.array([[0.5, 0, -0.5, -1, -1.5, -2, -2.5, -3, -3.5, -4]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)
        expect = np.array([[-4.5, -5, -5.5, -6, -6.5, -7, -7.5, -8, -8.5, -9]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_m2r0_f0p5_a(self):
        # constant rate, frame is properly carried over multiple renders
        rate = -2.0
        pe = RateWarpPE(self.identity, rate, frame=0.5)
        expect = np.array([[0.5, -1.5, -3.5, -5.5, -7.5, -9.5, -11.5, -13.5, -15.5, -17.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)
        expect = np.array([[-19.5, -21.5, -23.5, -25.5, -27.5, -29.5, -31.5, -33.5, -35.5, -37.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render_p0r0_f0(self):
        # test constant rate = 0
        rate = 0.0
        pe = RateWarpPE(self.identity, rate, frame=0.5)
        expect = np.array([[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]], dtype=np.float32)
        got = pe.render(self.extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        pe = RateWarpPE(self.identity, 1.0).crop(self.extent)
        self.assertTrue(self.extent.equals(pe.extent()))

    def test_frame_rate(self):
        pe = RateWarpPE(self.identity, 1.0)
        self.assertEqual(pe.frame_rate(), 1234)

    def test_channel_count(self):
        pe = RateWarpPE(self.identity, 1.0)
        self.assertEqual(pe.channel_count(), 1)

