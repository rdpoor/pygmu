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

## Todo

There are lots of loose ends. The system is currently ambiguous as to who "owns"
`frame_rate` and `n_channels`?  Best would be to have the Transport object offer
`pg.Transport.frame_rate()` and `pg.Transport.n_channels()` so any modules that
need to know could find out.

Need to create functions to map n channels into m channels.

Can frame indeces be non-integer?  If not, who is responsible for enforcing
that?  Should all Extent() objects enforce it?

I don't understand packages well enough to know how to put the
example_01.py into the example directory.

### Extent

Rather than using None to signify "the null extent", it might be useful to have
a special instance of Extent to represent it.  If that's the case:

    NULL_EXTENT.intersects(x) => NULL_EXTENT
    NULL_EXTENT.union(x) => x
    any event precedes (or follows) the null extent
    only the null extent equals the null extent

Perhaps implement NullExtent as a subclass of Extent and tweak the methods
accordingly.  And if we go that route, why not the same treatment for
InfiniteExtent?
