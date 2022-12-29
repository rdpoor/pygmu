# pygmu
Python  Generative Music framework

## Installing

Download pipenv unless you already have it

    $ pip install pipenv

Clone the pygmu repository

    $ git clone git@github.com:rdpoor/pygmu.git
    $ cd pygmu
    $ pipenv sync

Start the environment

    $ pipenv shell

Run an example

    $ cd pygmu
    $ python example_01.py

## Running the unit tests
```
    # Windows
    $ py -m pipenv run py -m unittest discover -f -s tests
    # macOS, Linux
    $ pipenv run python -m unittest discover -f -s tests
```
The `-f` means stop on first error.  The `-s` means search in the `tests/` directory for files that start with `test_xxx`

## Profiling
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

## Todo

* Create pyg_exceptions for channel mismatch, frame rate mismatch, perhaps others.
* Flesh out unit tests.
* Add auto-stop feature to Transport to halt on first buffer of all zeros.
* Write up discursis on array shapes, frames, buffers, samplers, monofy, sterofy, reshape(-1,1) et al
 

## To discuss


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

