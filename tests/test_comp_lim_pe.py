import numpy as np
import os
import sys
import unittest

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pyg_exceptions as pyx
import utils as ut
from pygmu import (ArrayPE, CompLimPE, ConstPE, Extent, PygPE)

class TestCompLimPE(unittest.TestCase):

    def test_init(self):
        # Test envelope input is a ramp from -60db to +10db
        extent = Extent(-60, 10)
        sig_pe = ConstPE(1.0)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))

        # instance with default values
        pe = CompLimPE(sig_pe, env_pe)
        self.assertIsInstance(pe, CompLimPE)
        self.assertEqual(pe.ratio(), 2.0)
        self.assertEqual(pe.limit_db(), 0.0)
        self.assertEqual(pe.squelch_db(), -50.0)

        pe = CompLimPE(sig_pe, env_pe, ratio=3.0, limit_db=-4.0, squelch_db=-60)
        self.assertIsInstance(pe, CompLimPE)
        self.assertEqual(pe.ratio(), 3.0)
        self.assertEqual(pe.limit_db(), -4.0)
        self.assertEqual(pe.squelch_db(), -60.0)

    def test_render(self):
        # Test envelope input is a ramp from -60db to +10db
        sig_pe = ConstPE(1.0)
        # env_pe maps f[i] = db_to_ratio[i-60]
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10).reshape(1, -1)))

        pe = CompLimPE(sig_pe, env_pe)
        # compression ratio = 2:1, squelch with slope 10 db below 50 db,
        # hard limit above 0db
        x1 = pe.limit_db()
        y1 = pe.limit_db()
        x0 = pe.squelch_db()
        y0 = (1 / pe.ratio()) * (x0 - x1) + y1

        # because the input is a constant 1.0, the output == gain
        # when the input is -50 db (x0), the output is -25 db (y0, ratio=2),
        # os the gain is +25 db
        gain = pe.render(Extent(0, 70)).reshape(-1) # convert to 1D for convenience
        db_gain = ut.ratio_to_db(gain)
        # The expected output (y) in db is input (x) + gain (db)
        # my brain is too soggy to figure out the squelch value...
        # self.assertAlmostEqual(db_gain[int(x0-1)+60]+x0, CompLimPE.SQUELCH_SLOPE)
        self.assertAlmostEqual(db_gain[int(x0)+60]+x0, y0, places=5)
        self.assertAlmostEqual(db_gain[int(x1)+60]+x1, y1, places=5)
        self.assertAlmostEqual(db_gain[int(x1+1)+60]+1, y1, places=5)  # limiting...

        # no overlap case...
        sig_pe = ConstPE(1.0).crop(Extent(0, 10))
        env_pe = sig_pe
        pe = CompLimPE(sig_pe, env_pe)
        got_frames = pe.render(Extent(10, 20))
        expect_frames = np.zeros((1, pe.extent().duration()))
        np.testing.assert_array_almost_equal(got_frames, expect_frames)

    def test_extent(self):
        extent = Extent(-60, 10)

        sig_pe = ConstPE(1.0).crop(extent)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompLimPE(sig_pe, env_pe)
        self.assertTrue(pe.extent().equals(extent))

        sig_pe = ConstPE(1.0)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompLimPE(sig_pe, env_pe)
        self.assertTrue(pe.extent().is_indefinite())

    def test_frame_rate(self):
        sig_pe = ConstPE(1.0)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompLimPE(sig_pe, env_pe)
        self.assertIsNone(pe.frame_rate())

        sig_pe = ConstPE(1.0, frame_rate=1234)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompLimPE(sig_pe, env_pe)
        self.assertEqual(pe.frame_rate(), 1234)

    def test_channel_count(self):
        sig_pe = ConstPE(1.0, frame_rate=1234)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompLimPE(sig_pe, env_pe)
        self.assertEqual(pe.channel_count(), 1)

        sig_pe = ConstPE(1.0, frame_rate=1234).spread(2)
        env_pe = ArrayPE(ut.db_to_ratio(np.arange(-60, 10)))
        pe = CompLimPE(sig_pe, env_pe)
        self.assertEqual(pe.channel_count(), 2)
