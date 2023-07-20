import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import numpy as np
import pygmu as pg
import soundfile as sf

def secs(s):
    return int(s * 48000)

def delays(src, secs, howmany = 1, decay = 1):
    frame_rate = 48000
    delay_units = []
    amp = 1
    for i in range(1, howmany):
        #delay_units.append(src.time_shift(int(i * secs * frame_rate)).gain(amp).pan(random.uniform(-90,90)))
        delay_units.append(src.time_shift(int(i * secs * frame_rate)).gain(amp))
        amp *= decay
    return pg.MixPE(src,*delay_units)

def mix_at(src, t, amp = 1):
    return pg.TimeShiftPE(src,t).gain(amp)

impulse = pg.WavReaderPE('samples/IR/Conic Long Echo Hall.wav')
impulse2 = pg.WavReaderPE('samples/IR/VoxPlateNo2.wav')
impulse3 = pg.WavReaderPE('samples/IR/Large Wide Echo Hall.wav')

lum1  = pg.WavReaderPE("samples/music/TamperFrame_SugarPlumFaries_Edit2.wav").crop(pg.Extent(secs(0.15),secs(33)))
lum1_slow = pg.WarpSpeedPE(lum1, 0.3).gain(0.35)
lum1_slow2 =  pg.BQ2HighPassPE(lum1_slow, f0=312, q=6)
lum1_convolved = pg.ConvolvePE(lum1_slow2.gain(0.11), impulse)
lum1_convolved2 = pg.ConvolvePE(lum1_convolved.gain(0.11), impulse2)
lum1_convolved3 = pg.ConvolvePE(lum1_convolved2.gain(0.11), impulse3)
lum1_convolved4 = pg.ConvolvePE(lum1_convolved3.gain(0.11), impulse).crop(pg.Extent(secs(12),secs(42)))





lum2  = pg.WavReaderPE("samples/music/TamperFrame_SugarPlumFaries_Edit2.wav").crop(pg.Extent(secs(0),secs(12))).reverse(9)


lum2_slow = pg.WarpSpeedPE(lum2, 0.13).gain(1.05)


lum2_slow2 =  pg.BQ2HighPassPE(lum2_slow, f0=312, q=6)



lum2_convolved = pg.ConvolvePE(lum2_slow2.gain(0.11), impulse)
lum2_convolved2 = pg.ConvolvePE(lum2_convolved.gain(0.21), impulse2)



Train1 = pg.WavReaderPE("samples/music/Waiting_For_A_Train_Rogers.wav").crop(pg.Extent(secs(0.15),secs(33)))
Train1HP = pg.BQ2HighPassPE(Train1, f0=3612, q=6).gain(0.8)
Train1Slow = pg.WarpSpeedPE(Train1HP, 0.24).gain(1.6)


Train1Rev_conv = pg.ConvolvePE(Train1Slow.gain(0.08), impulse3)
Train1Rev_conv2 = pg.ConvolvePE(Train1Rev_conv.gain(0.08), impulse)

Train1Rev_conv2.crop(pg.Extent(secs(0),secs(96)))



elements = []

t = 0
gain = 0.685

elements.append(mix_at(lum1_convolved4,secs(t),gain))

t += 11.5
gain = 0.78
elements.append(mix_at(Train1Rev_conv2,secs(t),0.93))


mosh = pg.MixPE(*elements).warp_speed(0.92)

mosh.pygplay('Lum')




