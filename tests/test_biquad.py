import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ArrayPE, BiquadPE, Extent, FrameRateMismatch)

class TestBiquadPE(unittest.TestCase):

    def test_init(self):
        # Mono source
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=1234)
        print("==== ArrayPE frame_rate=", src.frame_rate())
        pe = BiquadPE(src)
        self.assertIsInstance(pe, BiquadPE)
        self.assertTrue(pe.extent().equals(src.extent()))
        self.assertEquals(pe.channel_count(), src.channel_count())
        self.assertEquals(pe.frame_rate(), src.frame_rate())

        # Stereo source
        src = ArrayPE(np.zeros([2, 5], dtype=np.float32), frame_rate=1234)
        pe = BiquadPE(src)
        self.assertIsInstance(pe, BiquadPE)
        self.assertTrue(pe.extent().equals(src.extent()))
        self.assertEquals(pe.channel_count(), src.channel_count())
        self.assertEquals(pe.frame_rate(), src.frame_rate())

        # BiquadPE requires a known frame rate
        src = ArrayPE(np.zeros([2, 5], dtype=np.float32), frame_rate=None)
        with self.assertRaises(FrameRateMismatch):
            pe = BiquadPE(src)

    def test_render(self):
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=1234)
        pe = BiquadPE(src)
        expect = src.render(src.extent())
        got = pe.render(src.extent())
        np.testing.assert_array_almost_equal(got, expect)
