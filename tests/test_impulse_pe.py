import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ImpulsePE, Extent, PygPE)

class TestImpulsePE(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        self.pe = ImpulsePE(1)
        self.assertIsInstance(self.pe, ImpulsePE)

    def test_render(self):
        e = Extent(-5, 0)
        self.pe = ImpulsePE()
        expect = np.array([[0, 0, 0, 0, 0]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(0, 5)
        self.pe = ImpulsePE()
        expect = np.array([[1, 0, 0, 0, 0]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(5, 10)
        self.pe = ImpulsePE()
        expect = np.array([[0, 0, 0, 0, 0]], dtype=np.float32)
        got = self.pe.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        self.pe = ImpulsePE()
        self.assertTrue(Extent().equals(self.pe.extent()))

    def test_frame_rate(self):
        self.pe = ImpulsePE()
        self.assertEqual(self.pe.frame_rate(), None)
        self.pe = ImpulsePE(frame_rate=1234)
        self.assertEqual(self.pe.frame_rate(), 1234)

    def test_channel_count(self):
        self.pe = ImpulsePE()
        self.assertEqual(self.pe.channel_count(), 1)

