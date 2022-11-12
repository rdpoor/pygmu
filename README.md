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

## Who owns what?

A PygMu "ensmble" is implemented as a Directed Acyclic Graph, with the root
Processing Element as the source of data to be rendered by the transport.

When a PE's render(requested:Extent, n_channels:int) method is called, its
contract is to deliver any sample data that happens within the requested Extent.

The current implementation requires the caller to call the callee's extent()
method first, intersect that with the requested extent, pass the intersected
extent to the callee, and (finally) align the resulting data with the actual
requested data.  This is nuts.

Better would be for the caller to simply pass the requested extent to the
callee and let the callee return what it can.  The problem is that when the
first sample produced by the callee doesn't align with the first sample of
the requested data, there's no way for the caller to know how to align it.

To make it concrete, assume we call:

    callee.render(Extent(100, 200))

... but the callee only has sample data between 150 and 175.  It could allocate
a buffer of 100 elements, overlay its data from buffer[50:75], and return that
to the caller.  But that would lead to a lot of extra allocation.

### Approach A:

A PE could return a Buffer object, which is a thin class that encapsulates a
numpy array and the starting frame of that array.  This will tell the caller
how to align the numpy array in its own internal buffer.

Here's how the transport would handle this case:

        src_data, offset = self.src_pe.render(requested)
        output_data = src_data[offset:]
        # anything not filled by input data needs to be zeroed
        ouput_data[0:offset].fill(0)

### Approach B:

callee.render() return a duple containing the data and the callee's extent:

    (data:np.array, available:Extent)

When the caller receives the data, intersection = requested.intersect(available)
will tell the caller how the data aligns.  In particular, if intersection.start
equals requested.start, then the data aligns at element 0.  If intersection is
empty, then there's no data available from the callee.

Here's how the transport would handle this case:

        src_data, src_extent = self.src_pe.render(requested)
        intersection = requested.intersect(src_extent)
        offset = intersection.start() - requested.start()
        output_data = src_data[offset:]
        # anything not filled by input data needs to be zeroed
        ouput_data[0:offset].fill(0)

### Conclusion:

Approach A is simpler for the caller, Approach B may be simpler for the callee.
Go with Approach A for now.

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
