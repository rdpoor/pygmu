import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
import utils as ut
from pygmu import (ConstPE, EnvDetectPE, Extent)

class TestEnvDetectPE(unittest.TestCase):

    def test_render(self):
        # mono, full overlap
        amp = 0.5
        src_extent = Extent(0, 5)
        src_pe = ConstPE(amp).crop(src_extent)

        rqst_extent = Extent(0, 5)
        pe = EnvDetectPE(src_pe, attack=1.0, release=1.0)
        got = pe.render(rqst_extent)
        # with attack and release = 1.0...
        expect = np.array([[amp, amp, amp, amp, amp]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(ut.channel_count(got), src_pe.channel_count())
        self.assertEqual(ut.frame_count(got), rqst_extent.duration())

        # mono, partial overlap
        amp = 0.5
        src_extent = Extent(2, 7)
        src_pe = ConstPE(amp).crop(src_extent)

        rqst_extent = Extent(0, 5)
        pe = EnvDetectPE(src_pe, attack=1.0, release=1.0)
        got = pe.render(rqst_extent)
        # with attack and release = 1.0, expect single sample delay...
        expect = np.array([[0, 0, amp, amp, amp]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)

        # mono, no overlap
        amp = 0.5
        src_extent = Extent(5, 10)
        src_pe = ConstPE(amp).crop(src_extent)

        rqst_extent = Extent(0, 5)
        pe = EnvDetectPE(src_pe, attack=1.0, release=1.0)
        got = pe.render(rqst_extent)
        # with attack and release = 1.0, expect single sample delay...
        expect = np.array([[0, 0, 0, 0, 0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)

        # stereo, full overlap
        amp = 0.5
        src_extent = Extent(0, 5)
        src_pe = ConstPE(amp).crop(src_extent).spread()

        rqst_extent = Extent(0, 5)
        pe = EnvDetectPE(src_pe, attack=1.0, release=1.0)
        got = pe.render(rqst_extent)
        # with attack and release = 1.0, expect single sample delay...
        expect = np.array([[amp, amp, amp, amp, amp], [amp, amp, amp, amp, amp]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)
        self.assertEqual(ut.channel_count(got), src_pe.channel_count())
        self.assertEqual(ut.frame_count(got), rqst_extent.duration())

        # stero, partial overlap
        amp = 0.5
        src_extent = Extent(2, 7)
        src_pe = ConstPE(amp).crop(src_extent).spread()

        rqst_extent = Extent(0, 5)
        pe = EnvDetectPE(src_pe, attack=1.0, release=1.0)
        got = pe.render(rqst_extent)
        # with attack and release = 1.0, expect single sample delay...
        expect = np.array([[0, 0, amp, amp, amp], [0, 0, amp, amp, amp]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)

        # stereo, no overlap
        amp = 0.5
        src_extent = Extent(5, 10)
        src_pe = ConstPE(amp).crop(src_extent).spread()

        rqst_extent = Extent(0, 5)
        pe = EnvDetectPE(src_pe, attack=1.0, release=1.0)
        got = pe.render(rqst_extent)
        # with attack and release = 1.0, expect single sample delay...
        expect = np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)

        # units = db
        ratio = 12.34
        db = ut.ratio_to_db(ratio)
        src_extent = Extent(0, 5)
        src_pe = ConstPE(ratio).crop(src_extent)

        rqst_extent = Extent(0, 5)
        pe = EnvDetectPE(src_pe, attack=1.0, release=1.0, units='db')
        got = pe.render(rqst_extent)
        # with attack and release = 1.0, expect single sample delay...
        expect = np.array([[db, db, db, db, db]], dtype=np.float32)
        np.testing.assert_array_almost_equal(got, expect)

    def test_extent(self):
        # EnvDetectPE inherits extent from src_pe
        src_pe = ConstPE(0).crop(Extent(5, 10))
        pe = EnvDetectPE(src_pe, attack=1.0, release=1.0)
        self.assertEqual(src_pe.extent(), pe.extent())

    def test_frame_rate(self):
        # EnvDetectPE inherits frame_frate from src_pe
        src_pe = ConstPE(0, frame_rate=12345)
        pe = EnvDetectPE(src_pe)
        self.assertEqual(src_pe.frame_rate(), pe.frame_rate())
