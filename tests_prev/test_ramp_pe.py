import unittest
import numpy as np
import os
import sys

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pyg_exceptions as pyx
import utils as ut
from pygmu import (Extent, RampPE)

FRAME_RATE = 48000

class TestRampPE(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        pe = RampPE(0.0, 1.0, Extent(0, 10))
        self.assertIsInstance(pe, RampPE)

    def test_render(self):
        pe = RampPE(10, 20, Extent(0, 10))

        requested = Extent(-10, 0)
        expect = np.array([[10, 10, 10, 10, 10, 10, 10, 10, 10, 10]], dtype=np.float32)
        got = pe.render(requested)
        np.testing.assert_array_almost_equal(expect, got)

        requested = Extent(-5, 5)
        expect = np.array([[10, 10, 10, 10, 10, 10, 11, 12, 13, 14]], dtype=np.float32)
        got = pe.render(requested)
        np.testing.assert_array_almost_equal(expect, got)

        requested = Extent(0, 10)
        expect = np.array([[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]], dtype=np.float32)
        got = pe.render(requested)
        np.testing.assert_array_almost_equal(expect, got)

        requested = Extent(5, 15)
        expect = np.array([[15, 16, 17, 18, 19, 20, 20, 20, 20, 20]], dtype=np.float32)
        got = pe.render(requested)
        np.testing.assert_array_almost_equal(expect, got)

        requested = Extent(10, 20)
        expect = np.array([[20, 20, 20, 20, 20, 20, 20, 20, 20, 20]], dtype=np.float32)
        got = pe.render(requested)
        np.testing.assert_array_almost_equal(expect, got)

    def test_extent(self):
        pe = RampPE(0.0, 1.0, Extent(0, 10))
        self.assertTrue(Extent(0, 10).equals(pe.extent()))

    def test_frame_rate(self):
        pe = RampPE(0.0, 1.0, Extent(0, 10))
        self.assertIsNone(pe.frame_rate())

        pe = RampPE(0.0, 1.0, Extent(0, 10), frame_rate=1234)
        self.assertEqual(pe.frame_rate(), 1234)

    def test_channel_count(self):
        pe = RampPE(0.0, 1.0, Extent(0, 10))
        self.assertEqual(pe.channel_count(), 1)

