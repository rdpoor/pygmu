import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
import utils as ut
import numpy as np
from pygmu import (ArrayPE, EnvDetectPE, Extent, PwmPE, PygPE)

class TestEnvDetectPE(unittest.TestCase):

    def test_render(self):
        extent = Extent(0, 24)
        src_pe = PwmPE(12, 0.5).crop(extent)
        pe = EnvDetectPE(src_pe, attack=0.9, release=0.5)
        dst = pe.render(extent)
        self.assertEqual(ut.channel_count(dst), 1)
        self.assertEqual(ut.frame_count(dst), extent.duration())
