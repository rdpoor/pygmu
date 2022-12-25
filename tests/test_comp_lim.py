import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import utils as ut
import numpy as np
from pygmu import (ArrayPE, CompLimPE, ConstPE, Extent, PygPE)

class TestCompLimPE(unittest.TestCase):

    def setUp(self):
        self.env_pe = ArrayPE(np.array([
            -65, -60, -55, -50, -45, -40, -35, -30,
            -25, -20, -15, -10, -5, 0, 5, 10]).reshape(-1, 1), 
            channel_count=1)
        self.extent = self.env_pe.extent()
        self.src_pe = (
            ConstPE(1.0, channel_count=1)
            .crop(self.extent))

    def test_init(self):
        pe = CompLimPE(self.src_pe, self.env_pe)
        self.assertIsInstance(pe, CompLimPE)
        self.assertEqual(pe.ratio(), 2.0)
        self.assertEqual(pe.limit_db(), 0.0)
        self.assertEqual(pe.squelch_db(), -50.0)

        pe = CompLimPE(
            self.src_pe, self.env_pe, ratio=10.0, limit_db=-10, 
            squelch_db=-40)
        self.assertIsInstance(pe, CompLimPE)
        self.assertEqual(pe.ratio(), 10.0)
        self.assertEqual(pe.limit_db(), -10.0)
        self.assertEqual(pe.squelch_db(), -40.0)

    def test_render(self):
        pe = CompLimPE(self.src_pe, self.env_pe)
        # compression ratio = 2:1, squelch with slope 10db below 50 db,
        # hard limit above 0db
        expect_db = np.array([
            -175, -125, -75, -25, -22.5, -20, -17.5, -15,
            -12.5, -10, -7.5, -5, -2.5, 0, 0, 0]).reshape(-1, 1)
        got_ratio = pe.render(self.extent)
        got_db = ut.ratio_to_db(got_ratio)
        np.testing.assert_array_almost_equal(got_db, expect_db)

        pe = CompLimPE(self.src_pe, self.env_pe, squelch_db = -100.0)
        # compression ratio = 2:1, squelch with slope 10db below -100 db
        # (effectively disabled), hard limit above 0db.
        expect_db = np.array([
            -32.5, -30, -27.5, -25, -22.5, -20, -17.5, -15,
            -12.5, -10, -7.5, -5, -2.5, 0, 0, 0]).reshape(-1, 1)
        got_ratio = pe.render(self.extent)
        got_db = ut.ratio_to_db(got_ratio)
        np.testing.assert_array_almost_equal(got_db, expect_db)

        pe = CompLimPE(self.src_pe, self.env_pe, limit_db = -10.0)
        # compression ratio = 2:1, squelch with slope 10db below 50 db,
        # hard limit above -10db
        expect_db = np.array([
            -180.0, -130.0, -80.0, -30.0, -27.5, -25.0, -22.5, -20.0,
            -17.5, -15.0, -12.5, -10.0, -10.0, -10.0, -10.0, -10.0]).reshape(-1, 1)
        got_ratio = pe.render(self.extent)
        got_db = ut.ratio_to_db(got_ratio)
        np.testing.assert_array_almost_equal(got_db, expect_db)

        pe = CompLimPE(self.src_pe, self.env_pe, ratio = 10.0)
        # compression ratio = 10:1, squelch with slope 10db below 50 db,
        # hard limit above 0db
        expect_db = np.array([
            -155.0, -105.0, -55.0, -5.0, -4.5, -4.0, -3.5, -3.0,
            -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.0, 0.0]).reshape(-1, 1)
        got_ratio = pe.render(self.extent)
        got_db = ut.ratio_to_db(got_ratio)
        np.testing.assert_array_almost_equal(got_db, expect_db)

        # stereo source, mono envelope
        env_pe = ArrayPE(np.array([
            -65, -60, -55, -50, -45, -40, -35, -30,
            -25, -20, -15, -10, -5, 0, 5, 10]).reshape(-1, 1), 
            channel_count=1)
        self.extent = env_pe.extent()
        self.src_pe = ConstPE(1.0, channel_count=2).crop(self.extent)
        pe = CompLimPE(self.src_pe, self.env_pe)
        # compression ratio = 2:1, squelch with slope 10db below 50 db,
        # hard limit above 0db
        expect_db = np.array([[-175, -175],
                              [-125, -125],
                              [-75, -75],
                              [-25, -25],
                              [-22.5, -22.5],
                              [-20, -20],
                              [-17.5, -17.5],
                              [-15, -15],
                              [-12.5, -12.5],
                              [-10, -10],
                              [-7.5, -7.5],
                              [-5, -5],
                              [-2.5, -2.5],
                              [0, 0],
                              [0, 0],
                              [0, 0]])
        got_ratio = pe.render(self.extent)
        got_db = ut.ratio_to_db(got_ratio)
        np.testing.assert_array_almost_equal(got_db, expect_db)

        # stereo source, stereo envelope
        src_pe = ArrayPE(np.array([[1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1],
                                   [1.0, 0.1]]))
        env_pe = ArrayPE(np.array([[-65, -65],
                                   [-60, -60],
                                   [-55, -55],
                                   [-50, -50],
                                   [-45, -45],
                                   [-40, -40],
                                   [-35, -35],
                                   [-30, -30],
                                   [-25, -25],
                                   [-20, -20],
                                   [-15, -15],
                                   [-10, -10],
                                   [-5, -5],
                                   [0, 0],
                                   [5, 5],
                                   [10, 10]]))
        self.extent = env_pe.extent()
        pe = CompLimPE(src_pe, env_pe)
        # compression ratio = 2:1, squelch with slope 10db below 50 db,
        # hard limit above 0db.  Right channel is 20 db lower than left.
        expect_db = np.array([[-175, -195],
                              [-125, -145],
                              [-75, -95],
                              [-25, -45],
                              [-22.5, -42.5],
                              [-20, -40],
                              [-17.5, -37.5],
                              [-15, -35],
                              [-12.5, -32.5],
                              [-10, -30],
                              [-7.5, -27.5],
                              [-5, -25],
                              [-2.5, -22.5],
                              [0, -20],
                              [0, -20],
                              [0, -20]])
        got_ratio = pe.render(self.extent)
        got_db = ut.ratio_to_db(got_ratio)
        np.testing.assert_array_almost_equal(got_db, expect_db)


    def test_extent(self):
        pe = CompLimPE(self.src_pe, self.env_pe)
        self.assertTrue(pe.extent().equals(self.extent))

    def test_frame_rate(self):
        pe = CompLimPE(self.src_pe, self.env_pe)
        self.assertEqual(pe.frame_rate(), self.src_pe.frame_rate())

    def test_channel_count(self):
        pe = CompLimPE(self.src_pe, self.env_pe)
        self.assertEqual(pe.channel_count(), self.src_pe.channel_count())

