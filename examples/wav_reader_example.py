import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

src = pg.WavReaderPE("samples/loops/Bpm200_GuitarRiff_DigNoise_D_PL.wav")
# Start calling render() on the WaveReaderPE
pg.Transport(src).play()
