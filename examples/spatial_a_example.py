import os
import sys
import numpy as np

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("samples/sfx/s07.wav")

t = 0
def dt(dt):
    global t
    now = t
    t += dt
    return int(now * src.frame_rate())

mix = pg.MixPE(
    # pan using delay and gain
    # Note: cosine curve attempts to overcome "hole in the middle"
    pg.SpatialPE(src, degree=90, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=72, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=54, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=36, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=18, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=0, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-18, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-36, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-54, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-72, curve='cosine').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-90, curve='cosine').time_shift(dt(1.5)),

    # pan using delay and gain
    # Note: linear leaves a "hole in the middle"
    pg.SpatialPE(src, degree=90, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=72, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=54, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=36, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=18, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=0, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-18, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-36, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-54, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-72, curve='linear').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-90, curve='linear').time_shift(dt(1.5)),

    # pan using delay only
    pg.SpatialPE(src, degree=90, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=72, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=54, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=36, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=18, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=0, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-18, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-36, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-54, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-72, curve='none').time_shift(dt(0.25)),
    pg.SpatialPE(src, degree=-90, curve='none').time_shift(dt(1.5)),

)

pg.Transport(mix).play()
