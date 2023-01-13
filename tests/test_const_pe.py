import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ConstPE, Extent, PygPE)

class TestConstPE(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        self.pe = ConstPE(22.2, 1)
        self.assertIsInstance(self.pe, ConstPE)

    def test_render(self):
        e = Extent(0, 5)
        self.pe = ConstPE(22.2, 1)
        expect = np.array([[22.2, 22.2, 22.2, 22.2, 22.2]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        self.pe = ConstPE(11.1, 2)
        expect = np.array([[11.1, 11.1, 11.1, 11.1, 11.1], [11.1, 11.1, 11.1, 11.1, 11.1]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        self.pe = ConstPE(22.2, 1)
        self.assertTrue(Extent().equals(self.pe.extent()))

    def test_frame_rate(self):
        self.pe = ConstPE(22.2, 1)
        self.assertEqual(self.pe.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

    def test_channel_count(self):
        self.pe = ConstPE(22.2, 1)
        self.assertEqual(self.pe.channel_count(), 1)
        self.pe = ConstPE(22.2, 2)
        self.assertEqual(self.pe.channel_count(), 2)

