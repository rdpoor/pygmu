import unittest
import numpy as np
import os
import sys

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pyg_exceptions as pyx
from pygmu import (ConstPE, Extent, PygPE, SpatialPE)

class TestSpatialPE(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        src = ConstPE(0.0, frame_rate=1234)
        self.assertIsInstance((SpatialPE(src)), SpatialPE)

    def test_render(self):
        pass

    def test_extent(self):
        pass

    def test_frame_rate(self):
        pass

    def test_channel_count(self):
        pass

