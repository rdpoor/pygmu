import numpy as np
import os
import sys
import unittest

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pyg_exceptions as pyx
from pygmu import (Extent, IdentityPE, WarpSpeedPE)

class TestWarpSpeedPE(unittest.TestCase):

    def setUp(self):
        self.requested = Extent(20, 30)
        self.src_pe = IdentityPE(frame_rate=1234)

    def test_init(self):
        # with constant speed
        speed = 2.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        self.assertIsInstance(pe, WarpSpeedPE)

        # with dynamic speed
        with self.assertRaises(pyx.ArgumentError):
            pe = WarpSpeedPE(self.src_pe, speed=IdentityPE())

    def test_render_p0r5(self):
        # constant speed
        speed = 0.5
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =       20,   21, 22,   23, 24,   25, 26,   27, 28,   29
        expect = np.array([[10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(pe.get_src_frame(), 15)

    def test_render_p1r0(self):
        # constant speed
        speed = 1.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =       20, 21, 22, 23, 24, 25, 26, 27, 28, 29
        expect = np.array([[20, 21, 22, 23, 24, 25, 26, 27, 28, 29]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(pe.get_src_frame(), 30)

    def test_render_p2r0(self):
        # constant speed
        speed = 2.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =       20, 21, 22, 23, 24, 25, 26, 27, 28, 29
        expect = np.array([[40, 42, 44, 46, 48, 50, 52, 54, 56, 58]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(pe.get_src_frame(), 60)

    def test_render_p4r0(self):
        # constant speed
        speed = 4.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =       20, 21, 22, 23, 24,  25,  26,  27,  28,  29
        expect = np.array([[80, 84, 88, 92, 96, 100, 104, 108, 112, 116]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(pe.get_src_frame(), 120)

    def test_render_m0r5(self):
        # constant speed
        speed = -0.5                       # deeps flah
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =        20,    21,  22,    23,  24,    25,  26,    27,  28,    29
        expect = np.array([[-10, -10.5, -11, -11.5, -12, -12.5, -13, -13.5, -14, -14.5]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(pe.get_src_frame(), -15)

    def test_render_m1r0(self):
        # constant speed
        speed = -1.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =        20,  21,  22,  23,  24,  25,  26,  27,  28,  29
        expect = np.array([[-20, -21, -22, -23, -24, -25, -26, -27, -28, -29]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(pe.get_src_frame(), -30)

    def test_render_m2r0(self):
        # constant speed
        speed = -2.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =        20,  21,  22,  23,  24,  25,  26,  27,  28,  29
        expect = np.array([[-40, -42, -44, -46, -48, -50, -52, -54, -56, -58]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(pe.get_src_frame(), -60)

    def test_render_m4r0(self):
        # constant speed
        speed = -4.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =        20,  21,  22,  23,  24,   25,   26,   27,   28,   29
        expect = np.array([[-80, -84, -88, -92, -96, -100, -104, -108, -112, -116]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(pe.get_src_frame(), -120)

    def test_render_p0r0(self):
        # test constant speed = 0
        speed = 0.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =       20, 21, 22, 23, 24, 25, 26, 27, 28, 29
        expect = np.array([[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(pe.get_src_frame(), 0)

    def test_get_src_frame_a1(self):
        """
        Render 10 frames at 2x speed, then 10 more frames at half speed.  Use
        a delay on the source to avoid a discontinuity.
        """
        speed = 2.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =       20, 21, 22, 23, 24, 25, 26, 27, 28, 29
        # src_requested =   40, 42, 44, 46, 48, 50, 52, 54, 56, 58
        expect = np.array([[40, 42, 44, 46, 48, 50, 52, 54, 56, 58]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        src_frame = pe.get_src_frame()
        self.assertEqual(src_frame, 60)

        """
        last requested src frame = 60
        last requested dst frame = 30
        if we change rate to 0.5 and request dst frame 30, that will request
        src frame (dst_frame * 0.5) = 15.  we need to delay the request by
        15 - 60 = -45 to preserve continuity

        delay = last_dst_frame * new_speed - last_src_frame
        """
        # change speed...
        speed = 0.5
        delay = self.requested.end() * speed - pe.get_src_frame() # -45
        pe = WarpSpeedPE(self.src_pe.delay(delay), speed=speed)
        # render the next 10 frames, starting where the previous request ended
        t0 = self.requested.end()
        t1 = t0 + self.requested.duration()
        # requested =       30,   31, 32,   33, 34,   35, 36,   37, 38,   39
        # src requested =   60, 60.5, 61, 61.5, 62, 62.5, 63, 63.5, 64, 64.5
        expect = np.array([[60, 60.5, 61, 61.5, 62, 62.5, 63, 63.5, 64, 64.5]])
        got = pe.render(Extent(t0, t1))
        np.testing.assert_array_almost_equal(got, expect)
        # src_frame = 20 because the most recent call to pe.render() requested
        # src frames from 15 to 20.  The src_pe.delay() positioned the "read
        # head" properly to get continuity
        src_frame = pe.get_src_frame()
        self.assertEqual(src_frame, 20)

    def test_get_src_frame_b1(self):
        """
        Render 10 frames at half speed, then 10 more frames at 2x speed.  Use
        a delay on the source to avoid a discontinuity.
        """
        speed = 0.5
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        # requested =       20,   21, 22,   23, 24,   25, 26,   27, 28,   29
        # src requested =   10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5
        expect = np.array([[10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5]])
        got = pe.render(self.requested)
        np.testing.assert_array_almost_equal(got, expect)
        src_frame = pe.get_src_frame()
        self.assertEqual(src_frame, 15)

        """
        last requested src frame = 15
        last requested dst frame = 30
        if we change rate to 2.0 and request dst frame 30, that will request
        src frame (dst_frame * 2.0) = 60.  we need to delay the request by
        60 - 15 = 45 to preserve continuity

        delay = last_dst_frame * new_speed - last_src_frame
        """
        # change speed...
        speed = 2.0
        delay = self.requested.end() * speed - pe.get_src_frame() # 45
        pe = WarpSpeedPE(self.src_pe.delay(delay), speed=speed)
        # render the next 10 frames, starting where the previous request ended
        t0 = self.requested.end()
        t1 = t0 + self.requested.duration()
        # requested =       30, 31, 32, 33, 34, 35, 36, 37, 38, 39
        # src requested =   15, 17, 19, 21, 23, 25, 27, 29, 31, 33
        expect = np.array([[15, 17, 19, 21, 23, 25, 27, 29, 31, 33]])
        got = pe.render(Extent(t0, t1))
        np.testing.assert_array_almost_equal(got, expect)
        # src_frame = 80 because the most recent call to pe.render() requested
        # src frames from 60 to 80.  The src_pe.delay() positioned the "read
        # head" properly to get continuity
        src_frame = pe.get_src_frame()
        self.assertEqual(src_frame, 80)

    def test_extent_p1r0(self):
        pe = WarpSpeedPE(self.src_pe, speed=1.0)
        self.assertTrue(self.src_pe.extent().equals(pe.extent()))

    def test_extent_p2r0(self):
        speed = 2.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        t0 = self.src_pe.extent().start() / speed
        t1 = self.src_pe.extent().end() / speed
        if t1 < t0:
            t1, t0 = t0, t1            # enforce t0 <= t1
        self.assertTrue(pe.extent().equals(Extent(t0, t1)))

    def test_extent_p0r0(self):
        pe = WarpSpeedPE(self.src_pe, speed=0.0)
        # print("pe.extent() =", pe.extent())
        self.assertTrue(pe.extent().is_indefinite())

    def test_extent_m1r0(self):
        speed = -1.0
        pe = WarpSpeedPE(self.src_pe, speed=speed)
        t0 = self.src_pe.extent().start() / speed
        t1 = self.src_pe.extent().end() / speed
        if t1 < t0:
            t1, t0 = t0, t1            # enforce t0 <= t1
        self.assertTrue(pe.extent().equals(Extent(t0, t1)))

    def test_frame_rate(self):
        pe = WarpSpeedPE(self.src_pe, speed=1.0)
        self.assertEqual(pe.frame_rate(), 1234)

    def test_channel_count(self):
        pe = WarpSpeedPE(self.src_pe, speed=1.0)
        self.assertEqual(pe.channel_count(), 1)

