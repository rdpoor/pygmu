import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import numpy as np
import pygmu as pg
import soundfile as sf
import utils as ut

src = pg.WavReaderPE("samples/s07.wav")

def dtor(degree):
    """
    Degrees to Radians
    """
    return np.pi * degree / 180.0

def dur(seconds):
    return int(seconds * src.frame_rate())

t = 0
def dt(dt):
    global t
    now = t
    t += dt
    return dur(now)

mix = pg.MixPE(
    # immobile (for reference)
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(1.5)),

    # pan using delay only
    pg.SpatialAPE(src, theta=dtor(90)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(72)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(54)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(36)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(18)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-18)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-36)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-54)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-72)).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-90)).delay(dt(1.5)),

    # pan using delay and gain
    # Note: gain_[lr] should not be linear since it leaves "hole in the middle"
    # with gain_l=0.5 and gain_r=0.5 (but still convincing sounding).  More 
    # likely that should be 0.7 or so.  Perhaps use db attenuation instead?
    pg.SpatialAPE(src, theta=dtor(90), gain_l=0.0, gain_r=1.0).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(72), gain_l=0.1, gain_r=0.9).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(54), gain_l=0.2, gain_r=0.8).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(36), gain_l=0.3, gain_r=0.7).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(18), gain_l=0.4, gain_r=0.6).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(0), gain_l=0.5, gain_r=0.5).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-18), gain_l=0.6, gain_r=0.4).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-36), gain_l=0.7, gain_r=0.3).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-54), gain_l=0.8, gain_r=0.2).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-72), gain_l=0.9, gain_r=0.1).delay(dt(0.25)),
    pg.SpatialAPE(src, theta=dtor(-90), gain_l=1.0, gain_r=0.0).delay(dt(0.25)),

)

pg.Transport(mix).play()
