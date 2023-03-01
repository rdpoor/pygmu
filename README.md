# pygmu

pygmu is a Python Generative Music framework.  It comprises a collection of _processing elements_ that you connect together to create works of music.  Unlike most other frameworks, pygmu does not make a strong distinction between voices and notes: everything is computed at the sampling rate.

pygmu is designed more for composers than for performers -- unlike GarageBand or Ableton Live, PygMu is unapologetically NOT real time: you think about the results you want, you type in some code, you drink some coffee and contemplate your actions while it renders, then you listen to it.  It invites a slower, more deliberate approach to creating music.

## Fundamental concepts

There are three fundamental objects upon which all of pygmu is built:
* **Extent:** An Extent encapsulates a starting time (measured in samples) and an ending time (also measured in samples).
* **Processing Element:**: Each processing element has a constructor, where you specificy parameters, and a `render(extent)` function which, when invoked, asks the processing element to produce sample data between `extent.start()` and `extent.end()`.  
* **frames:** Sample data is passed around as a two-dimensional array, where each row is a channel (e.g. stereo frames will have two rows) and each columm is an individual sample (mono, stereo or multi-channel).

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

SRATE = 48000  # Define the frame rate for the piece.

def s_to_f(seconds):
    '''Convert seconds to frames (samples)'''
    return int(seconds * SRATE)

def generate_note(start_time, duration, hz, amp):
    """
    Return a Processing Element such that when you call render(), it produces
    a tone at the desired time with a given duration, frequency and amplitude.
    """
    # Use an Extent to define the start and end times of the note
    extent = pg.Extent(s_to_f(start_time), s_to_f(start_time + duration))

    # We use a BlitSaw (bandwidth limited sawtooth wave generator) to generate 
    # the tone, passing its output through a gain stage to adjust the amplitude 
    # and then through a "CropPE" to specify the start and end times.

    # We could chain together the processing elements like this...
    # saw_pe = pg.BlitSawPE(frequency=hz, frame_rate=SRATE)
    # saw_pe = pg.GainPE(saw_pe, amp)          # Adjust the amplitude
    # saw_pe = pg.CropPE(saw_pe, extent)       # Crop start and end times
    # return saw_pe                            # Return the result

    # ... but PygMu provides shorthand chaining methods for many common
    # functions, so you can write the whole thing in one line if you prefer:
    return pg.BlitSawPE(frequency=hz, frame_rate=SRATE).gain(amp).crop(extent)

# Mix the output of four tones to Generate Wagner's famous opening chord.
# Note that we use the `utils` module's `pitch_to_freq()` functon to convert
# MIDI style pitch numbers to frequencies.  
tristan = pg.MixPE(
    generate_note(0.5, 4.5, ut.pitch_to_freq(53), 0.2),
    generate_note(1.0, 4.0, ut.pitch_to_freq(59), 0.2),
    generate_note(1.5, 3.5, ut.pitch_to_freq(63), 0.2),
    generate_note(2.0, 3.0, ut.pitch_to_freq(68), 0.2))

# At this point, we have defined HOW the final piece will be generated, but it 
# hasn't been generated yet.  The Transport `play()` method will repeatedly call
# `tristan.render()` to request samples, sending the result to the DAC on your
# computer.
pg.Transport(tristan).play()
```

The example above has eleven processing elements, connected as shown below.  The 
important thing to notice is that each processing element is a black box that 
will produce frames whenever its `render()` method is called.  A graphical 
representation of the above looks like this:

```
      +---------------+ +---------------+ +---------------+ +---------------+ 
      | saw(174, 0.2) | | saw(246, 0.2) | | saw(311, 0.2) | | saw(415, 0.2) | 
      +-------v-------+ +-------v-------+ +-------v-------+ +-------v-------+ 
              |                 |                 |                 |
      +-------v-------+ +-------v-------+ +-------v-------+ +-------v-------+ 
      |   amp(0.2)    | |   amp(0.2)    | |   amp(0.2)    | |   amp(0.2)    | 
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

The `Transport` object is not a processing element itself: it doesn't provide a 
render() function.  Instead, when its play() method is called, it starts calling 
render() on the processing element connected to its input, which in this case is 
the `mix` processing element.  The `mix` PE in turn calls each of its inputs 
(the `crop` PEs), which in turn call _their_ inputs and so on, to generate the 
tones.

In computer science terms, a pygmu composition is a _directed acyclic graph_ in 
which the root node (Transport) "pulls" frames from the rest of the network.

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

### Keeping it real

The file API.md documents pygmu's functions.  To be official, each function:
1. Must be documented in API.md
2. Must have a corresponding test in tests/
3. Must have an appropirate import line in pygmu/pygmu.py

