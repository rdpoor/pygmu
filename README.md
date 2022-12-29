# pygmu

pygmu is a Python Generative Music framework.  It comprises a collection of _processing elements_ that you connect together to create works of music.  Unlike most other frameworks, pygmu does not make a strong distinction between voices and notes: everything is computed at the sampling rate.

## Fundamental concepts

There are three fundamental objects upon which all of pygmu is built:
* **Extent:** An Extent encapsulates a starting time (measured in samples) and an ending time (also measured in samples).
* **Processing Element:**: Each processing element has a constructor, where you specificy parameters, and a `render(extent)` function which, when invoked, asks the processing element to produce sample data between `extent.start()` and `extent.end()`.  
* **frames:** Sample data is passed around as a two-dimensional array, where each column is a channel (e.g. stereo frames will have two columns) and each row is an individual sample (mono, stereo or multi-channel).

## A taste of pygmu

Here is an annotated exmple of a pygmu-based composition that plays Wagner's famous opening
chord to _Tristan und Isolde_:

```
# This bit of boilerplate allows Python to find the pygmu library
import os
import sys
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

def gen_sin(at_s, dur_s, freq_hz, amp):
    """
    Return a Processing Element such that when you call render(), it produces
    a sine tone at the desired time, frequency and amplitude.

    This gen_sin() function is intended to show that it is easy to compose 
    different PEs together to create more complex (or more bespoke) functions.
    """
    # Exploit Python's support of nested functions
    def s_to_f(seconds):
        '''Convert seconds to frames (samples)'''
        # In addition to a render() method, every processing element provides a
        # frame_rate() method that advertises its frame rate.  Here, we use this
        # to convert seconds to frames.
        return int(seconds * sin_pe.frame_rate())

    # Create a sine generator with given frequency and ampltude
    sin_pe = pg.SinPE(frequency = freq_hz, amplitude = amp)
    # Crop the output to to start and end at the desired times.
    return pg.CropPE(sin_pe, pg.Extent(s_to_f(at_s), s_to_f(at_s + dur_s)))

# Generate Wagner's famous opening chord...
# Mix the output of four sinewaves, each with its own frequency and start time.
mix = pg.MixPE(
    gen_sin(0.5, 3.5, ut.pitch_to_freq(53), 0.2),
    gen_sin(1.0, 3.0, ut.pitch_to_freq(59), 0.2),
    gen_sin(1.5, 2.5, ut.pitch_to_freq(63), 0.2),
    gen_sin(2.0, 2.0, ut.pitch_to_freq(68), 0.2))

# Start calling render() on the "mix" processing element to play in real-time
pg.Transport(mix).play()

```

The example above has nine processing elements, connected as shown below.  The important thing to notice is that each processing element is a black box that will produce frames whenever its `render()` method is called.  A graphical representation of the above looks like this:

```
      +---------------+ +---------------+ +---------------+ +---------------+ 
      | sin(174, 0.2) | | sin(246, 0.2) | | sin(311, 0.2) | | sin(415, 0.2) | 
      +-------v-------+ +-------v-------+ +-------v-------+ +-------v-------+ 
              |                 |                 |                 |
      +-------v-------+ +-------v-------+ +-------v-------+ +-------v-------+ 
      | crop(0.5,4.0) | | crop(1.0,4.0) | | crop(1.5,4.0) | | crop(2.0,4.0) | 
      +-------v-------+ +-------v-------+ +-------v-------+ +-------v-------+
              |                 |                 |                 |
      +-------v-----------------v-----------------v-----------------v-------+
      | mix(          ,                  ,                ,                )|
      +----------------------------------v----------------------------------+
                                         |
                                 +-------v-------+ 
                                 |  Transport()  |
                                 +---------------+
```

The `Transport` object is not a processing element itself: it doesn't provide a render() function.  Instead, when its play() method is called, it starts calling render() on the
processing element connected to its input, which in this case is the `mix` processing element.  The `mix` PE in turn calls each of its inputs (the `crop` PEs), which in turn call _their_ inputs, which generate the sine tones.

