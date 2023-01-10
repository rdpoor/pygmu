import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

# seq is a little helper function that delays a pe for a given amount
def seq(snippet, at):
    return pg.DelayPE(snippet, at)

# q is the number of frames in a quarter note
q = int(89576 / 4)     # quarter note duration

# s1 ... s4 define four slices out of the original sound file.
s1 = pg.SnippetPE("samples/Fox48.wav", 0*q, pg.Extent(0*q, 1*q))
s2 = pg.SnippetPE("samples/Fox48.wav", 1*q, pg.Extent(1*q, 2*q))
s3 = pg.SnippetPE("samples/Fox48.wav", 2*q, pg.Extent(2*q, 3*q))
s4 = pg.SnippetPE("samples/Fox48.wav", 3*q, pg.Extent(3*q, 4*q))

# snips is a Python dictionary (aka map) that associates a letter (e.g. 'A')
# with a snippet (e.g. s1)
snips = {'A':s1, 'B':s2, 'C':s3, 'D':s4}

# composition is a string of snippet letter names.  We'll iterate over each
# letter in turn...
composition = 'AAAABBBBCDCDDDCD'

# whoo!  This is called a "list comprehension" in Python:
# Deconstructing from the end to the front:
#    enumerate(composition) produces an iterator over that string of letters
#    i, s in enumerate() pulls out sequential indeces and letters, e.g.:
#           0, A
#           1, A
#           2, A
#           3, A
#           4, B
#           ...
#   <function> for i, s in enumerate() calls <function> sequentially with i, s
#   [<function> for i, s in enumerate()] returns a list of values produced by
#       the repeated calls to <function>
# ... so you end up with a list of SnippetPEs.
all_snips = [seq(snips[s], i*q) for i,s in enumerate(composition)]

# See that asterisk?  It means "expand the list" as arguments to MixPE(...)
mix = pg.MixPE(*all_snips)

# And voila...
pg.Transport(mix).play()
