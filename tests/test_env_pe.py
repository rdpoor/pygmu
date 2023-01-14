import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ConstPE, CropPE, EnvPE, Extent, PygPE)

class TestEnvPE(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        src_pe = CropPE(ConstPE(10), Extent(0, 10))
        pe = EnvPE(src_pe, up_dur=4, dn_dur=5)
        self.assertIsInstance(pe, EnvPE)

    def test_render1(self):
        """
        The source for pe1 is a ConstPE, cropped to 10 frames.  pe1 ramps
        up from 0 to 1 over 4 steps, holds for 1, then ramps down from 1 to 0
        over 5 steps.  It has the following [time, gain] values:
        [[0, 0.0, 1, 0.25, 2, 0.5, 3, 0.75, 4, 1.0], 
         [5, 1.0, 6, 0.8, 7, 0.6, 8, 0.4, 9, 0.2]]
        """
        src_pe = CropPE(ConstPE(10), Extent(0, 10))
        pe1 = EnvPE(src_pe, up_dur=4, dn_dur=5)

        e = Extent(-10, 0)       # no overlap
        expect = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-8, 2)       # partial overlap
        expect = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 2.5]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-6, 4)       # partial overlap
        expect = np.array([[0, 0, 0, 0, 0, 0, 0, 2.5, 5.0, 7.5]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-4, 6)       # partial overlap
        expect = np.array([[0, 0, 0, 0, 0, 2.5, 5.0, 7.5, 10.0, 10.0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-2, 8)       # partial overlap
        expect = np.array([[0, 0, 0, 2.5, 5.0, 7.5, 10.0, 10.0, 8.0, 6.0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(0, 10)       # full overlap
        expect = np.array([[0, 2.5, 5.0, 7.5, 10.0, 10.0, 8.0, 6.0, 4.0, 2.0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(2, 12)       # partial overlap
        expect = np.array([[5.0, 7.5, 10.0, 10.0, 8.0, 6.0, 4.0, 2.0, 0, 0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(4, 14)       # partial overlap
        expect = np.array([[10.0, 10.0, 8.0, 6.0, 4.0, 2.0, 0, 0, 0, 0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(6, 16)       # partial overlap
        expect = np.array([[8.0, 6.0, 4.0, 2.0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(8, 18)       # partial overlap
        expect = np.array([[4.0, 2.0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(10, 20)       # noverlap
        expect = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
        got = pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_render2(self):
        """
        Test case when down starts before ramp up completes

        The source for pe1 is a ConstPE, cropped to 6 frames.  pe1 ramps
        up from 0 to 1 over 4 steps, holds for 1, then ramps down from 1 to 0
        over 5 steps.  It has the following [time, gain] values:
        [[0, 0.0, 1, 0.25, 2, 0.5, 3, 0.6, 4, 0.4, [5, 0.2]]
        """
        src_pe = CropPE(ConstPE(10), Extent(0, 6))
        self.pe1 = EnvPE(src_pe, up_dur=4, dn_dur=5)

        e = Extent(-10, 0)       # no overlap
        expect = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-8, 2)       # partial overlap
        expect = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 2.5]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-6, 4)       # partial overlap
        expect = np.array([[0, 0, 0, 0, 0, 0, 0, 2.5, 5.0, 6.0]], dtype=np.float32)
        got = self.pe1.render(e)
        # print("expect=", expect, "got=", got)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-4, 6)       # partial overlap
        expect = np.array([[0, 0, 0, 0, 0, 2.5, 5.0, 6.0, 4.0, 2.0]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(-2, 8)       # full overlap
        expect = np.array([[0, 0, 0, 2.5, 5.0, 6.0, 4.0, 2.0, 0.0, 0.0]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(0, 10)       # full overlap
        expect = np.array([[0, 2.5, 5.0, 6.0, 4.0, 2.0, 0.0, 0.0, 0.0, 0.0]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(2, 12)       # partial overlap
        expect = np.array([[5.0, 6.0, 4.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(4, 14)       # partial overlap
        expect = np.array([[4.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

        e = Extent(6, 16)       # partial overlap
        expect = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
        got = self.pe1.render(e)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        # EnvPE inherits extent rate from source.
        src_pe = CropPE(ConstPE(10), Extent(0, 10))
        pe = EnvPE(src_pe, up_dur=4, dn_dur=5)
        self.assertTrue(src_pe.extent().equals(pe.extent()))

    def test_frame_rate(self):
        # EnvPE inherits frame_rate rate from source.
        src_pe = CropPE(ConstPE(10), Extent(0, 10))
        pe = EnvPE(src_pe, up_dur=4, dn_dur=5)
        self.assertEqual(src_pe.frame_rate(), pe.frame_rate())

    def test_channel_count(self):
        # EnvPE inherits channel_count from source.
        src_pe = CropPE(ConstPE(10), Extent(0, 10))
        pe = EnvPE(src_pe, up_dur=4, dn_dur=5)
        self.assertEqual(src_pe.channel_count(), pe.channel_count())

