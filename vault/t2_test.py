import os
import sys
import time
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import pygui as pui


"""
Test T2

The best way to run this:

% python -i t2_example.py
>>> t2.play()
>>> t2.pause()
>>> t2.play(speed=1.5)
>>> t2.play(speed=-1.0)
>>> t2.stop()
"""

src = pg.WavReaderPE("samples/TamperFrame_AfternoonOfAFaun.wav")
t2 = pg.T2(src)


t2.play()

pui.start_pygui()