import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import random
import utils as ut
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


def good_gravy(src,window_start, window_duration, walk_rate, final_duration, flip_flag):
    els = []
    st_frame = secs(window_start)
    cur_frame = 0
    final_frame = secs(final_duration)
    walk_frames = secs(walk_rate)
    window_frames = secs(window_duration)
    overlap_frames = 200
    if overlap_frames > window_frames:
        overlap_frames = window_frames / 3
    even_odd = True

    while(cur_frame < final_frame):
        g = src.crop(pg.Extent(st_frame, st_frame + window_frames)).time_shift(cur_frame).splice(overlap_frames,overlap_frames)
        if not even_odd:
            g = g.reverse(window_frames)
        els.append(g)
        st_frame += walk_frames
        cur_frame += window_frames - overlap_frames
        even_odd = not even_odd

    return pg.MixPE(*els)

def splay(src, show_meter=True, max_silent_frames=300):
    output_filename = "/tmp/gravy_etude_01.wav"
    syrup_mix = pg.WavWriterPE(src, output_filename)
    pg.FtsTransport(syrup_mix).play()
    out = pg.WavReaderPE(output_filename)
    while True:
        print('press return to end playback, q to exit, space to replay',end='\r')
        ret = pg.Transport(out).play(show_meter, max_silent_frames)
        match ret:
            case 32:
                ut.clear_term_lines(3)
                if ut.terminal_has_ansi_support:
                    print(ut.ansicodes.PREVLINE,end='\r')
                print('')
            case _:
                return('')

dur = 33

sourceA= pg.WavReaderPE("samples/ItsGonnaRain_Original.wav")

# window_start:float, window_duration:float, walk_rate:float, flip_flag: bool)

# gravy = pg.GravyPE(sourceA,secs(2.95),secs(.17),secs(0.005),False).crop(pg.Extent(start=0,end=secs(dur)))
# gravy2 = pg.GravyPE(sourceA,secs(3.15),secs(.22),secs(0.0078),False).crop(pg.Extent(start=0,end=secs(dur)))
# gravy3 = pg.GravyPE(sourceA,secs(6.95),secs(.11),secs(0.0008),False).crop(pg.Extent(start=0,end=secs(dur)))
# gravy4 = pg.GravyPE(sourceA,secs(1.95),secs(.05),secs(0.00083),False).crop(pg.Extent(start=0,end=secs(dur)))
# frag1a = delays(gravy, 0.36,15,0.8).env(secs(2),100)
# frag2a = delays(gravy2, 0.39,6,0.98).env(secs(2),100)
# frag3a = delays(gravy3, 0.49,6,0.98).env(secs(2),100)
# frag4a = delays(gravy4, 0.29,6,0.98).env(secs(2),100)


frag1a = good_gravy(sourceA, 2.85, 0.07, 0.002, dur, True).pan(-40).splice(secs(2),100)
frag2a = good_gravy(sourceA, 3.13, 0.04, 0.005, dur, True).pan(10).splice(secs(2),100)
frag3a = good_gravy(sourceA, 3.83, 0.02, 0.002, dur, True).pan(35).splice(secs(2),100)
frag4a = good_gravy(sourceA, 14.13, 0.024, 0.0014, dur, True).pan(0).splice(secs(2),100)


elements = []

gain = 1.5

t = 0
elements.append(mix_at(frag1a,secs(t),gain * 0.25))

t += 6

elements.append(mix_at(frag2a,secs(t),gain * 0.15))

t += 6

elements.append(mix_at(frag1a.reverse(dur),secs(t),gain * 0.25))
elements.append(mix_at(frag3a,secs(t),gain * 0.25))
elements.append(mix_at(frag4a,secs(t),gain * 0.25))

mosh =  pg.LimiterPE(pg.MixPE(*elements))

mosh_del = delays(mosh, 0.52, 5, 0.57)

mosh_del = mosh
moshr =  mosh.reverse(dur).splice(secs(2),100)
all = pg.MixPE(mosh_del,moshr)
all_del = delays(all, 0.4, 3, 0.57)

splay(all_del, True, 0)
