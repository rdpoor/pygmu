import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import numpy as np
from pygmu import (CachePE, ArrayPE, Extent, PygPE)
import utils as ut


class CounterPE(PygPE):
    """
    Special purpose PE that counts calls to render()
    """

    def __init__(self, frame_count, channel_count):
        super(CounterPE, self).__init__()
        self._frame_count = frame_count
        self._channel_count = channel_count
        self._render_calls = 0

    def render(self, requested:Extent):
        self._render_calls += 1
        return ut.ramp_frames(0, self._frame_count, self._frame_count, self._channel_count)

    def extent(self):
        return Extent(0, self._frame_count)

    def channel_count(self):
        return self._channel_count

    def render_calls(self):
        return self._render_calls

class TestCachePE(unittest.TestCase):

    def test_init(self):
        src = CounterPE(5, 1)
        self.assertIsInstance(CachePE(src), CachePE)

    def test_render(self):
        src = CounterPE(5, 1)

        pe = CachePE(src)
        self.assertEqual(src.render_calls(), 1)

        pe.render(pe.extent())
        self.assertEqual(src.render_calls(), 1)

        pe.render(pe.extent())
        self.assertEqual(src.render_calls(), 1)

        np.testing.assert_array_almost_equal(
            pe.render(pe.extent()),
            src.render(pe.extent()))
