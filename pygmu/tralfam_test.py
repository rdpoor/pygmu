import pygmu as pg
import numpy as np

pluck = pg.WavReaderPE('../samples/044-n-2723_stero.wav')
mogrify = pg.TralfamPE(pluck)
pg.Transport().play(mogrify)
