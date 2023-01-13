import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (CropPE, Extent, IdentityPE, PygPE)

class TestCropPE(unittest.TestCase):

    def setUp(self):
        self.id_pe = IdentityPE(channel_count=2)
        self.pe = CropPE(self.id_pe, Extent(100, 103))

    def test_init(self):
        self.assertIsInstance(self.pe, CropPE)

    def test_render(self):   
        e = Extent(95, 100)       # no overlap
        expect = np.zeros([2, 5], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(97, 102)     # partial overlap
        expect = np.array([[0., 0., 0., 100., 101.], [0., 0., 0., 100., 101.]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(99, 104)     # full overlap
        expect = np.array([[0, 100, 101, 102, 0], [0, 100, 101, 102, 0]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(101, 106)     # partial overlap
        expect = np.array([[101., 102., 0., 0., 0.], [101., 102., 0., 0., 0.]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(103, 108)     # no overlap
        expect = np.zeros([2, 5], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        self.assertTrue(Extent(100, 103).equals(self.pe.extent()))

    def test_frame_rate(self):
        self.assertEqual(self.pe.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

    def test_channel_count(self):
        self.assertEqual(self.pe.channel_count(), self.id_pe.channel_count())

