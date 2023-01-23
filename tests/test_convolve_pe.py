import numpy as np
import os
import sys
import unittest

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pyg_exceptions as pyx
import utils as ut
from pygmu import (ArrayPE, ConvolvePE, Extent, ImpulsePE, NoisePE)

class TestConvolvePE(unittest.TestCase):

    # For testing, We use an inpulse function as the filter, since 
    # convolving a signal with an impulse yields the original signal.

    def test_init(self):
        extent = Extent(0, 20)
        src_pe = NoisePE()
        filter_pe = ImpulsePE()

        # Constructor yields a ConvolvePE
        pe = ConvolvePE(src_pe, filter_pe.crop(extent))
        self.assertIsInstance(pe, ConvolvePE)


    def test_render(self):
        extent = Extent(0, 1000)
        src_pe = NoisePE()
        filter_pe = ImpulsePE()

        # mono source, mono filter
        pe = ConvolvePE(src_pe, filter_pe.crop(Extent(0, 10)))
        dst_frames = pe.render(extent)
        self.assertEqual(ut.frame_count(dst_frames), extent.duration())
        self.assertEqual(ut.channel_count(dst_frames), 1)

        # stereo source, mono filter
        pe = ConvolvePE(src_pe.spread(2), filter_pe.crop(Extent(0, 10)))
        dst_frames = pe.render(extent)
        self.assertEqual(ut.frame_count(dst_frames), extent.duration())
        self.assertEqual(ut.channel_count(dst_frames), 2)

        # mono source, stereo filter
        pe = ConvolvePE(src_pe, filter_pe.spread(2).crop(Extent(0, 10)))
        dst_frames = pe.render(extent)
        self.assertEqual(ut.frame_count(dst_frames), extent.duration())
        self.assertEqual(ut.channel_count(dst_frames), 2)

        # mono source, mono filter
        pe = ConvolvePE(src_pe.spread(2), filter_pe.spread(2).crop(Extent(0, 10)))
        dst_frames = pe.render(extent)
        self.assertEqual(ut.frame_count(dst_frames), extent.duration())
        self.assertEqual(ut.channel_count(dst_frames), 2)

        # test no overlap
        pe = ConvolvePE(src_pe.crop(Extent(0, 100)), filter_pe.crop(Extent(0, 10)))
        got = pe.render(Extent(200, 300))
        expect = np.zeros([1, 100])
        np.testing.assert_array_almost_equal(got, expect)


    def test_extent(self):
        extent = Extent(0, 20)
        src_pe = NoisePE()
        filter_pe = ImpulsePE()

        # indefinite source => indefinite output
        pe = ConvolvePE(src_pe, filter_pe.crop(extent))
        self.assertTrue(pe.extent().is_indefinite())

        # finite source => finite output
        pe = ConvolvePE(src_pe.crop(extent), filter_pe.crop(extent))
        self.assertFalse(pe.extent().is_indefinite())

        # indefinite filter raises an error
        with self.assertRaises(pyx.IndefiniteExtent):
            ConvolvePE(src_pe, filter_pe)


    def test_frame_rate(self):
        extent = Extent(0, 20)

        # no frame rate on source or filter => no frame rate on output
        pe = ConvolvePE(NoisePE(), ImpulsePE().crop(extent))
        self.assertIsNone(pe.frame_rate())

        # frame rate on source => frame rate on output
        pe = ConvolvePE(NoisePE(frame_rate=1234), ImpulsePE().crop(extent))
        self.assertEqual(pe.frame_rate(), 1234)
        
        # frame rate on filter => frame rate on output
        pe = ConvolvePE(NoisePE(), ImpulsePE(frame_rate=5678).crop(extent))
        self.assertEqual(pe.frame_rate(), 5678)

        # matching frame rate on both => frame rate on output
        pe = ConvolvePE(NoisePE(frame_rate=1111), ImpulsePE(frame_rate=1111).crop(extent))
        self.assertEqual(pe.frame_rate(), 1111)

        # mismatching frame rate on both raise an error
        with self.assertRaises(pyx.FrameRateMismatch):
            ConvolvePE(NoisePE(frame_rate=1111), 
                       ImpulsePE(frame_rate=2222).crop(extent))

    def test_channel_count(self):
        extent = Extent(0, 20)
        src_pe1 = NoisePE()
        src_pe2 = NoisePE().spread(2)
        filter_pe1 = ImpulsePE()
        filter_pe2 = ImpulsePE().spread(2)

        # mono source, mono filter => mono output
        pe = ConvolvePE(src_pe1, filter_pe1.crop(extent))
        self.assertEqual(pe.channel_count(), 1)

        # stereo source, mono filter => stereo out
        pe = ConvolvePE(src_pe2, filter_pe1.crop(extent))
        self.assertEqual(pe.channel_count(), 2)

        # mono source, stereo filter => stereo out
        pe = ConvolvePE(src_pe1, filter_pe2.crop(extent))
        self.assertEqual(pe.channel_count(), 2)

        # stereo source, stereo filter => stereo out
        pe = ConvolvePE(src_pe2, filter_pe2.crop(extent))
        self.assertEqual(pe.channel_count(), 2)

        # too many source channels raises an error
        with self.assertRaises(pyx.ChannelCountMismatch):
            ConvolvePE(src_pe1.spread(3), filter_pe1.crop(extent))

        # too many filter channels raises an error
        with self.assertRaises(pyx.ChannelCountMismatch):
            ConvolvePE(src_pe1, filter_pe1.crop(extent).spread(3))
