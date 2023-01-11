import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import random
import utils as ut
import tempfile
from sport import Sport


prior = ut.use_ansi_when_avaible

ut.use_ansi_when_avaible = False

# term_play(meter_type='live', max_silent_frames=300, max_dur_secs_for_infinite_sources=100)
# play(meter_type='live, max_silent_frames=300)

ut.print_info('ansi status:',ut.terminal_has_ansi_support(),ut.use_ansi_when_avaible,'\n')


sourceA= pg.WavReaderPE("samples/ItsGonnaRain_Original.wav").gain(7)
sourceB= pg.WavReaderPE("samples/BigBeat120bpm10.wav").gain(2)
monoSource= pg.WavReaderPE("samples/Sine_C4.wav") 

filename = tempfile.gettempdir()+'/sport.wav'
dst = pg.WavWriterPE(sourceA, filename)

max_secs = 1

ut.print_info('\tplay()\n\t\tdefault -- no meter, continue after default seconds.\n')
ret = Sport(sourceB).play() 


ut.print_info('\tterm_play()\n\t\tdefault -- meter, continue after default seconds.\n')
ret = Sport(sourceB).term_play() 

ut.print_info('\tplay(\'bars\')\n\t\tmeter, continue after default seconds.\n')
ret = Sport(sourceB).play('bars') 

ut.print_info('\tplay(\'live\')\n\t\tmeter (should fallback to bars since we have no ansi), continue after default seconds.\n')
ret = Sport(sourceB).play('live') 

ut.print_info('\tplay()\n\t\tmono signal, default -- no meter, continue after default seconds\n')
ret = Sport(monoSource).play()

ut.print_info('\tterm_play()\n\t\tmono signal, default -- meter, continue after default seconds\n')
ret = Sport(monoSource).term_play()

ut.print_info('\tterm_play(\'bars\',0)\n\t\tmono signal, bars meter, should wait for return before continuing\n')
ret = Sport(monoSource).term_play('bars',0)


ut.print_info('FtsTransport rendering....')
pg.FtsTransport(dst).play()
ut.print_info('\tplay()\n\t\tno meter, continue after default seconds.\n')
Sport(pg.WavReaderPE(filename)).play()


ut.print_info('FtsTransport rendering....')
pg.FtsTransport(dst).play()
ut.print_info('\tterm_play()\n\t\tdefault  -- meter, continue after default seconds.\n')
Sport(pg.WavReaderPE(filename)).term_play()


ut.use_ansi_when_avaible = True

if not ut.terminal_has_ansi_support():
    ut.print_info('No ansi on this terminal, test finished.')
    exit('')


ut.print_warn('Turning ansi on.\n')


ut.print_info('\tplay()\n\t\tdefault -- no meter, continue after default seconds.\n')
ret = Sport(sourceB).play() 

ut.print_info('\tterm_play()\n\t\tdefault -- meter, continue after default seconds.\n')
ret = Sport(sourceB).term_play() 

ut.print_info('\tplay(\'bars\')\n\t\tmeter, continue after default seconds.\n')
ret = Sport(sourceB).play('bars') 

ut.print_info('\tplay(\'live\')\n\t\tmeter (presumably live since we have ansi), continue after default seconds.\n')
ret = Sport(sourceB).play('live') 

ut.print_info('\tplay()\nmono signal, default -- no meter, continue after default seconds\n')
ret = Sport(monoSource).play()

ut.print_info('\tterm_play()\n\t\tmono signal, default -- meter, continue after default seconds\n')
ret = Sport(monoSource).term_play()

ut.print_info('\tterm_play(\'bars\',0)\n\t\tmono signal, bars meter, should wait for return before continuing\n')
ret = Sport(monoSource).term_play('bars',0)


ut.print_info('FtsTransport rendering....')
ut.print_info('\tplay()\n\t\tno meter, continue after default seconds.\n')
pg.FtsTransport(dst).play()
Sport(pg.WavReaderPE(filename)).play()

ut.print_info('FtsTransport rendering....')
ut.print_info('\tterm_play()\n\t\tdefault --  meter, continue after default seconds.\n')
pg.FtsTransport(dst).play()
Sport(pg.WavReaderPE(filename)).term_play()



ut.use_ansi_when_avaible = prior #restore





