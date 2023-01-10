import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Play with pg.GaneshPE
"""

print("hit return after each example to hear the next")

f1 = pg.WavReaderPE("samples/multisamples/HarmonicGuitar-C3.wav")
f2 = pg.WavReaderPE("samples/multisamples/Seaward_Piano_ppp_D3.wav")
f3 = pg.WavReaderPE("samples/multisamples/Violin_Undul_C3_RM.wav")

print("Guitar")
pg.Transport(f1).play()
print("Guitar head, guitar body")
pg.Transport(pg.GaneshPE(f1, f1, True)).play()
print("Guitar head, piano body")
pg.Transport(pg.GaneshPE(f1, f2, True)).play()
print("Guitar head, violin body")
pg.Transport(pg.GaneshPE(f1, f3, True)).play()
print("Piano")
pg.Transport(f2).play()
print("piano head, piano body")
pg.Transport(pg.GaneshPE(f2, f2, True)).play()
print("piano head, guitar body")
pg.Transport(pg.GaneshPE(f2, f1, True)).play()
print("piano head, violin body")
pg.Transport(pg.GaneshPE(f2, f3, True)).play()
print("Violin")
pg.Transport(f3).play()
print("violin head, violin body")
pg.Transport(pg.GaneshPE(f3, f3, True)).play()
print("violin head, guitar body")
pg.Transport(pg.GaneshPE(f3, f1, True)).play()
print("violin head, piano body")
pg.Transport(pg.GaneshPE(f3, f2, True)).play()

