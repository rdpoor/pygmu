import unittest
import numpy as np
import os
import sys

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pyg_exceptions as pyx
import utils as ut
from pygmu import (NoisePE, Extent, PygPE)

FRAME_RATE = 48000

class TestNoisePE(unittest.TestCase):

    def test_init(self):
        pe = NoisePE()
        self.assertIsInstance(pe, NoisePE)
        self.assertTrue(pe.extent().is_indefinite())
        self.assertIsNone(pe.frame_rate())
        self.assertEqual(pe.channel_count(), 1)

        pe = NoisePE(frame_rate=FRAME_RATE)
        self.assertIsInstance(pe, NoisePE)
        self.assertTrue(pe.extent().is_indefinite())
        self.assertEqual(pe.frame_rate(), FRAME_RATE)
        self.assertEqual(pe.channel_count(), 1)

    def test_render(self):
        e = Extent(0, 5)
        # DC
        pe = NoisePE(frame_rate=FRAME_RATE)
        got = pe.render(e)
        self.assertEqual(ut.frame_count(got), e.duration())
        self.assertEqual(ut.channel_count(got), 1)

    def test_extent(self):
        # already tested
        pass

    def test_frame_rate(self):
        # already tested
        pass

    def test_channel_count(self):
        # alredy tested
        pass
