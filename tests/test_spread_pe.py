import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
import pyg_exceptions as pyx
from pygmu import (Extent, LinearRampPE, PygPE, SpreadPE)


class TestSpreadPE(unittest.TestCase):

    def setUp(self):
        self.extent = Extent(0, 5)
        self.src = LinearRampPE(0, 5, self.extent)
        self.pe1 = SpreadPE(self.src, channel_count=1)
        self.pe2 = SpreadPE(self.src, channel_count=2)
        self.pe3 = SpreadPE(self.src, channel_count=3)
        self.pe_default = SpreadPE(self.src)

    def test_init(self):
        # verify that creating a DelayPE returns an instance of DelayPE
        self.assertIsInstance(self.pe1, SpreadPE)
        self.assertEqual(self.pe1.channel_count(), 1)
        self.assertEqual(self.pe1.extent(), self.src.extent())
        self.assertEqual(self.pe1.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

        self.assertIsInstance(self.pe2, SpreadPE)
        self.assertEqual(self.pe2.channel_count(), 2)
        self.assertEqual(self.pe2.extent(), self.src.extent())
        self.assertEqual(self.pe2.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

        self.assertIsInstance(self.pe3, SpreadPE)
        self.assertEqual(self.pe3.channel_count(), 3)
        self.assertEqual(self.pe3.extent(), self.src.extent())
        self.assertEqual(self.pe3.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

        self.assertIsInstance(self.pe_default, SpreadPE)
        self.assertEqual(self.pe_default.channel_count(), 2)
        self.assertEqual(self.pe_default.extent(), self.src.extent())
        self.assertEqual(self.pe_default.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

        # Cannot use a multi-channel source as input to SpreadPE
        with self.assertRaises(pyx.ChannelCountMismatch):
            SpreadPE(self.pe2)

    def test_render(self):
        got = self.pe1.render(self.extent)
        expect = np.array([[0, 1, 2, 3, 4]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)

        got = self.pe2.render(self.extent)
        expect = np.array([[0, 1, 2, 3, 4], [0, 1, 2, 3, 4]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)

        got = self.pe3.render(self.extent)
        expect = np.array([[0, 1, 2, 3, 4], [0, 1, 2, 3, 4], [0, 1, 2, 3, 4]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        # already tested
        pass

    def test_frame_rate(self):
        # already tested
        pass

    def test_channel_count(self):
        # already tested
        pass
