import os
import sys
import unittest
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import utils as ut
from pygmu import (ArrayPE, Extent, PygPE)

class TestArrayPE(unittest.TestCase):

    def setUp(self):
        # single channel
        self.frames1 = np.array([[-2.,  0.,  2.]], dtype=np.float32)
        self.pe1 = ArrayPE(self.frames1)
        # two channel
        self.frames2 = np.array([[-2.,  0.,  2.], [-1.,  1.,  3.]], dtype=np.float32)
        self.pe2 = ArrayPE(self.frames2)

    def test_init(self):
        self.assertIsInstance(self.pe1, ArrayPE)
        self.assertEqual(self.pe1.extent().start(), 0)
        self.assertEqual(self.pe1.extent().duration(), ut.frame_count(self.frames1))
        self.assertEqual(self.pe1.frame_rate(), None)
        self.assertEqual(self.pe1.channel_count(), ut.channel_count(self.frames1))

        self.assertIsInstance(self.pe2, ArrayPE)
        self.assertEqual(self.pe2.extent().start(), 0)
        self.assertEqual(self.pe2.extent().duration(), ut.frame_count(self.frames2))
        self.assertEqual(self.pe2.frame_rate(), None)
        self.assertEqual(self.pe2.channel_count(), ut.channel_count(self.frames2))

    def test_render1(self):
        # one channel
        e = Extent(-5, 0)     # no overlap
        expect = np.zeros([1, 5], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-3, 2)     # partial overlap
        expect = np.array([[0., 0., 0., -2., 0.]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-1, 4)     # full overlap
        expect = np.array([[0., -2., 0., 2., 0.]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(1, 6)     # partial overlap
        expect = np.array([[0., 2., 0., 0., 0.]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(3, 8)     # no overlap
        expect = np.zeros([1, 5], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render2(self):
        # two channel
        e = Extent(-5, 0)     # no overlap
        expect = np.zeros([2, 5], dtype=np.float32)
        got = self.pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-3, 2)     # partial overlap
        expect = np.array([[0., 0., 0., -2., 0.], [0., 0., 0., -1., 1.]], dtype=np.float32)
        got = self.pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-1, 4)     # full overlap
        expect = np.array([[0., -2., 0., 2., 0.], [0., -1., 1., 3., 0.]], dtype=np.float32)
        got = self.pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(1, 6)     # partial overlap
        expect = np.array([[0., 2., 0., 0., 0.], [1., 3., 0., 0., 0.]], dtype=np.float32)
        got = self.pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(3, 8)     # no overlap
        expect = np.zeros([2, 5], dtype=np.float32)
        got = self.pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        pass

    def test_frame_rate(self):
        pass

    def test_channel_count(self):
        pass
