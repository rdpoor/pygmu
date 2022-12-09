import numpy as np

class Extent(object):
    """
    Extent defines the extent of an event, including events of indefinite
    length.  An extent is implemented as a duple with (start, end)
    where start is inclusive and end is exclusive.  If start
    is NINF or end is PINF, then the extent is said to be of indefinite
    duration.  Otherwise the duration is simply end - start.

    The advantage of using PINF over using some special symbol is that
    PINF + x == PINF, which simplifies calculations.  (Ditto for NINF.)
    """

    NINF = np.finfo('float').min
    PINF = np.finfo('float').max
    INDEFINITE_DURATION = np.inf
    INFINITE_EXTENT = (NINF, PINF)
    NULL_EXTENT = (0, 0)

    def __init__(self, start = NINF, end = PINF):
        self.s = start
        self.e = max(end, start)

    def __repr__(self):
        st = str(self.s)
        et = str(self.e)
        if self.s == self.NINF:
            st = "NINF"
        if self.e == self.PINF:
            et = "PINF"
        return f"""<Extent {self.__hash__()}: s={st}, e={et}>"""

    # ================================================================
    # operations on a single extent

    def start(self):
        return self.s

    def end(self):
        return self.e

    def is_indefinite(self):
        return self.s == self.NINF or self.e == self.PINF

    def is_empty(self):
        return self.s == self.e

    def duration(self):
        if self.is_indefinite():
            return self.INDEFINITE_DURATION
        else:
            return self.e - self.s

    def offset(self, delay):
        return Extent(self.s + delay, self.e + delay)

    # ================================================================
    # logical operations on an extent

    def precedes(self, other):
        """
        Returns True if self strictly precedes other.  other may be a scalar or
        another Extent.
        """
        if isinstance(other, Extent):
            return self.e <= other.s
        else:
            return self.e <= other

    def follows(self, other):
        """
        Returns True if self strictly follows other.  other may be a scalar or
        another Extent.
        """
        if isinstance(other, Extent):
            return other.e <= self.s
        else:
            # subtlety: other must be strictly less than self starting time.
            return other < self.s

    def overlaps(self, other):
        """
        Returns True if any part of self overlaps other.
        """
        if isinstance(other, Extent):
            return not ((self.e <= other.s) or (other.e <= self.s))
        else:
            return self.s <= other and other < self.e

    def spans(self, other):
        """
        Returns True if self completely encompases other.
        """
        if isinstance(other, Extent):
            return self.s <= other.s and self.e >= other.e
        else:
            return self.s <= other and other < self.e

    def equals(self, other):
        """
        Returns true if self and other refer to the same extent.
        """
        if isinstance(other, Extent):
            return self.s == other.s and self.e == other.e
        else:
            # can equal a scalar iff self has zero duration.
            return self.s == other and self.e == other

    # ================================================================
    # operations on two extents

    #  TODO: should accept a list of other Extents

    def union(self, other):
        """
        returns a new Extent whose start time is the earlier of a and b and
        whose end time is the later of a and b
        """
        return Extent(min(self.s, other.s), max(self.e, other.e))

    def intersect(self, other):
        """
        If self intersects other, return a new Extent with that intersection,
        else return None
        """
        s = max(self.s, other.s)
        e = min(self.e, other.e)
        if (s <= e):
            return Extent(s, e)
        else:
            return Extent(0, 0)
