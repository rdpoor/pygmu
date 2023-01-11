import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
import pyg_exceptions as pyx
from pygmu import (ArrayPE, ConstPE, DelayAPE, Extent, IdentityPE, LinearRampPE, PygPE)


class TestDelayAPE(unittest.TestCase):

    def test_init(self):
        # verify that creating a DelayAPE returns an instance of DelayAPE
        extent = Extent(0, 10)
        delay = 0
        src = LinearRampPE(0, 10, extent, channel_count = 1).crop(extent)
        pe = DelayAPE(src, delay)
        self.assertIsInstance(pe, DelayAPE)
        self.assertEqual(pe.channel_count(), 1)
        self.assertFalse(pe.extent().is_indefinite())

        delay = 0
        src = LinearRampPE(0, 10, extent, channel_count = 2).crop(extent)
        pe = DelayAPE(src, delay)
        self.assertIsInstance(pe, DelayAPE)
        self.assertEqual(pe.channel_count(), 2)
        self.assertFalse(pe.extent().is_indefinite())

        delay = ConstPE(0, channel_count = 1)
        src = LinearRampPE(0, 10, extent, channel_count = 1).crop(extent)
        pe = DelayAPE(src, delay)
        self.assertIsInstance(pe, DelayAPE)
        self.assertEqual(pe.channel_count(), 1)
        self.assertTrue(pe.extent().is_indefinite())

        delay = ConstPE(0, channel_count = 1)
        src = LinearRampPE(0, 10, extent, channel_count = 2).crop(extent)
        pe = DelayAPE(src, delay)
        self.assertIsInstance(pe, DelayAPE)
        self.assertEqual(pe.channel_count(), 2)
        self.assertTrue(pe.extent().is_indefinite())

        delay = ConstPE(0, channel_count = 2)
        src = LinearRampPE(0, 10, extent, channel_count = 1).crop(extent)
        with self.assertRaises(pyx.ChannelCountMismatch):
            DelayAPE(src, delay)

    def test_render(self):
        delay = -0.5
        src = ArrayPE(np.array([[100], [101], [98], [100]]))
        pe = DelayAPE(src, delay)
        got = pe.render(Extent(0, 3))
        expect = np.array([[100.5], [99.5], [99.0]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = -0.5
        src = ArrayPE(np.array([[100], [101], [98], [100]])).delay(30)
        pe = DelayAPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[100.5], [99.5], [99.0]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = -1.0
        src = ArrayPE(np.array([[100], [101], [98], [100]])).delay(30)
        pe = DelayAPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[101], [98], [100]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = 0.0
        src = ArrayPE(np.array([[100], [101], [98], [100]])).delay(30)
        pe = DelayAPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[100], [101], [98]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

        delay = -0.5
        src = ArrayPE(np.array([[100, 200], [101, 201], [98, 198], [100, 200]])).delay(30)
        pe = DelayAPE(src, delay)
        got = pe.render(Extent(30, 33))
        expect = np.array([[100.5, 200.5], [99.5, 199.5], [99.0, 199.0]], dtype=np.float32)
        # print("got:", got)
        # print("expect:", expect)
        np.testing.assert_array_almost_equal(got, expect)

