import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import unittest
from pygmu import (utils)

def rnd_digits(wut):
    max_digits = 1000000000000
    return round(wut * max_digits) / max_digits


class TestTuning(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        pass

    def test_render(self):
        self.assertTrue(utils.PHI == 1.6180339887)
        self.assertTrue(utils.noteLetters[3] == 'D#')
        self.assertTrue(utils.freq_to_nearest_just_freq(440) == 436.0429329888192)
        self.assertTrue(utils.freq_to_nearest_renold_freq(440) == 441.5331008616805)
        self.assertTrue(utils.note_to_freq(60) == 261.6255653005986)
        self.assertTrue(utils.note_to_freq(69, "12TET", 440) == 440)
        self.assertTrue(utils.note_to_freq(69, "12TET", 432) == 432)
        self.assertTrue(utils.note_to_freq(69, "12TET", 412.557) == 412.557)
        self.assertTrue(utils.note_to_freq(69, "Just", 440) == 436.0429329888192)
        self.assertTrue(utils.note_to_freq(69, "Renold", 440) == 441.5331008616805)
        self.assertTrue(rnd_digits(utils.note_to_freq(69 - 12, "Renold", 440)) == rnd_digits(441.5331008616805 / 2))
        
    def test_extent(self):
        pass

    def test_frame_rate(self):
        pass

    def test_channel_count(self):
        pass

TestTuning().test_render()
