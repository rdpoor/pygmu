import pygmu as pg
import numpy as np

pluck = pg.WavReaderPE('../samples/044-n-2723_stero.wav')
pg.Transport(pg.TralfamPE(pluck)).play()
