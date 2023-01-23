import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (ArrayPE, CachePE, Extent, IdentityPE, PygPE)
import utils as ut
import pyg_exceptions as pyx


class CounterPE(PygPE):
    """
    Special purpose PE that counts calls to render()
    """

    def __init__(self, channel_count, frame_count):
        super(CounterPE, self).__init__()
        self._channel_count = channel_count
        self._frame_count = frame_count
        self._render_calls = 0

    def render(self, requested:Extent):
        self._render_calls += 1
        return ut.ramp_frames(0, self._frame_count, self._channel_count, self._frame_count)

    def extent(self):
        return Extent(0, self._frame_count)

    def channel_count(self):
        return self._channel_count

    def render_calls(self):
        return self._render_calls

class TestCachePE(unittest.TestCase):

    def test_init(self):
        src = CounterPE(1, 5)
        self.assertIsInstance(CachePE(src), CachePE)
        self.assertEqual(CachePE(src).channel_count(), src.channel_count())
        with self.assertRaises(pyx.IndefiniteExtent):
            CachePE(IdentityPE())

    def test_render(self):
        src = CounterPE(1, 5)
        self.assertEqual(src.render_calls(), 0)

        pe = CachePE(src)
        self.assertEqual(src.render_calls(), 1)

        pe.render(pe.extent())
        self.assertEqual(src.render_calls(), 1)

        pe.render(pe.extent())
        self.assertEqual(src.render_calls(), 1)

        np.testing.assert_array_almost_equal(
            pe.render(pe.extent()),
            src.render(pe.extent()))

    def test_channel_count(self):
        src = CounterPE(1, 5)
        self.assertEqual(CachePE(src).channel_count(), src.channel_count())

    def test_frame_rate(self):
        src = CounterPE(1, 5)
        self.assertEqual(CachePE(src).frame_rate(), src.frame_rate())

