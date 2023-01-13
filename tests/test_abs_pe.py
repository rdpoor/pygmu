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
        self.frames = np.array([[-2.,  0.,  2.], [-1.,  1.,  3.]], dtype=np.float32)
        self.src = ArrayPE(self.frames)
        self.pe = AbsPE(self.src)

    def test_init(self):
        self.assertIsInstance(self.pe, AbsPE)

    def test_render(self):
        e = Extent(-5, 0)     # no overlap
        expect = np.zeros([2, 5], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-3, 2)     # partial overlap
        expect = np.array([[0., 0., 0., 2., 0.], [0., 0., 0., 1., 1.]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-1, 4)     # full overlap
        expect = np.array([[0., 2., 0., 2., 0.], [0., 1., 1., 3., 0.]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(1, 6)     # partial overlap
        expect = np.array([[0., 2., 0., 0., 0.], [1., 3., 0., 0., 0.]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(3, 8)     # no overlap
        expect = np.zeros([2, 5], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        self.assertTrue(self.pe.extent().equals(self.src.extent()))

    def test_frame_rate(self):
        self.assertEqual(self.pe.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

    def test_channel_count(self):
        self.assertEqual(self.pe.channel_count(), self.src.channel_count())

