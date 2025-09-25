import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
import utils as ut
class TestUtils(unittest.TestCase):

    def test_tuning(self):
        np.testing.assert_allclose([ut.PHI], [1.6180339887])
        np.testing.assert_allclose([ut.freq_to_nearest_just_freq(440)], [436.0429329888])
        np.testing.assert_allclose([ut.freq_to_nearest_just_freq(440)], [436.042932988])
        np.testing.assert_allclose([ut.freq_to_nearest_renold_freq(440)], [433.505226])
        np.testing.assert_allclose([ut.pitch_to_freq(60)], [261.6255653005986])
        np.testing.assert_allclose([ut.pitch_to_freq(69, "12TET", 440)], [440])
        np.testing.assert_allclose([ut.pitch_to_freq(69, "12TET", 432)], [432])
        np.testing.assert_allclose([ut.pitch_to_freq(69, "12TET", 412.557)], [412.557])
        np.testing.assert_allclose([ut.pitch_to_freq(69, "Just", 440)], [436.0429329888])
        np.testing.assert_allclose([ut.pitch_to_freq(69, "Renold", 440)], [441.5331008616])
        np.testing.assert_allclose([ut.pitch_to_freq(69 - 12, "Renold", 440)], [441.5331008616 / 2])

    def test_ratio_to_db(self):
        ratios = [100, 10, 1, 0.1, 0.01, 0.001]
        dbs = [40, 20, 0, -20, -40, -60]
        np.testing.assert_array_almost_equal(
            [ut.ratio_to_db(v) for v in ratios], 
            dbs)

    def test_db_to_ratio(self):
        dbs = [40, 20, 0, -20, -40, -60]
        ratios = [100, 10, 1, 0.1, 0.01, 0.001]
        np.testing.assert_array_almost_equal(
            [ut.db_to_ratio(v) for v in dbs], 
            ratios)
