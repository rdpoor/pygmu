import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
from pygmu import (utils)
import numpy as np
class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        pass

    def test_render(self):
        pass

    def test_extent(self):
        pass

    def test_frame_rate(self):
        pass

    def test_channel_count(self):
        pass

    def test_tuning(self):
        np.testing.assert_allclose([utils.PHI], [1.6180339887])
        np.testing.assert_allclose([utils.freq_to_nearest_just_freq(440)], [436.0429329888])
        np.testing.assert_allclose([utils.freq_to_nearest_just_freq(440)], [436.042932988])
        np.testing.assert_allclose([utils.freq_to_nearest_renold_freq(440)], [433.505226])
        np.testing.assert_allclose([utils.pitch_to_freq(60)], [261.6255653005986])
        np.testing.assert_allclose([utils.pitch_to_freq(69, "12TET", 440)], [440])
        np.testing.assert_allclose([utils.pitch_to_freq(69, "12TET", 432)], [432])
        np.testing.assert_allclose([utils.pitch_to_freq(69, "12TET", 412.557)], [412.557])
        np.testing.assert_allclose([utils.pitch_to_freq(69, "Just", 440)], [436.0429329888])
        np.testing.assert_allclose([utils.pitch_to_freq(69, "Renold", 440)], [441.5331008616])
        np.testing.assert_allclose([utils.pitch_to_freq(69 - 12, "Renold", 440)], [441.5331008616 / 2])

TestUtils().test_tuning()
