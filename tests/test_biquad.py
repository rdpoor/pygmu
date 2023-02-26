import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ArrayPE, BiquadPE, BQLowPassPE, BQHighPassPE, BQBandPassPE,
        BQBandRejectPE, BQAllPassPE, BQPeakPE, BQLowShelfPE, BQHighShelfPE,
        Extent, ChannelCountMismatch, FrameRateMismatch)

class TestBiquadPE(unittest.TestCase):

    def test_init(self):
        # Mono source
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=1234)
        pe = BQLowPassPE(src, f0=440, q=20)
        self.assertIsInstance(pe, BiquadPE)
        self.assertTrue(pe.extent().equals(src.extent()))
        self.assertEqual(pe.channel_count(), src.channel_count())
        self.assertEqual(pe.frame_rate(), src.frame_rate())

        # BiquadPE requires a known frame rate
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=None)
        with self.assertRaises(FrameRateMismatch):
            pe = BiquadPE(src)

        # BiquadPE requires a mono source
        src = ArrayPE(np.zeros([2, 5], dtype=np.float32), frame_rate=44100)
        with self.assertRaises(ChannelCountMismatch):
            pe = BiquadPE(src)

    def test_coeffs_a(self):
        # test coefficients derived from
        #   https://www.earlevel.com/main/2021/09/02/biquad-calculator-v3/
        src = ArrayPE(np.zeros([1, 5], dtype=np.float32), frame_rate=44100)
        pe = BQLowPassPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.9929499544928433,
            0.99687248213489,
            0.0009806319105117329,
            0.0019612638210234658,
            0.0009806319105117329])
        pe = BQHighPassPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.9929499544928433,
            0.99687248213489,
            0.9974556091569333,
            -1.9949112183138666,
            0.9974556091569333])
        pe = BQBandPassPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.9929499544928433,
            0.99687248213489,
            0.0015637589325549896,
            0,
            -0.0015637589325549896])
        pe = BQBandRejectPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.9929499544928433,
            0.99687248213489,
            0.998436241067445,
            -1.9929499544928433,
            0.998436241067445])
        pe = BQAllPassPE(src, f0=440, q=20)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
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
            pe.coeffs(),
            [-1.9929499544928433,
            0.99687248213489,
            1.0015563503352678,
            -1.9929499544928433,
            0.9953161317996221])
        pe = BQPeakPE(src, f0=440, q=20, gain_db=0)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.9929499544928433,
            0.99687248213489,
            1,
            -1.9929499544928433,
            0.99687248213489])
        pe = BQPeakPE(src, f0=440, q=20, gain_db=-6)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.989853046037509,
            0.9937694783388304,
            0.9984460681271236,
            -1.989853046037509,
            0.9953234102117071])
        pe = BQLowShelfPE(src, f0=440, gain_db=6)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.9113981953542545,
            0.9151602126790416,
            1.0184358472917574,
            -1.909526098318444,
            0.8985964624230943])
        pe = BQLowShelfPE(src, f0=440, gain_db=0)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.9113981953542545,
            0.9151602126790416,
            1,
            -1.9113981953542545,
            0.9151602126790416])
        pe = BQLowShelfPE(src, f0=440, gain_db=-6)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.8749596289214383,
            0.8823299619830329,
            0.9818978806168475,
            -1.8767978370332095,
            0.8985938732544143])
        pe = BQHighShelfPE(src, f0=440, gain_db=6)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.9113981953542545,
            0.9151602126790416,
            1.9696071436595646,
            -3.8156128851256788,
            1.8497677587909012])
        pe = BQHighShelfPE(src, f0=440, gain_db=0)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
            [-1.9113981953542545,
            0.9151602126790416,
            1,
            -1.9113981953542545,
            0.9151602126790416])
        pe = BQHighShelfPE(src, f0=440, gain_db=-6)
        np.testing.assert_array_almost_equal(
            pe.coeffs(),
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