### Running the unit tests
If you haven't launched the pygmu shell:
```
    # On Windows
    $ py -m pipenv run py -m unittest discover -f -s tests
    # On macOS, Linux
    $ pipenv run python -m unittest discover -f -s tests
```
If you are already running the pygmu shell:
```
    # On Windows
    $ py -m unittest discover -f -s tests
    # On macOS, Linux
    $ python -m unittest discover -f -s tests
```
The `-f` means stop on first error.  The `-s` means search in the `tests/` directory for files that start with `test_xxx`

You can also test an individual file like this:
```
    $ python -m unittest tests/test_something.py
```
You can even run a single function within a test file like this:
```
# On Windows:
$ py -m unittest tests.test_rate_warp_pe.TestRateWarpPE.test_render_p0r0_f0
# On macOS, Linux:
$ python -m unittest tests.test_rate_warp_pe.TestRateWarpPE.test_render_p0r0_f0
```
### Coverage Tests

After you have the unit tests running, hre are the commands that will make sure you've got good testing coverage.
When you open the .html file, click on an individual file listed there.  Lines highlighted in red indicate that 
they did not get run, and is a strong indicator that your unit tests need to excercise and test those lines.

#### On Windows:

```
$ py -m coverage run -m unittest discover -f -s tests
......................................................................
----------------------------------------------------------------------
Ran 152 tests in 0.038s
OK

$ py -m coverage html
Wrote HTML report to htmlcov\index.html

$ start htmlcov/index.html

# Or all at once:

py -m coverage run -m unittest discover -f -s tests && py -m coverage html ; start htmlcov/index.html
```

#### On macOS:

(Typed from memory -- please correct if needed)

```
$ python -m coverage run -m unittest discover -f -s tests
......................................................................
----------------------------------------------------------------------
Ran 152 tests in 0.038s
OK

$ python -m coverage html
Wrote HTML report to htmlcov\index.html

$ open htmlcov/index.html
```


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

### All about `frames`

