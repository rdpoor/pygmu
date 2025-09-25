import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
import utils as ut
import pyg_exceptions as pyx
from pygmu import (BlitSawPE, ConstPE, Extent)

class TestBlitSawPE(unittest.TestCase):

    def test_init(self):
        # fixed frequency
        pe = BlitSawPE(frequency=440, n_harmonics=2, frame_rate=48000)
        self.assertIsInstance(pe, BlitSawPE)
        self.assertTrue(pe.extent().is_indefinite())
        self.assertEqual(pe.frame_rate(), 48000)
        self.assertEqual(pe.channel_count(), 1)

        # omitted frame_rate
        with self.assertRaises(pyx.FrameRateMismatch):
            BlitSawPE(frequency=440, n_harmonics=2)

        # dynamic frequency
        freq = ConstPE(1.0)
        pe = BlitSawPE(frequency=freq, n_harmonics=2, frame_rate=48000)
        self.assertIsInstance(pe, BlitSawPE)
        self.assertTrue(pe.extent().is_indefinite())
        self.assertEqual(pe.frame_rate(), 48000)
        self.assertEqual(pe.channel_count(), 1)

        # dynamic frequency source > 1 channel
        freq = ConstPE(1.0).spread(2)
        with self.assertRaises(pyx.ChannelCountMismatch):
            BlitSawPE(frequency=freq, n_harmonics=2, frame_rate=48000)

    def test_render(self):
        # fixed frequency
        pe = BlitSawPE(frequency=440, n_harmonics=2, frame_rate=48000)
        extent = Extent(0, 5)
        frames = pe.render(extent)
        self.assertEqual(ut.channel_count(frames), pe.channel_count())
        self.assertEqual(ut.frame_count(frames), extent.duration())

        # dynamic frequency
        freq = ConstPE(1.0)
        pe = BlitSawPE(frequency=freq, n_harmonics=2, frame_rate=48000)
        extent = Extent(0, 5)
        frames = pe.render(extent)
        self.assertEqual(ut.channel_count(frames), pe.channel_count())
        self.assertEqual(ut.frame_count(frames), extent.duration())

        # dynamic frequency with zero value
        freq = ConstPE(0.0)
        pe = BlitSawPE(frequency=freq, n_harmonics=2, frame_rate=48000)
        extent = Extent(0, 5)
        with self.assertRaises(pyx.ArgumentError):
            pe.render(extent)

    def test_extent(self):
        pass

    def test_frame_rate(self):
        pass

    def test_channel_count(self):
        pass

