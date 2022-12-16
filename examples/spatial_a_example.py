import os
import sys
import numpy as np

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

src = pg.WavReaderPE("samples/s07.wav")

t = 0
def dt(dt):
    global t
    now = t
    t += dt
    return int(now * src.frame_rate())

mix = pg.MixPE(
    # pan using delay and gain
    # Note: cosine curve attempts to overcome "hole in the middle"
    pg.SpatialAPE(src, degree=90, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=72, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=54, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=36, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=18, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=0, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-18, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-36, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-54, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-72, curve='cosine').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-90, curve='cosine').delay(dt(1.5)),

    # pan using delay and gain
    # Note: linear leaves a "hole in the middle"
    pg.SpatialAPE(src, degree=90, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=72, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=54, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=36, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=18, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=0, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-18, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-36, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-54, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-72, curve='linear').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-90, curve='linear').delay(dt(1.5)),

    # pan using delay only
    pg.SpatialAPE(src, degree=90, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=72, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=54, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=36, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=18, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=0, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-18, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-36, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-54, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-72, curve='none').delay(dt(0.25)),
    pg.SpatialAPE(src, degree=-90, curve='none').delay(dt(1.5)),

)

pg.Transport(mix).play()