In computer science terms, a pygmu composition is a _directed acyclic graph_ in which the root node (Transport) "pulls" frames from the rest of the network.

## Install pygmu, run an example

Download `pipenv` unless you already have it:

    $ pip install pipenv

Clone the pygmu repository and ask pipenv to install the required libraries:

    $ git clone git@github.com:rdpoor/pygmu.git
    $ cd pygmu
    $ pipenv sync

Start a shell running the pygmu environment:

    $ pipenv shell

Run an example:

    $ cd pygmu
    $ python examples/sin_example.py

## Developer's Corner

### Running the unit tests
```
    # On Windows
    $ py -m pipenv run py -m unittest discover -f -s tests
    # On macOS, Linux
    $ pipenv run python -m unittest discover -f -s tests
```
The `-f` means stop on first error.  The `-s` means search in the `tests/` directory for files that start with `test_xxx`

### Profiling
Python has built-in profiling tools.  To use it:
* Run the python script with the cProfile module, as shown below
* Run `tools/analyze_profile.py` to find the most CPU hungry functions.
In the example below, you can see that TimeWarpPE and a numpy filter (in the case, CombPE) consume the most time.

```
$ python -m cProfile -o profile.txt examples/piece_RD03.py
0% 1% 2% 3% 4% 5% ... 96% 98% 99% 100% 100%
$ py tools/analyze_profile.py
Reading profile from profile.txt
Sun Dec 18 17:57:06 2022    profile.txt

         3171045 function calls (3118995 primitive calls) in 79.459 seconds

   Ordered by: internal time
   List reduced from 2803 to 10 due to restriction <10>

     ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        184   53.834    0.293   66.429    0.361 C:\Users\r\Projects\pygmu\examples\..\pygmu\timewarp_pe.py:17(render)
       1756   11.388    0.006   11.388    0.006 {built-in method scipy.signal._sigtools._linear_filter}
    1422/92    3.814    0.003   78.143    0.849 C:\Users\r\Projects\pygmu\examples\..\pygmu\mix_pe.py:16(render)
       2953    2.201    0.001    2.243    0.001 C:\Users\r\.virtualenvs\pygmu-oJfXpe_C\lib\site-packages\soundfile.py:1343(_cdata_io)
74034/70404    1.656    0.000    2.429    0.000 {built-in method numpy.core._multiarray_umath.implement_array_function}
       2861    1.486    0.001    4.730    0.002 C:\Users\r\Projects\pygmu\examples\..\pygmu\wav_reader_pe.py:40(render)
 12419/6682    0.709    0.000   73.799    0.011 C:\Users\r\Projects\pygmu\examples\..\pygmu\gain_pe.py:16(render)
       3517    0.633    0.000    0.633    0.000 {method 'reduce' of 'numpy.ufunc' objects}
  5421/3019    0.338    0.000    6.035    0.002 C:\Users\r\Projects\pygmu\examples\..\pygmu\mono_pe.py:15(render)
        607    0.241    0.000    0.241    0.000 {built-in method io.open_code}

```

### Todo

* Create pyg_exceptions for channel mismatch, frame rate mismatch, perhaps others.
* Flesh out unit tests.
* Add auto-stop feature to Transport to halt on first buffer of all zeros.
* Write up discursis on array shapes, frames, buffers, samplers, monofy, sterofy, reshape(-1,1) et al
 

### For future consideration


### Dynamic changes to the graph

At present, the system assumes the graph will be fully built and constant before 
processing starts.  Relaxing this assumption creates lots of possibilities and lots
of potential issues.

### Formalize a connection between two PEs

Should connecting the output of one PE to the input of another go through a 
special object?  This could buy us:
* Automatic channel count fitting
* Detection of circularity
* Ability to notify a PE when connections change

