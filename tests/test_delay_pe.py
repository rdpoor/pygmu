import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
import pyg_exceptions as pyx
from pygmu import (ArrayPE, ConstPE, DelayPE, Extent, IdentityPE, LinearRampPE, PygPE)


class TestDelayPE(unittest.TestCase):

    def test_init(self):
        # verify that creating a DelayPE returns an instance of DelayPE
        extent = Extent(0, 10)
        delay = 0
        src = LinearRampPE(0, 10, extent, channel_count = 1).crop(extent)
        pe = DelayPE(src, delay)
        self.assertIsInstance(pe, DelayPE)
        self.assertEqual(pe.channel_count(), 1)
        self.assertFalse(pe.extent().is_indefinite())

        delay = 0
        src = LinearRampPE(0, 10, extent, channel_count = 2).crop(extent)
        pe = DelayPE(src, delay)
        self.assertIsInstance(pe, DelayPE)
        self.assertEqual(pe.channel_count(), 2)
        self.assertFalse(pe.extent().is_indefinite())

        delay = ConstPE(0, channel_count = 1)
        src = LinearRampPE(0, 10, extent, channel_count = 1).crop(extent)
        pe = DelayPE(src, delay)
        self.assertIsInstance(pe, DelayPE)
        self.assertEqual(pe.channel_count(), 1)
        self.assertTrue(pe.extent().is_indefinite())

        delay = ConstPE(0, channel_count = 1)
        src = LinearRampPE(0, 10, extent, channel_count = 2).crop(extent)
        pe = DelayPE(src, delay)
        self.assertIsInstance(pe, DelayPE)
        self.assertEqual(pe.channel_count(), 2)
        self.assertTrue(pe.extent().is_indefinite())

        delay = ConstPE(0, channel_count = 2)
        src = LinearRampPE(0, 10, extent, channel_count = 1).crop(extent)
        with self.assertRaises(pyx.ChannelCountMismatch):
            DelayPE(src, delay)

    def test_render(self):
        delay = -0.5
        src = ArrayPE(np.array([[100, 101, 98, 100]]))
        pe = DelayPE(src, delay)
        got = pe.render(Extent(0, 3))
        expect = np.array([[100.5, 99.5, 99.0]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = -0.5
        src = ArrayPE(np.array([[100, 101, 98, 100]])).delay(30)
        pe = DelayPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[100.5, 99.5, 99.0]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = -1.0
        src = ArrayPE(np.array([[100, 101, 98, 100]])).delay(30)
        pe = DelayPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[101, 98, 100]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = 0.0
        src = ArrayPE(np.array([[100, 101, 98, 100]])).delay(30)
        pe = DelayPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[100, 101, 98]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = -0.5
        src = ArrayPE(np.array([[100, 101,  98, 100], [200, 201, 198, 200]])).delay(30)
        pe = DelayPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[100.5,  99.5,  99. ], [200.5, 199.5, 199. ]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        # fixed integer delay
        delay = 5
        src = IdentityPE(channel_count=2)
        pe = DelayPE(src, delay)
        expect = np.array([[-5., -4., -3., -2., -1.], [-5., -4., -3., -2., -1.]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        delay = 5
        src = IdentityPE(channel_count=2)
        pe = DelayPE(src, delay)
        expect = np.array([[0., 1., 2., 3., 4.], [0., 1., 2., 3., 4.]], dtype=np.float32)
        got = pe.render(Extent(5, 10))
        np.testing.assert_array_almost_equal(got, expect)