In pygmu, buffers of sample data are exchanged using `frames`, which are implemented using 
two-dimensional [numpy arrrays](https://numpy.org/doc/stable/reference/generated/numpy.array.html) of 32 bit floating point values.  Every call to `pe.render()` will return a frames object.

`numpy` provides a truly dazziling assortment of functions that operate on arrays.  Here are some of the more common ones you might encounter as a pygmu developer.


A buffer of single-channel (mono) data is represented as a 2-D array with one row:
```
>>> a1 = np.array([np.arange(100, 105)], dtype=np.float32)
array([[100., 101., 102., 103., 104.]], dtype=float32)
```

As a convenience, a mono channel can also be represented by a 1-D array of samples:
```
>>> a2 = np.arange(200, 205, dtype=np.float32)
array([200., 201., 202., 203., 204.], dtype=float32) 
```

Stereo frames have two rows, where row 0 is understood to be the left channel:
```
>>> b = np.array([np.arange(100, 105), np.arange(200, 205)], dtype=np.float32)
array([[100., 101., 102., 103., 104.],                          
       [200., 201., 202., 203., 204.]], dtype=float32) 
```
You can use `np.vstack()` to convert a mono buffer into stereo without changing gain.  Note that you can use 1-D or 2-D arrays:
```
>>> np.vstack((a1, a1))
array([[100., 101., 102., 103., 104.],
       [100., 101., 102., 103., 104.]], dtype=float32)
>>> np.vstack((a2, a2))
array([[100., 101., 102., 103., 104.],
       [100., 101., 102., 103., 104.]], dtype=float32)
```
You can also use `np.vstack()` to "glue" two independent mono tracks into stereo, assuming they have the same length:
```
>>> a3=np.arange(300, 305, dtype=np.float32)
>>> np.vstack((a2, a3))
array([[200., 201., 202., 203., 204.],
       [300., 301., 302., 303., 304.]], dtype=float32)
```
You can use 'slicing' to extract the left or right channel from stereo frames:
```
>>> b[0,:]
array([100., 101., 102., 103., 104.], dtype=float32)
>>> b[1,:]
array([200., 201., 202., 203., 204.], dtype=float32)
```
You can think of that as "get all of row 0 from b" and "get all of row 1 from b" respectively.  The general syntax for slicing is:

    <array>[<row indexes>,<column indexes>]

If \<column indeces\> has the form `j:k`, that's interpreted as starting at column j (inclusive) and ending at column k (exclusive).  If j is omitted, it is interpreted as 0.  If k is omitted, it is interpreted as the end of the column.  And if either j or k are negative, they index from the end of the row.  So:

```
>>> b[:, 1:3]
array([[101., 102.],
       [201., 202.]], dtype=float32)
>>> b[:,-4:3]           # -4 is equivalent to 2
array([[101., 102.],
       [201., 202.]], dtype=float32)

``` 

numpy arrays support scalar operations which are "broadcast" over all the elements.  Therefore:
```
>>> a1 + 0.123
array([[100.123, 101.123, 102.123, 103.123, 104.123]], dtype=float32)
```
Slices can almost always appear on the left hand side of an assignment.  If you wanted to modify the left channel of a frames object:
```
>>> b[0:1,] = a3
>>> b
array([[300., 301., 302., 303., 304.],
       [200., 201., 202., 203., 204.]], dtype=float32)
```
The `T` operator will transpose a column array into a row array and vice versa:
```
>>> b.T
array([[300., 200.],
       [301., 201.],
       [302., 202.],
       [303., 203.],
       [304., 204.]], dtype=float32)
>>> b.T.T
array([[300., 301., 302., 303., 304.],
       [200., 201., 202., 203., 204.]], dtype=float32)
```

#### Of frame_count and channel_count

A numpy array has a `shape` property, so:

```
>>> b.shape
(2, 5)
```

This tells us that `b` has two channels and is five frames long.

#### The ubiquitous `reshape()` function

If you delve into pygmu code, you'll see frequent use of the `reshape()` 
function.  Here's how it works.

Assume that you have a numpy array of 12 elements:
```
>>> a = np.arange(12, dtype=np.float32)
>>> a 
array([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10., 11.], dtype=float32)   
```

The `reshape()` function lets you reshape an array to a given number of rows
and columns, as long as rows * columns equals the length of the array.  The
simplified form is `<array>.reshape(n_rows, n_columns)`:

```
>>> a.reshape(3, 4)
array([[ 0.,  1.,  2.,  3.],
       [ 4.,  5.,  6.,  7.],
       [ 8.,  9., 10., 11.]], dtype=float32)
>>> a.reshape(6, 2)
array([[ 0.,  1.],
       [ 2.,  3.],
       [ 4.,  5.],
       [ 6.,  7.],
       [ 8.,  9.],
       [10., 11.]], dtype=float32)
```
Note that the following two calls produce different results.  The first results
in a 1-D array of 12 elements, the second a 2-D array with one row and 12 
columns:
```
>>> a.reshape(12)
array([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10., 11.], dtype=float32)
>>> a.reshape(1, 12)
array([[ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10., 11.]], dtype=float32)
```
As a convenience, `reshape()` lets you specify -1 as one of the arguments.  It
will infer what that should be based on the other argument and the length of the
underlying array:
```
>>> a.reshape(1, -1)
array([[ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10., 11.]], dtype=float32)
>>> a.reshape(2, -1)
array([[ 0.,  1.,  2.,  3.,  4.,  5.],
       [ 6.,  7.,  8.,  9., 10., 11.]], dtype=float32)
>>> a.reshape(3, -1)
array([[ 0.,  1.,  2.,  3.],
       [ 4.,  5.,  6.,  7.],
       [ 8.,  9., 10., 11.]], dtype=float32)
```

### Utilities

Command to print out info about all the soundfiles in the current directory 
(must have sox installed):

    Windows:    find . -name "*.wav" -print0 | xargs -0 sox.exe --i
    OSX/Linux:  find . -name "*.wav" -print0 | xargs -0 sox --i


### Todo

* [done] Create pyg_exceptions for channel mismatch, frame rate mismatch, perhaps others.
* [never entirely done] Flesh out unit tests.
* [done] add explanation of reshape(-1,1) to All about frames section
* [done] TimewarpPE needs help.  see examples/example_09.py.  enfoce single-channel timeline
* BiQuadPE needs help.  see examples/example_11.py
* FilterPE needs help.  see examples/filter_example.py
* examples/piece_RA01_v1.py needs help: MixPE trying to mix mono and stereo for some seeds
* [done] Create user-supplied f(x) processing element: output = user_function(input).  (Create `MapPE`)
* [done] Rethink EnvDetectPE, CompLimPE, CompressorPE, LimiterAPE, LimiterPE.  (Create `MapPE`,
give `EnvDetectPE` and `GainPE` a `units='db'` optional parameter.)
* In `EnvDetectPE`, optionally support time constants (seconds) for attack and relase rather than 0.99 meaning "fast" and 0.01 meaning "slow".
* Incorporate tkintr

### Installing tkintr

Here's the WIP formula for getting tkinter up and running on macOS:

pipenv install Tk inter
brew install python-tk@3.10


### Ponders

* Should compressors / limiters accept multi-channel envelope data?
* If a PE takes multple inputs, and inputs have different frame rates, should it: (1) raise an error, (2) print a warning, (3) silently accept the frame rate of the first input?  For now, we're implementing (1) (raise an error).  We could create a pass-through PE that discards frame rate as a universal adaptor.

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

