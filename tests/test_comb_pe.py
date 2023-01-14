import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
import utils as ut
import pyg_exceptions as pyx
from pygmu import (CombPE, ConstPE, Extent, IdentityPE)

class TestCombPE(unittest.TestCase):

    def test_init(self):
        # single channel source
        src1 = IdentityPE()
        pe = CombPE(src1, frame_rate=48000)
        self.assertIsInstance(pe, CombPE)
        self.assertTrue(pe.extent().is_indefinite())
        self.assertEqual(pe.frame_rate(), 48000)
        self.assertEqual(pe.channel_count(), src1.channel_count())

        # two channel source
        src2 = IdentityPE().spread(2)
        pe = CombPE(src2, frame_rate=48000)
        self.assertIsInstance(pe, CombPE)
        self.assertTrue(pe.extent().is_indefinite())
        self.assertEqual(pe.frame_rate(), 48000)
        self.assertEqual(pe.channel_count(), src2.channel_count())

        # omitted frame_rate
        src1 = IdentityPE()
        with self.assertRaises(pyx.FrameRateMismatch):
            CombPE(src1)

        # inherit frame rate from source
        src1 = IdentityPE(frame_rate=12345)
        pe = CombPE(src1)
        self.assertEqual(pe.frame_rate(), 12345)

        # mismatched rrame rate (prints a warning only)
        src1 = IdentityPE(frame_rate=12345)
        pe = CombPE(src1, frame_rate=45678)
        self.assertEqual(pe.frame_rate(), 45678)

    def test_render(self):
        extent = Extent(0, 5)

        # single channel source
        src1 = IdentityPE()
        pe = CombPE(src1, frame_rate=48000)
        frames = pe.render(extent)
        self.assertEqual(ut.channel_count(frames), pe.channel_count())
        self.assertEqual(ut.frame_count(frames), extent.duration())

        # two channel source
        src2 = IdentityPE()
        pe = CombPE(src2, frame_rate=48000)
        frames = pe.render(extent)
        self.assertEqual(ut.channel_count(frames), pe.channel_count())
        self.assertEqual(ut.frame_count(frames), extent.duration())

        # no overlap
        extent2 = extent.offset(extent.duration())
        src1 = IdentityPE().crop(extent)
        pe = CombPE(src1, frame_rate=48000)
        frames = pe.render(extent2)
        self.assertEqual(ut.channel_count(frames), pe.channel_count())
        self.assertEqual(ut.frame_count(frames), extent2.duration())
        expect = np.zeros((1, extent2.duration()))

    def test_extent(self):
        pass

    def test_frame_rate(self):
        pass

    def test_channel_count(self):
        pass

