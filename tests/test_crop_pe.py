import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (CropPE, Extent, IdentityPE, PygPE)

class TestCropPE(unittest.TestCase):

    def test_init(self):
        extent = Extent(100, 103)

        src1 = IdentityPE()    # single channel
        pe1 = CropPE(src1, extent)
        self.assertIsInstance(pe1, CropPE)
        self.assertTrue(pe1.extent().equals(extent))
        self.assertIsNone(pe1.frame_rate())
        self.assertEqual(pe1.channel_count(), src1.channel_count())

        src2 = src1.spread(2)  # two channel
        pe2 = CropPE(src2, extent)
        self.assertIsInstance(pe2, CropPE)
        self.assertTrue(pe2.extent().equals(extent))
        self.assertIsNone(pe2.frame_rate())
        self.assertEqual(pe2.channel_count(), src2.channel_count())

    def test_render(self):   
        extent = Extent(100, 103)

        # single channel
        src1 = IdentityPE()    # single channel
        pe1 = CropPE(src1, extent)

        e = Extent(95, 100)       # no overlap
        expect = np.zeros([1, 5], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(97, 102)     # partial overlap
        expect = np.array([[0., 0., 0., 100., 101.]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(100, 103)     # exact overlap
        expect = np.array([[100, 101, 102]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(99, 104)     # full overlap
        expect = np.array([[0, 100, 101, 102, 0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(101, 106)     # partial overlap
        expect = np.array([[101., 102., 0., 0., 0.]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(103, 108)     # no overlap
        expect = np.zeros([1, 5], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        # two channel
        src2 = IdentityPE().spread(2)
        pe2 = CropPE(src2, extent)

        e = Extent(95, 100)       # no overlap
        expect = np.zeros([2, 5], dtype=np.float32)
        got = pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(97, 102)     # partial overlap
        expect = np.array([[0., 0., 0., 100., 101.], [0., 0., 0., 100., 101.]], dtype=np.float32)
        got = pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(99, 104)     # full overlap
        expect = np.array([[0, 100, 101, 102, 0], [0, 100, 101, 102, 0]], dtype=np.float32)
        got = pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(101, 106)     # partial overlap
        expect = np.array([[101., 102., 0., 0., 0.], [101., 102., 0., 0., 0.]], dtype=np.float32)
        got = pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(103, 108)     # no overlap
        expect = np.zeros([2, 5], dtype=np.float32)
        got = pe2.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        pass

    def test_frame_rate(self):
        pass

    def test_channel_count(self):
        pass

