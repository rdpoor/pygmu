import os
import sys
import unittest
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
from pygmu import (Extent, GainPE, IdentityPE, RampPE)

class TestGainPE(unittest.TestCase):

    def test_init(self):
        src = IdentityPE();
        pe = GainPE(src, 1.0)
        self.assertIsInstance(pe, GainPE)

    def test_render(self):
        src = IdentityPE()

        pe = GainPE(src, 1.0)
        expect = np.array([[0, 1, 2, 3, 4]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, -2.0)
        expect = np.array([[0, -2, -4, -6, -8]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, 1.0).crop(Extent(2, 4))
        expect = np.array([[0, 0, 2, 3, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src.crop(Extent(2, 4)), 1.0)
        expect = np.array([[0, 0, 2, 3, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, src)
        expect = np.array([[0, 1, 4, 9, 16]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src.crop(Extent(2, 4)), src)
        expect = np.array([[0, 0, 4, 9, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, src.crop(Extent(2, 4)))
        expect = np.array([[0, 0, 4, 9, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        # no overlap
        pe = GainPE(src, src.crop(Extent(0, 5)))
        expect = np.array([[0, 0, 0, 0, 0]])
        got = pe.render(Extent(5, 10))
        np.testing.assert_array_almost_equal(got, expect)


    def test_render_db(self):
        src = IdentityPE()

        pe = GainPE(src, 0, units='db')
        expect = np.array([[0, 1, 2, 3, 4]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, -20.00, units='db')
        expect = np.array([[0, .1, .2, .3, .4]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        pe = GainPE(src, 20.00, units='db')
        expect = np.array([[0, 10, 20, 30, 40]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        # GainPE extent is shorter than src
        pe = GainPE(src, 0, units='db').crop(Extent(2, 4))
        expect = np.array([[0, 0, 2, 3, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        # GainPE extent is longer than src
        pe = GainPE(src.crop(Extent(2, 4)), 0, units='db')
        expect = np.array([[0, 0, 2, 3, 0]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        # dynamic gain input
        gain_pe = RampPE(-40, 60, Extent(0, 5))  # [-40, -20, 0, 20, 40]
        pe = GainPE(src, gain_pe, units='db')
        expect = np.array([[0, .1, 2, 30, 400]], dtype=np.float32)
        got = pe.render(Extent(0, 5))
        np.testing.assert_array_almost_equal(got, expect)

        # dynamic gain with no overlap
        gain_pe = RampPE(-40, 60, Extent(0, 5))  # [-40, -20, 0, 20, 40]
        pe = GainPE(src.crop(Extent(0, 5)), gain_pe, units='db')
        expect = np.array([[0, 0, 0, 0, 0]])
        got = pe.render(Extent(5, 10))
        np.testing.assert_array_almost_equal(got, expect)


    def test_extent(self):
        src = IdentityPE()
        expected_extent = Extent(2, 4)

        pe = GainPE(src, 1.0)
        self.assertTrue(pe.extent().equals(Extent()))  # infinite extent

        pe = GainPE(src.crop(expected_extent), 1.0)
        self.assertTrue(pe.extent().equals(expected_extent)) # src limited

        pe = GainPE(src.crop(expected_extent), src)
        self.assertTrue(pe.extent().equals(expected_extent)) # src limited

        pe = GainPE(src, src.crop(expected_extent))
        self.assertTrue(pe.extent().equals(expected_extent)) # gain limited


    def test_frame_rate(self):
        src = IdentityPE(frame_rate = 1234)
        pe = GainPE(src, 1.0)
        self.assertEqual(pe.frame_rate(), 1234)

    def test_channel_count(self):
        src = IdentityPE().spread(2)
        pe = GainPE(src, 1.0)
        self.assertEqual(pe.channel_count(), 2)

