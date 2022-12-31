import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (AbsPE, ArrayPE, Extent, PygPE)

class TestAbsPE(unittest.TestCase):

    def setUp(self):
        self.a = np.array([[-2, -1], [0, 1], [2, 3]], dtype=np.float32)
        array_pe = ArrayPE(self.a)
        self.pe = AbsPE(array_pe)

    def test_init(self):
        self.assertIsInstance(self.pe, AbsPE)

    def test_render(self):
        e = Extent(-5, 0)     # no overlap
        expect = np.zeros([5, 2], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-3, 2)     # partial overlap
        expect = np.array([[0, 0], [0, 0], [0, 0], [2, 1], [0, 1]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-1, 4)     # full overlap
        expect = np.array([[0, 0], [2, 1], [0, 1], [2, 3], [0, 0]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(1, 6)     # partial overlap
        expect = np.array([[0, 1], [2, 3], [0, 0], [0, 0], [0, 0]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(3, 8)     # no overlap
        expect = np.zeros([5, 2], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        self.assertTrue(Extent(0, self.a.shape[0]).equals(self.pe.extent()))

    def test_frame_rate(self):
        self.assertEqual(self.pe.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

    def test_channel_count(self):
        self.assertEqual(self.pe.channel_count(), self.a.shape[1])

