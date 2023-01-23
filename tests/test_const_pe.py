import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ConstPE, Extent, PygPE)

class TestConstPE(unittest.TestCase):

    def test_init(self):
        pe = ConstPE(22.2)
        self.assertIsInstance(pe, ConstPE)
        self.assertTrue(pe.extent().is_indefinite())
        self.assertIsNone(pe.frame_rate())
        self.assertEqual(pe.channel_count(), 1)

    def test_render(self):
        e = Extent(0, 5)
        self.pe = ConstPE(22.2)
        expect = np.array([[22.2, 22.2, 22.2, 22.2, 22.2]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        pass

    def test_frame_rate(self):
        pass

    def test_channel_count(self):
        pass

