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

TamperClip50  = pg.WavReaderPE("samples/music/TamperClip50.wav")
TamperClip50_slow = pg.WarpSpeedPE(TamperClip50, 0.3).gain(0.35)
TamperClip50_slow2 =  pg.BQ2HighPassPE(TamperClip50_slow, f0=312, q=6)
TamperClip50_convolved = pg.ConvolvePE(TamperClip50_slow2.gain(0.11), impulse)
TamperClip50_convolved2 = pg.ConvolvePE(TamperClip50_convolved.gain(0.11), impulse2)
TamperClip50_convolved3 = pg.ConvolvePE(TamperClip50_convolved2.gain(0.11), impulse3)
TamperClip50_convolved4 = pg.ConvolvePE(TamperClip50_convolved3.gain(0.11), impulse)


Watts1 = pg.WavReaderPE("samples/spoken/Alan Watts Humanity Within the Universe.mp3").crop(pg.Extent(secs(124),secs(337))).time_shift(int(-secs(124)))

#wenv = pg.EnvDetectPE(Watts1, attack=0.09, release=0.21)
#Watts1Compressed = pg.CompressorPE(Watts1, wenv, ratio=3.0, threshold_db=-20, makeup_db=2)
# dst = pg.WavWriterPE(Watts1Compressed, "user_files/renders/Watts1Compressed.wav")
# pg.FtsTransport(dst).play()
# Watts1Compressed2 = pg.WavReaderPE("user_files/renders/Watts1Compressed.wav")

#Watts1Rev = Watts1.reverse(25)

Watts1_HP = pg.BQ2HighPassPE(Watts1, f0=110, q=8).gain(0.68)

Gleason1 = pg.WavReaderPE("samples/music/PrettyGirl_Gleason.wav").crop(pg.Extent(secs(0.75),secs(92)))

#env = pg.EnvDetectPE(Gleason1, attack=0.9, release=0.0001)
#Gleason1Compressed = pg.CompressorPE(Gleason1, env, ratio=3.0, threshold_db=-20, makeup_db=2)
#Gleason1Slow = pg.WarpSpeedPE(Gleason1Compressed, 0.4)

Gleason1Slow = pg.WarpSpeedPE(Gleason1, 0.4).gain(1.6)
Gleason1Slow_HP = pg.BQ2HighPassPE(Gleason1Slow, f0=412, q=4).gain(0.7)
Gleason1Rev = Gleason1Slow_HP.reverse(33)

convolved = pg.ConvolvePE(Gleason1Slow_HP.gain(0.08), impulse)

insk = secs(12)
dur = secs(42)
Swan1 = pg.WavReaderPE("samples/music/SwanLakeOp-ActIIConcl.wav").reverse(41).crop(pg.Extent(secs(0),secs(31)))
Swan1Slow = pg.WarpSpeedPE(Swan1, 0.4)
Swan1Slow_HP = pg.BQ2HighPassPE(Swan1Slow, f0=1712, q=6).splice(secs(3),secs(8))
Swan1Slow_F = pg.BQ2LowPassPE(Swan1Slow, f0=7712, q=4)
Swan1Slow_convolved = pg.ConvolvePE(Swan1Slow_F.gain(0.28), impulse)

# Swan1Slow_convolved.pygplay()
# Gleason1Rev.pygplay()

Train1 = pg.WavReaderPE("samples/music/Waiting_For_A_Train_Rogers.wav").crop(pg.Extent(secs(0.15),secs(33)))
Train1HP = pg.BQ2HighPassPE(Train1, f0=3612, q=6).gain(0.8)
Train1Slow = pg.WarpSpeedPE(Train1HP, 0.24).gain(1.6)




Train1Rev_conv = pg.ConvolvePE(Train1Slow.gain(0.08), impulse3)
Train1Rev_conv2 = pg.ConvolvePE(Train1Rev_conv.gain(0.08), impulse)

convolved_watts = pg.ConvolvePE(Watts1_HP.gain(0.08), impulse2)
convolved_watts_rev = pg.ConvolvePE(Watts1_HP.reverse(244).gain(0.08), impulse2).reverse(244)
convolved_watts_rev_lp = pg.BQ2LowPassPE(convolved_watts_rev, f0=1110, q=8)

elements = []

t = 0
gain = 0.685

elements.append(mix_at(convolved,secs(t),0.71))
elements.append(mix_at(Train1Rev_conv2,secs(0.8),0.14))
elements.append(mix_at(Swan1Slow_convolved.splice(secs(43),secs(8)),secs(61.3),0.43)) # bass at branches express the tree
elements.append(mix_at(Swan1Slow_convolved,secs(140.8),0.61)) # witts out of you

t += 11.5
gain = 0.78
elements.append(mix_at(Watts1_HP,secs(t),0.93))
elements.append(mix_at(convolved_watts,secs(t),0.82))
elements.append(mix_at(convolved_watts_rev_lp,secs(t),0.32))

elements.append(mix_at(TamperClip50_convolved4,secs(54),0.21))


mosh = pg.MixPE(*elements).warp_speed(0.92)

mosh.pygplay('We Belong In This World')




