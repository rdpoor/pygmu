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

pg.Transport(f1).play()
pg.Transport(pg.GaneshPE(f1, f1, True)).play()
pg.Transport(pg.GaneshPE(f1, f2, True)).play()
pg.Transport(pg.GaneshPE(f1, f3, True)).play()
pg.Transport(f2).play()
pg.Transport(pg.GaneshPE(f2, f2, True)).play()
pg.Transport(pg.GaneshPE(f2, f1, True)).play()
pg.Transport(pg.GaneshPE(f2, f3, True)).play()
pg.Transport(f3).play()
pg.Transport(pg.GaneshPE(f3, f3, True)).play()
pg.Transport(pg.GaneshPE(f3, f1, True)).play()
pg.Transport(pg.GaneshPE(f3, f2, True)).play()

