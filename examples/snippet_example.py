import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

def seq(snippet, at):
    return pg.DelayPE(snippet, at)

q = int(89576 / 4)     # quarter note duration

s1 = pg.SnippetPE("samples/Fox48.wav", 0*q, pg.Extent(0*q, 1*q))
s2 = pg.SnippetPE("samples/Fox48.wav", 1*q, pg.Extent(1*q, 2*q))
s3 = pg.SnippetPE("samples/Fox48.wav", 2*q, pg.Extent(2*q, 3*q))
s4 = pg.SnippetPE("samples/Fox48.wav", 3*q, pg.Extent(3*q, 4*q))

# what does what does what does the fox the fox ...
mix = pg.MixPE(
    seq(s1, 0*q),
    seq(s1, 1*q),
    seq(s1, 2*q),
    seq(s1, 3*q),
    seq(s2, 4*q),
    seq(s2, 5*q),
    seq(s2, 6*q),
    seq(s2, 7*q),
    seq(s3, 8*q),
    seq(s4, 9*q),
    seq(s3, 10*q),
    seq(s4, 11*q),
    seq(s4, 12*q),
    seq(s4, 13*q),
    seq(s3, 14*q),
    seq(s4, 15*q))

# Start calling render() on the "root" processing element.
pg.Transport(mix).play()
