import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import random
import utils as ut
import tempfile


prior = ut.use_ansi_when_avaible

ut.use_ansi_when_avaible = False

ut.print_info('ansi status:',ut.terminal_has_ansi_support(),ut.use_ansi_when_avaible,'\n')


sourceA= pg.WavReaderPE("samples/ItsGonnaRain_Original.wav").gain(7)
sourceB= pg.WavReaderPE("samples/BigBeat120bpm10.wav").gain(2)
monoSource= pg.WavReaderPE("samples/Sine_C4.wav") 

filename = tempfile.gettempdir()+'/transport.wav'
dst = pg.WavWriterPE(sourceA, filename)


ut.print_info('no meter, should continue when finished')
ret = pg.Transport(sourceB).term_play(False) #no meter, should continue when finished
ut.print_info('done.\n')
ut.print_info('meter, should continue when finished')
ret = pg.Transport(sourceB).term_play(True) #meter, should continue when finished
ut.print_info('done.\n')
ut.print_info('mono, no meter, should continue when finished')
ret = pg.Transport(monoSource).play() # mono no meter, should auto continue
ut.print_info('done.\n')
ut.print_info('mono meter, should continue when finished')
ret = pg.Transport(monoSource).play(True) # mono meter, should auto continue
ut.print_info('done.\n')

ut.print_info('rendering....')
pg.FtsTransport(dst).play()
ut.print_info('no meter, should auto continue')
pg.Transport(pg.WavReaderPE(filename)).play()
ut.print_info('done.')
ut.print_info('meter, should auto continue')
pg.Transport(pg.WavReaderPE(filename)).play(True)
ut.print_info('done...')

ut.use_ansi_when_avaible = True

if not ut.terminal_has_ansi_support():
    ut.print_info('No ansi on this terminal, test finished.')
    exit('')


ut.print_warn('Turning ansi on.\n')


ut.print_info('no meter, should continue when finished')
ret = pg.Transport(sourceB).term_play(False) #no meter, should continue when finished
ut.print_info('done.')
ut.print_info('meter, should continue when finished')
ret = pg.Transport(sourceB).term_play(True) #meter, should continue when finished
ut.print_info('done.')
ut.print_info('mono, no meter, should continue when finished')
ret = pg.Transport(monoSource).play() # mono no meter, should auto continue
ut.print_info('done.')
ut.print_info('mono meter, should continue when finished')
ret = pg.Transport(monoSource).play(True) # mono meter, should auto continue
ut.print_info('done.')

ut.print_info('rendering....')
pg.FtsTransport(dst).play()
ut.print_info('no meter, should auto continue')
pg.Transport(pg.WavReaderPE(filename)).play()
ut.print_info('done.')
ut.print_info('meter, should auto continue')
pg.Transport(pg.WavReaderPE(filename)).play(True)
ut.print_info('done.')




ut.use_ansi_when_avaible = prior #restore





