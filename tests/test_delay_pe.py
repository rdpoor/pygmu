import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (DelayPE, Extent, IdentityPE, PygPE)

class TestDelayPE(unittest.TestCase):

    def setUp(self):
        self.id_pe = IdentityPE(channel_count=2)
        self.pe = DelayPE(self.id_pe, 5)

    def test_init(self):
        self.assertIsInstance(self.pe, DelayPE)

    def test_render(self):        
        e = Extent(0, 5)
        expect = np.array([[-5, -5], [-4, -4], [-3, -3], [-2, -2], [-1, -1]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(5, 10)
        expect = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        # This is not quite a complete test.  If src_pe has finite extent, then the
        # delay_pe's extent is the shifted version.
        self.assertTrue(self.id_pe.extent().equals(self.pe.extent()))

    def test_frame_rate(self):
        self.assertEqual(self.pe.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

    def test_channel_count(self):
        self.assertEqual(self.pe.channel_count(), self.id_pe.channel_count())

