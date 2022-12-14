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

def stof(seconds):
    return int(seconds * src.frame_rate())

mix = pg.MixPE(
    pg.SpatialAPE(src, theta=dtor(90)).delay(stof(0)),
    pg.SpatialAPE(src, theta=dtor(72)).delay(stof(0.5)),
    pg.SpatialAPE(src, theta=dtor(54)).delay(stof(1.0)),
    pg.SpatialAPE(src, theta=dtor(36)).delay(stof(1.5)),
    pg.SpatialAPE(src, theta=dtor(18)).delay(stof(2.0)),
    pg.SpatialAPE(src, theta=dtor(0)).delay(stof(2.5)),
    pg.SpatialAPE(src, theta=dtor(-18)).delay(stof(3.0)),
    pg.SpatialAPE(src, theta=dtor(-36)).delay(stof(3.5)),
    pg.SpatialAPE(src, theta=dtor(-54)).delay(stof(4.0)),
    pg.SpatialAPE(src, theta=dtor(-72)).delay(stof(4.5)),
    pg.SpatialAPE(src, theta=dtor(-90)).delay(stof(5.0)),
)

pg.Transport(mix).play()
