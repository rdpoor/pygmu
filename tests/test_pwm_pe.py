import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (PwmPE, Extent, PygPE)

class TestPwmPE(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        self.pe = PwmPE(10, 0.5)
        self.assertIsInstance(self.pe, PwmPE)

    def test_render(self):
        e = Extent(0, 12)
        self.pe = PwmPE(10, 0.1)
        expect = np.array([[1], [0], [0], [0], [0], [0], [0], [0], [0], [0], [1], [0]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        self.pe = PwmPE(10, 0.2)
        expect = np.array([[1], [1], [0], [0], [0], [0], [0], [0], [0], [0], [1], [1]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        self.pe = PwmPE(10, 0.5)
        expect = np.array([[1], [1], [1], [1], [1], [0], [0], [0], [0], [0], [1], [1]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        self.pe = PwmPE(10, 0.9)
        expect = np.array([[1], [1], [1], [1], [1], [1], [1], [1], [1], [0], [1], [1]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        self.pe = PwmPE(4, 0.5)
        expect = np.array([[1], [1], [0], [0], [1], [1], [0], [0], [1], [1], [0], [0]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        self.pe = PwmPE(4, 0.25)
        expect = np.array([[1], [0], [0], [0], [1], [0], [0], [0], [1], [0], [0], [0]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        self.pe = PwmPE(4, 0.5, 1)
        self.assertTrue(Extent().equals(self.pe.extent()))

    def test_frame_rate(self):
        self.pe = PwmPE(4, 0.5, 1)
        self.assertEqual(self.pe.frame_rate(), PygPE.DEFAULT_FRAME_RATE)

    def test_channel_count(self):
        self.pe = PwmPE(4, 0.5, 1)
        self.assertEqual(self.pe.channel_count(), 1)
        self.pe = PwmPE(4, 0.5, 2)
        self.assertEqual(self.pe.channel_count(), 2)

