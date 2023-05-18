
# This bit of boilerplate allows Python to find the pygmu library
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

import importlib

def is_module_installed(name):
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False

if not is_module_installed('music21'):
    print("would be better with music21 installed!")
    note_list = [pg.Note(0, 0.5, 60), pg.Note(1, 0.5, 62), pg.Note (2, 0.5, 64), pg.Note (3, 0.5, 65), pg.Note (4, 0.5, 67)]
else:
    note_list = pg.get_notes_from_midi("vault/earle_of_salisbury.mid")
    # book1-prelude-01 earle_of_salisbury.mid frederic-chopin-nocturne-no20 scriabin_prelude_11
    note_list = note_list[:78]

sin_pe = pg.SinPE(frequency = 512, amplitude = 1, frame_rate = 48000).gain(0.25)
src_pe = pg.WavReaderPE("samples/multisamples/Seaward_Piano/Seaward_Piano_ppp_C4.wav")
#src_pe = pg.WavReaderPE("samples/multisamples/LOA_Piano/LOA_Piano_C4.wav")

note_pe = pg.NotesPE(src_pe, note_list, 95, 0.25, 72,0,0.2)
note_pe.play()

note_pe2 = pg.NotesPE(sin_pe, note_list, 95, 0.25, 72, 0.1 ,0.1)
note_pe2.play()



