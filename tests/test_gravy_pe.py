import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ConstPE, CropPE, IdentityPE, Extent, GravyPE, PygPE)

class TestGravyPE(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        src_pe = CropPE(ConstPE(10, channel_count=1), Extent(0, 10))
        pe = GravyPE(src_pe, loop_length=4)
        self.assertIsInstance(pe, GravyPE)

    def test_render1(self):
        src_pe = CropPE(IdentityPE(channel_count=1), Extent(0, 6))

        pe = GravyPE(src_pe, loop_length=3) # loop is shorter than source
        e = Extent(0, 12)
        expect = np.array([[0], [1], [2], [0], [1], [2], [0], [1], [2], [0], [1], [2]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = GravyPE(src_pe, loop_length=5) # loop is shorter than source
        e = Extent(0, 12)
        expect = np.array([[0], [1], [2], [3], [4], [0], [1], [2], [3], [4], [0], [1]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = GravyPE(src_pe, loop_length=7) # loop is longer than source
        e = Extent(0, 12)
        expect = np.array([[0], [1], [2], [3], [4], [5], [0], [0], [1], [2], [3], [4]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = GravyPE(src_pe, loop_length=9) # loop is longer than source
        e = Extent(0, 12)
        expect = np.array([[0], [1], [2], [3], [4], [5], [0], [0], [0], [0], [1], [2]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = GravyPE(src_pe, loop_length=5) # Extent fully negative...
        e = Extent(-12, 0)
        #                  -12  -11  -10  -9   -8   -7   -6   -5   -4   -3   -2   -1
        expect = np.array([[3], [4], [0], [1], [2], [3], [4], [0], [1], [2], [3], [4]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = GravyPE(src_pe, loop_length=5) # Extent spans negative to positive
        e = Extent(-6, 6)
        #                  -6   -5   -4   -3   -2   -1    0    1    2    3    4    5
        expect = np.array([[4], [0], [1], [2], [3], [4], [0], [1], [2], [3], [4], [0]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        src_pe = CropPE(IdentityPE(channel_count=1), Extent(0, 3))
        pe = GravyPE(src_pe, loop_length=5) # src < loop_len, negative to positive
        e = Extent(-5, 7)
        #                  -5   -4   -3   -2   -1    0    1    2    3    4    5    6
        expect = np.array([[0], [1], [2], [0], [0], [0], [1], [2], [0], [0], [0], [1]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        src_pe = CropPE(IdentityPE(channel_count=1), Extent(3, 6))
        pe = GravyPE(src_pe, loop_length=5) # source starts > 0
        e = Extent(0, 12)
        #                   0    1    2    3    4    5    6    7    8    9    10   11
        expect = np.array([[0], [0], [0], [3], [4], [0], [0], [0], [3], [4], [0], [0]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        # extent is, by definition, indefinite...
        src_pe = CropPE(IdentityPE(channel_count=1), Extent(3, 6))
        pe = GravyPE(src_pe, loop_length=5)
        self.assertTrue(pe.extent().equals(Extent()))

    def test_frame_rate(self):
        # inherits frame_rate rate from source.
        src_pe = CropPE(IdentityPE(channel_count=1), Extent(3, 6))
        pe = GravyPE(src_pe, loop_length=5)
        self.assertEqual(src_pe.frame_rate(), pe.frame_rate())

    def test_channel_count(self):
        # inherits frame_rate rate from source.
        src_pe = CropPE(IdentityPE(channel_count=1), Extent(3, 6))
        pe = GravyPE(src_pe, loop_length=5)
        self.assertEqual(src_pe.channel_count(), pe.channel_count())

