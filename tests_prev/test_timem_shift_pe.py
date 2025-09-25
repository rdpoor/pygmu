import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
import pyg_exceptions as pyx
from pygmu import (ArrayPE, ConstPE, TimeShiftPE, Extent, IdentityPE, RampPE, PygPE)


class TestTimeShiftPE(unittest.TestCase):

    def test_init(self):
        # verify that creating a TimeShiftPE returns an instance of TimeShiftPE
        extent = Extent(0, 10)

        # fixed delay, single channel
        delay = 0
        src = RampPE(0, 10, extent).crop(extent)
        pe = TimeShiftPE(src, delay)
        self.assertIsInstance(pe, TimeShiftPE)
        self.assertEqual(pe.channel_count(), 1)
        self.assertFalse(pe.extent().is_indefinite())

        # fixed delay, two channel
        delay = 0
        src = RampPE(0, 10, extent).crop(extent).spread(2)
        pe = TimeShiftPE(src, delay)
        self.assertIsInstance(pe, TimeShiftPE)
        self.assertEqual(pe.channel_count(), 2)
        self.assertFalse(pe.extent().is_indefinite())

        # dynamic delay, single channel
        delay = ConstPE(0)
        src = RampPE(0, 10, extent).crop(extent)
        pe = TimeShiftPE(src, delay)
        self.assertIsInstance(pe, TimeShiftPE)
        self.assertEqual(pe.channel_count(), 1)
        self.assertTrue(pe.extent().is_indefinite())

        # dynamic delay, two channel
        delay = ConstPE(0)
        src = RampPE(0, 10, extent).crop(extent).spread(2)
        pe = TimeShiftPE(src, delay)
        self.assertIsInstance(pe, TimeShiftPE)
        self.assertEqual(pe.channel_count(), 2)
        self.assertTrue(pe.extent().is_indefinite())

        # dynamic delay source must be single channel
        delay = ConstPE(0).spread(2)
        src = RampPE(0, 10, extent).crop(extent)
        with self.assertRaises(pyx.ChannelCountMismatch):
            TimeShiftPE(src, delay)

    def test_render(self):
        delay = -0.5
        src = ArrayPE(np.array([[100, 101, 98, 100]]))
        pe = TimeShiftPE(src, delay)
        got = pe.render(Extent(0, 3))
        expect = np.array([[100.5, 99.5, 99.0]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = -0.5
        src = ArrayPE(np.array([[100, 101, 98, 100]])).time_shift(30)
        pe = TimeShiftPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[100.5, 99.5, 99.0]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = -1.0
        src = ArrayPE(np.array([[100, 101, 98, 100]])).time_shift(30)
        pe = TimeShiftPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[101, 98, 100]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = 0.0
        src = ArrayPE(np.array([[100, 101, 98, 100]])).time_shift(30)
        pe = TimeShiftPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[100, 101, 98]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = -0.5
        src = ArrayPE(np.array([[100, 101,  98, 100], [200, 201, 198, 200]])).time_shift(30)
        pe = TimeShiftPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[100.5,  99.5,  99. ], [200.5, 199.5, 199. ]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        # fixed integer delay
        delay = 5
        src = IdentityPE().spread(2)
        pe = TimeShiftPE(src, delay)
        expect = np.array([[-5., -4., -3., -2., -1.], [-5., -4., -3., -2., -1.]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        delay = 5
        src = IdentityPE().spread(2)
        pe = TimeShiftPE(src, delay)
        expect = np.array([[0., 1., 2., 3., 4.], [0., 1., 2., 3., 4.]], dtype=np.float32)
        got = pe.render(Extent(5, 10))
        np.testing.assert_array_almost_equal(got, expect)

        # dynamic delay times, single channel source
        extent = Extent(10, 20)
        delay = ConstPE(22.0)
        src = IdentityPE()
        pe = TimeShiftPE(src, delay);
        expect = src.render(extent) - 22
        got = pe.render(extent)
        np.testing.assert_array_almost_equal(got, expect)

        # dynamic delay times, two channel source
        extent = Extent(10, 20)
        delay = ConstPE(22.0)
        src = IdentityPE().spread(2)
        pe = TimeShiftPE(src, delay);
        expect = src.render(extent) - 22
        got = pe.render(extent)
        np.testing.assert_array_almost_equal(got, expect)

    def test_frame_rate(self):
        # no frame rate specified
        delay = IdentityPE()
        src = IdentityPE()
        pe = TimeShiftPE(src, delay);
        self.assertIsNone(pe.frame_rate())

        # frame_rate inherited from src
        delay = IdentityPE()
        src = IdentityPE(frame_rate = 1234)
        pe = TimeShiftPE(src, delay);
        self.assertEqual(pe.frame_rate(), 1234)
