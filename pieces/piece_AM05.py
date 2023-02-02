import os
import sys
import numpy as np
import random

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

srate = 44100

def secs(s):
    return int(s * srate)

def mix_at(src, t, amp = 1):
    return pg.DelayPE(src,t).gain(amp)

def sterofy(frames):
    # convert horizontal mono array into stero frames (2 columns, N rows)
    return np.dot(frames.reshape(-1, 1), [[1.0, 1.0]])

def delays(src, secs, howmany = 1, decay = 1):
    frame_rate = 48000
    delay_units = []
    amp = 1 / howmany
    print('---------',src.channel_count())
    for i in range(1, howmany + 1):
        #delay_units.append(src.delay(int(i * secs * frame_rate)).gain(amp).lowpass(500))
        delay_units.append(src.delay(int(i * secs * frame_rate)).gain(amp))
        amp *= decay
    return pg.MixPE(src.gain(2/howmany),*delay_units)
    
def loopWindow(src,insk,dur):
    return pg.LoopPE(src.crop(pg.Extent(insk)).delay(-insk), dur)

def blit_note(pitch,t,dur,gain,harmonics):
    f = ut.pitch_to_freq(pitch)    
    return pg.BlitSawPE(frequency=f, n_harmonics=harmonics, frame_rate=srate).crop(pg.Extent(0, secs(dur))).gain(gain).delay(secs(t)).splice(100,100)
    #return pg.BlitsigPE(frequency=f, n_harmonics=harmonics, channel_count=1, frame_rate=48000, waveform=pg.BlitsigPE.SAWTOOTH).crop(pg.Extent(0, secs(dur))).gain(gain).delay(secs(t)).env(500,1000)

def render_cycle(pitches, pulses, dur, gain, harmonics, transpose=0, big_start=0):
    pi = 0
    t = big_start
    if transpose > 0:
        pitches = [x+transpose for x in pitches]

    #[x+1 for x in mylist]
    print('render_cycle',pitches)
    #map(lambda x:x+1, [1,2,3])
    while t < big_start + dur:
        for pitch in pitches:
            pulse = pulses[pi]
            pi = (pi + 1) % len(pulses)
            note = blit_note(pitch,t,pulse,gain,harmonics).pan(random.uniform(-90,90))
            elements.append(note)
            t += pulse
            if t > big_start + dur:
                break

def expand_cycle(a,type,b):
    ans = []
    for a_step in a:
        chroma_step = a_step
        match type:
            case 'chromatic':
                chroma_step = a_step
        for b_step in b:
            ans.append(b_step + a_step)
    return ans

def tone_cycle(base_pitch,a,type):
    ans = []
    for a_step in a:
        chroma_step = a_step
        ans.append(base_pitch + a_step)
    return ans

sourceA= pg.WavReaderPE("/Users/andy/Dev/python/pygmu/samples/DP2_108_Maxmex_Breakdown2.wav")

pulseA = 60 / 216

beatloop = loopWindow(sourceA,secs(0),secs(pulseA * 8)).crop(pg.Extent(start=0,end=secs(21)))

elements = []


gain = 0.17

pitch = 36
cycle_do_re = [0,-2,1,3,0]
cycle_do_re2 = [2,2,-2,0]
cycle_do_re3 = [-5,-3,0,2,-1,1]
cycle_do_do = [6,7]
cycle_abc = [0,4,3]
cycle_xyz = [0,2,1,4,-1,1]


doabc = expand_cycle(cycle_do_re, 'chromatic', cycle_abc)
doxyz = expand_cycle(cycle_do_re, 'chromatic', cycle_xyz)
doxyz2 = expand_cycle(cycle_do_re3, 'chromatic', cycle_xyz)
doxyz3 = expand_cycle(cycle_do_re2, 'chromatic', cycle_xyz)


cycle42 = tone_cycle(36, doabc, 'chromatic')
cycle36 = tone_cycle(42, doxyz, 'chromatic')
cycle50 = tone_cycle(50, doxyz2, 'chromatic')
cycle51 = tone_cycle(57, doxyz3, 'chromatic')


for i in range(1,15):

    big_t = 0

    pulse = pulseA / i

    render_cycle(cycle42, [pulse], 10, gain * 0.75, 4, 0 + i, big_t)
    render_cycle(cycle36, [pulse * 1.5], 10, gain * 0.25, 4, 12, big_t)
    render_cycle(cycle50, [pulse * 0.66], 10, gain * 0.09, 11, 0, big_t)
    render_cycle(cycle51, [pulse * 0.3], 10, gain * 0.05, 5 ,0, big_t)

    render_cycle(cycle42, [pulse, pulse * 2], 10, gain * 0.07, 4 + i, 24, big_t)
    render_cycle(cycle36, [pulse], 10, gain * 0.25, 4, 12, big_t)
    render_cycle(cycle50, [pulse * 0.66, pulse * 1.4], 10, gain * 0.07, 6, 12, big_t)
    render_cycle(cycle51, [pulse * 0.3], 10, gain * 0.007, 5 ,24, big_t)
    render_cycle(cycle51, [pulse * 0.32], 10, gain * 0.007, 5 ,2 * i, big_t)
    render_cycle(cycle51, [pulse * 0.34], 10, gain * 0.007, 5 ,2 * i, big_t)
    render_cycle(cycle51, [pulse * 0.37], 10, gain * 0.007, 5 ,2 * i, big_t)


    big_t = 10

    render_cycle(cycle42, [pulse], 10, gain * 0.75, 4, 2, big_t)
    render_cycle(cycle36, [pulse * 1.5], 10, gain * 0.25, 4, 14, big_t)
    render_cycle(cycle50, [pulse * 0.66], 10, gain * 0.09, 11, 2, big_t)
    render_cycle(cycle51, [pulse * 0.3], 10, gain * 0.05, 5 ,2, big_t)

    render_cycle(cycle42, [pulse, pulse * 2], 10, gain * 0.07, 4, 24, big_t)
    render_cycle(cycle36, [pulse], 10, gain * 0.25, 4, 12, big_t)
    render_cycle(cycle50, [pulse * 0.66, pulse * 1.4], 10, gain * 0.07, 6, 12, big_t)
    render_cycle(cycle51, [pulse * 0.3], 10, gain * 0.007, 5 ,24, big_t)
    render_cycle(cycle51, [pulse * 0.32], 10, gain * 0.007, 5 ,28, big_t)
    render_cycle(cycle51, [pulse * 0.34], 10, gain * 0.007, 5 ,28, big_t)
    render_cycle(cycle51, [pulse * 0.37], 10, gain * 0.007, 5 ,28, big_t)


mixA = pg.MixPE(*elements)

syrup_mixA = delays(mixA, pulse, 5, 0.85)

mixB = pg.MixPE(syrup_mixA, beatloop.gain(0.5))

impulse = pg.WavReaderPE('samples/IR/Small Prehistoric Cave.wav')
convolved = pg.ConvolvePE(mixB.gain(0.25), impulse)

#convolved.term_play('live',0)
convolved.play()

