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

Run the unit tests
```
    $ py -m pipenv run py -m unittest discover -f -s tests
```
The `-f` means stop on first error.  The `-s` means search in the `tests/` directory for files that start with `test_xxx`

## Todo

* Create pyg_exceptions for channel mismatch, frame rate mismatch, perhaps others.
* Flesh out unit tests.
* Create "ASAP" transport that runs as fast as possible, e.g. for writing to a file.
* Add auto-stop feature to Transport to halt on first buffer of all zeros.
* Introduce "constant or PE" as arguments, e.g. to SinPE frequency, amplitude, phase.

## To discuss

### EMPTY_EXTENT

Consider creating a special "EMPTY_EXTENT" object to signify an extent of zero length.

Pro: Might be useful, if only for making code easier to understand.
Con: Any Extent of zero length will behave as expected.

Also, if we do create "EMPTY_EXTENT", shouldn't we then also create "INDEFINITE_EXTENT"?

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

