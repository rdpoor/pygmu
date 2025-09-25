import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ConstPE, CropPE, IdentityPE, Extent, LoopPE, PygPE)

class TestLoopPE(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        src_pe = CropPE(ConstPE(10), Extent(0, 10))
        pe = LoopPE(src_pe, loop_duration=4)
        self.assertIsInstance(pe, LoopPE)

    def test_render1(self):
        src_pe = CropPE(IdentityPE(), Extent(0, 6))

        pe = LoopPE(src_pe, loop_duration=3) # loop is shorter than source
        e = Extent(0, 12)
        expect = np.array([[0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = LoopPE(src_pe, loop_duration=5) # loop is shorter than source
        e = Extent(0, 12)
        expect = np.array([[0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = LoopPE(src_pe, loop_duration=7) # loop is longer than source
        e = Extent(0, 12)
        expect = np.array([[0, 1, 2, 3, 4, 5, 0, 0, 1, 2, 3, 4]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = LoopPE(src_pe, loop_duration=9) # loop is longer than source
        e = Extent(0, 12)
        expect = np.array([[0, 1, 2, 3, 4, 5, 0, 0, 0, 0, 1, 2]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = LoopPE(src_pe, loop_duration=5) # Extent fully negative...
        e = Extent(-12, 0)
        #                  -12  -11  -10  -9   -8   -7   -6   -5   -4   -3   -2   -1
        expect = np.array([[ 3,   4,   0,  1,   2,   3,   4,   0,   1,   2,   3,  4]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        pe = LoopPE(src_pe, loop_duration=5) # Extent spans negative to positive
        e = Extent(-6, 6)
        #                  -6   -5   -4   -3   -2   -1    0    1    2    3    4    5
        expect = np.array([[4,   0,   1,   2,   3,   4,   0,   1,   2,   3,   4,   0]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        src_pe = CropPE(IdentityPE(), Extent(0, 3))
        pe = LoopPE(src_pe, loop_duration=5) # src < loop_len, negative to positive
        e = Extent(-5, 7)
        #                  -5   -4   -3   -2   -1    0    1    2    3    4    5    6
        expect = np.array([[0,   1,   2,   0,   0,   0,   1,   2,   0,   0,   0,   1]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        src_pe = CropPE(IdentityPE(), Extent(3, 6))
        pe = LoopPE(src_pe, loop_duration=5) # source starts > 0
        e = Extent(0, 12)
        #                   0    1    2    3    4    5    6    7    8    9    10   11
        expect = np.array([[0,   0,   0,   3,   4,   0,   0,   0,   3,   4,    0,   0]], dtype=np.float32)
        got = pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        # Loop is longer than render request...
        src_pe = IdentityPE()
        pe = LoopPE(src_pe, loop_duration=10000)   # rather long...
        got = pe.render(Extent(0, 10))
        expect = np.array([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]])
        np.testing.assert_array_almost_equal(got, expect)

        got = pe.render(Extent(10, 20))
        expect = np.array([[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]])
        np.testing.assert_array_almost_equal(got, expect)

        got = pe.render(Extent(9995, 10005))
        expect = np.array([[9995, 9996, 9997, 9998, 9999, 0, 1, 2, 3, 4]])
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        # extent is, by definition, indefinite...
        src_pe = CropPE(IdentityPE(), Extent(3, 6))
        pe = LoopPE(src_pe, loop_duration=5)
        self.assertTrue(pe.extent().is_indefinite())

    def test_frame_rate(self):
        # inherits frame_rate rate from source.
        src_pe = CropPE(IdentityPE(), Extent(3, 6))
        pe = LoopPE(src_pe, loop_duration=5)
        self.assertEqual(src_pe.frame_rate(), pe.frame_rate())

    def test_channel_count(self):
        # inherits frame_rate rate from source.
        src_pe = CropPE(IdentityPE(), Extent(3, 6))
        pe = LoopPE(src_pe, loop_duration=5)
        self.assertEqual(src_pe.channel_count(), pe.channel_count())

