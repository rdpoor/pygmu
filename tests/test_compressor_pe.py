import numpy as np
import os
import sys
import unittest

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pyg_exceptions as pyx
import utils as ut
from pygmu import (ArrayPE, CompressorPE, ConstPE, Extent, PygPE)

class TestCompressorPE(unittest.TestCase):

    def test_init(self):
        # Test envelope input is a ramp from -60db to +10db
        extent = Extent(-60, 10)
        sig_pe = ConstPE(1.0)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))

        # instance with default values
        pe = CompressorPE(sig_pe, env_pe)
        self.assertIsInstance(pe, CompressorPE)
        self.assertEqual(pe.ratio(), 2.0)
        self.assertEqual(pe.threshold_db(), 0.0)
        self.assertEqual(pe.makeup_db(), pe.threshold_db())
        self.assertTrue(pe.extent().equals(sig_pe.extent()))
        self.assertEqual(pe.channel_count(), sig_pe.channel_count())
        self.assertEqual(pe.frame_rate(), sig_pe.frame_rate())

        # Two channels
        sig2_pe = sig_pe.spread(2)
        pe = CompressorPE(sig2_pe, env_pe, threshold_db=-10, ratio=3.0, makeup_db=12)
        self.assertIsInstance(pe, CompressorPE)
        self.assertEqual(pe.ratio(), 3.0)
        self.assertEqual(pe.threshold_db(), -10)
        self.assertEqual(pe.makeup_db(), 12)
        self.assertTrue(pe.extent().equals(sig2_pe.extent()))
        self.assertEqual(pe.channel_count(), sig2_pe.channel_count())
        self.assertEqual(pe.frame_rate(), sig2_pe.frame_rate())

    def test_render(self):
        # Test envelope input is a ramp from -60db to +10db
        sig_pe = ConstPE(1.0)
        # env_pe maps f[i] = db_to_ratio[i-60]
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10).reshape(1, -1)))

        pe = CompressorPE(sig_pe, env_pe, threshold_db=-20, ratio=2, makeup_db=0)
        # compression ratio = 2:1, slope is 1 below -20 db, 1/ratio above -20 db

        # Because the input is a constant 1.0, the output == gain.  We want to
        # verify db(out), so we take db(in * gain).
        input_frames = env_pe.render(Extent(0, 70))
        gain_frames = pe.render(Extent(0, 70))
        db_in = ut.ratio_to_db(input_frames).reshape(-1)
        db_out = ut.ratio_to_db(input_frames * gain_frames).reshape(-1)

        # print(input_frames)
        # print(gain_frames)
        # print(db_out_frames)

        # Here:
        # db_in[X+60] is the compressor's input (= X db)
        # db_out[X+60] is the compressor's response to X db input

        thresh_db = pe.threshold_db()
        # At threshold, in_db == out_db == threshold
        db = thresh_db
        self.assertAlmostEqual(db_in[db+60], db, places=5)
        self.assertAlmostEqual(db_out[db+60], db, places=5)

        # at threshold + 1 db, out_db = threshold + 1/ratio
        db = thresh_db + 1
        self.assertAlmostEqual(db_in[db+60], thresh_db+1, places=5)
        self.assertAlmostEqual(db_out[db+60], thresh_db+(1/pe.ratio()), places=5)

        # at threshold - 1 db, out_db = threshold - 1db
        db = thresh_db - 1
        self.assertAlmostEqual(db_in[db+60], thresh_db-1, places=5)
        self.assertAlmostEqual(db_out[db+60], thresh_db-1, places=5)

        # no overlap case...
        sig_pe = ConstPE(1.0).crop(Extent(0, 10))
        env_pe = sig_pe
        pe = CompressorPE(sig_pe, env_pe)
        got_frames = pe.render(Extent(10, 20))
        expect_frames = np.zeros((1, pe.extent().duration()))
        np.testing.assert_array_almost_equal(got_frames, expect_frames)

    def test_extent(self):
        extent = Extent(-60, 10)

        sig_pe = ConstPE(1.0).crop(extent)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompressorPE(sig_pe, env_pe)
        self.assertTrue(pe.extent().equals(extent))

        sig_pe = ConstPE(1.0)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompressorPE(sig_pe, env_pe)
        self.assertTrue(pe.extent().is_indefinite())

    def test_frame_rate(self):
        sig_pe = ConstPE(1.0)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompressorPE(sig_pe, env_pe)
        self.assertIsNone(pe.frame_rate())

        sig_pe = ConstPE(1.0, frame_rate=1234)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompressorPE(sig_pe, env_pe)
        self.assertEqual(pe.frame_rate(), 1234)

    def test_channel_count(self):
        sig_pe = ConstPE(1.0, frame_rate=1234)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompressorPE(sig_pe, env_pe)
        self.assertEqual(pe.channel_count(), 1)

        sig_pe = ConstPE(1.0, frame_rate=1234).spread(2)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompressorPE(sig_pe, env_pe)
        self.assertEqual(pe.channel_count(), 2)
