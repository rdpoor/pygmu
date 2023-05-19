import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut
import soundfile as sf

src_gain = 0.05
src_gain_adjust = 0

src_name = "samples/music/TamperClip93.wav"
src_gain_adjust = 0.4

# src_name = "samples/100_Radiator_Rattle.wav"
# src_gain_adjust = 0

# src_name = "samples/PED_95_BapBeat_Full_Drums.wav"
src_name = "samples/loops/AcousticDrumLoopsSiggi_Track47_104bpm.wav"
src_gain_adjust = 0.1
# src_name = "samples/BigBeat4_BigBeat5drumloops120bpm.wav"
# src_name = "samples/TamperClip93.wav"
# src_name = "samples/TamperClip93.wav"

src = pg.WavReaderPE(src_name).gain(src_gain + src_gain_adjust)
src_info = sf.info(src_name, True)

IR_dir = "samples/IR"
available_IRs =  list(filter(lambda s: s[0] != '.', os.listdir(IR_dir)))
output_filename = "user_files/renders/convolve_example.wav"

def show_IRS():
    print('')
    print("\t 0\t-  None")
    i = 1
    for s in available_IRs:
        print("\t",i,"\t- ",os.path.split(s)[1])
        i += 1

user_input = ''

while True:
    if user_input == '':
        show_IRS()
        print('\nEnter IR or \'return\' to quit:')
        user_input = input()
    if user_input == '':
        exit()

    user_index = int(user_input) - 1
    full_path = IR_dir+"/"+available_IRs[user_index]

    if user_index >= 0:
        info = sf.info(full_path, True)
        impulse = pg.WavReaderPE(full_path)
        sr_color =  ut.ansicodes.ENDC
        if info.samplerate != src_info.samplerate:
            sr_color =  ut.ansicodes.WARNING
        print(ut.ansicodes.OKCYAN)
        print(full_path,ut.ansicodes.ENDC,'\tduration: ',ut.ansicodes.OKCYAN,round(info.duration,2),ut.ansicodes.ENDC,'secs nchans: ',info.channels,'sr: ',sr_color,info.samplerate,ut.ansicodes.ENDC)
        convolved = pg.ConvolvePE(src, impulse)
    else:
        convolved = src
        print('none')
        
    convolved = pg.WavWriterPE(convolved, output_filename)

    pg.FtsTransport(convolved).play()
    user_input = pg.Transport(pg.WavReaderPE(output_filename)).play()