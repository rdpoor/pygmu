import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ArrayPE, Biquad2PE, BQLowPassPE, BQHighPassPE, BQBandPassPE,
        BQBandRejectPE, BQAllPassPE, BQPeakPE, BQLowShelfPE, BQHighShelfPE,
        Extent, ChannelCountMismatch, FrameRateMismatch)

class TestBiquad2PE(unittest.TestCase):

    def test_init(self):
        # Mono source
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=1234)
        pe = BQLowPassPE(src, f0=440, q=20)
        self.assertIsInstance(pe, Biquad2PE)
        self.assertTrue(pe.extent().equals(src.extent()))
        self.assertEqual(pe.channel_count(), src.channel_count())
        self.assertEqual(pe.frame_rate(), src.frame_rate())

        # Biquad2PE requires a known frame rate
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=None)
        with self.assertRaises(FrameRateMismatch):
            pe = Biquad2PE(src)

        # Biquad2PE accepts a stereo source
        src = ArrayPE(np.zeros([2, 5], dtype=np.float32), frame_rate=44100)
        pe = BQLowPassPE(src, f0=440, q=20)
        self.assertIsInstance(pe, Biquad2PE)
        self.assertTrue(pe.extent().equals(src.extent()))
        self.assertEqual(pe.channel_count(), src.channel_count())
        self.assertEqual(pe.frame_rate(), src.frame_rate())

    def test_coeffs_a(self):
        # test coefficients derived from
        #   https://www.earlevel.com/main/2021/09/02/biquad-calculator-v3/
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=44100)
        pe = BQLowPassPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9929499544928433,
            0.99687248213489,
            0.0009806319105117329,
            0.0019612638210234658,
            0.0009806319105117329])
        pe = BQHighPassPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9929499544928433,
            0.99687248213489,
            0.9974556091569333,
            -1.9949112183138666,
            0.9974556091569333])
        pe = BQBandPassPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9929499544928433,
            0.99687248213489,
            0.0015637589325549896,
            0,
            -0.0015637589325549896])
        pe = BQBandRejectPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9929499544928433,
            0.99687248213489,
            0.998436241067445,
            -1.9929499544928433,
            0.998436241067445])
        pe = BQAllPassPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9929499544928433,
            0.99687248213489,
            0.99687248213489,
            -1.9929499544928433,
            1])

    def test_coeffs_b(self):
        # test coefficients derived from
        #   https://www.earlevel.com/main/2021/09/02/biquad-calculator-v3/
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=44100)
        pe = BQPeakPE(src, f0=440, q=20, gain_db=6)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9929499544928433,
            0.99687248213489,
            1.0015563503352678,
            -1.9929499544928433,
            0.9953161317996221])
        pe = BQPeakPE(src, f0=440, q=20, gain_db=0)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9929499544928433,
            0.99687248213489,
            1,
            -1.9929499544928433,
            0.99687248213489])
        pe = BQPeakPE(src, f0=440, q=20, gain_db=-6)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.989853046037509,
            0.9937694783388304,
            0.9984460681271236,
            -1.989853046037509,
            0.9953234102117071])
        pe = BQLowShelfPE(src, f0=440, gain_db=6)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9113981953542545,
            0.9151602126790416,
            1.0184358472917574,
            -1.909526098318444,
            0.8985964624230943])
        pe = BQLowShelfPE(src, f0=440, gain_db=0)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9113981953542545,
            0.9151602126790416,
            1,
            -1.9113981953542545,
            0.9151602126790416])
        pe = BQLowShelfPE(src, f0=440, gain_db=-6)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.8749596289214383,
            0.8823299619830329,
            0.9818978806168475,
            -1.8767978370332095,
            0.8985938732544143])
        pe = BQHighShelfPE(src, f0=440, gain_db=6)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9113981953542545,
            0.9151602126790416,
            1.9696071436595646,
            -3.8156128851256788,
            1.8497677587909012])
        pe = BQHighShelfPE(src, f0=440, gain_db=0)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9113981953542545,
            0.9151602126790416,
            1,
            -1.9113981953542545,
            0.9151602126790416])
        pe = BQHighShelfPE(src, f0=440, gain_db=-6)
        np.testing.assert_array_almost_equal(
            pe.get_coefficients(),
            [-1.9372456570380847,
            0.939155691400469,
            0.5077154615422355,
            -0.9704464169452813,
            0.46464098976543])

    def test_render(self):
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=44100)
        pe = BQLowPassPE(src, f0=440, q=20)
        frames = pe.render(src.extent());
        self.assertEqual(frames.size, src.extent().duration())

    def test_render2(self):
        src = ArrayPE([[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]], frame_rate=44100)
        pe = BQLowPassPE(src, f0=440, q=2)
        frames = pe.render(src.extent());
        # derived from known working example (but warrants confirmation)
        np.testing.assert_array_almost_equal(
            frames,
            [[0.        , 0.00096702, 0.00480155, 0.01236733, 0.02352002,
              0.03810586, 0.05596255, 0.07692014, 0.10080193, 0.12742535,
              0.15660288, 0.18814286, 0.22185046, 0.25752842, 0.29497797,
              0.33399963, 0.37439395, 0.41596237, 0.45850787, 0.50183575]])


