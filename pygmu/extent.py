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
        self.e = end

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

import unittest
import math

class TestExtent(unittest.TestCase):

    def test_constructors(self):
        a0 = Extent()
        a1 = Extent(start=10)
        a2 = Extent(end=100)
        a3 = Extent(start=10, end=100)
        self.assertEqual(a0.start(), Extent.NINF)
        self.assertEqual(a0.end(), Extent.PINF)
        self.assertEqual(a1.start(), 10)
        self.assertEqual(a1.end(), Extent.PINF)
        self.assertEqual(a2.start(), Extent.NINF)
        self.assertEqual(a2.end(), 100)
        self.assertEqual(a3.start(), 10)
        self.assertEqual(a3.end(), 100)

    def test_is_indefinite(self):
        a0 = Extent()
        a1 = Extent(start=10)
        a2 = Extent(end=100)
        a3 = Extent(start=10, end=100)
        self.assertTrue(a0.is_indefinite())
        self.assertTrue(a1.is_indefinite())
        self.assertTrue(a2.is_indefinite())
        self.assertFalse(a3.is_indefinite())

    def test_duration(self):
        a0 = Extent()
        a1 = Extent(start=10)
        a2 = Extent(end=100)
        a3 = Extent(start=10, end=100)
        self.assertTrue(math.isinf(a0.duration()))
        self.assertTrue(math.isinf(a1.duration()))
        self.assertTrue(math.isinf(a2.duration()))
        self.assertEqual(a3.duration(), 90)

    def test_offset(self):
        a0 = Extent().offset(20)
        a1 = Extent(start=10).offset(20)
        a2 = Extent(end=100).offset(20)
        a3 = Extent(start=10, end=100).offset(20)
        self.assertEqual(a0.start(), Extent.NINF)
        self.assertEqual(a0.end(), Extent.PINF)
        self.assertEqual(a1.start(), 30)
        self.assertEqual(a1.end(), Extent.PINF)
        self.assertEqual(a2.start(), Extent.NINF)
        self.assertEqual(a2.end(), 120)
        self.assertEqual(a3.start(), 30)
        self.assertEqual(a3.end(), 120)

    def test_precedes(self):
        a0 = Extent(end=10)
        a1 = Extent(start=0, end=20)
        a2 = Extent(start=10, end=30)
        a3 = Extent(start=20, end=40)
        a4 = Extent(start=30)
        self.assertFalse(a0.precedes(a0))
        self.assertFalse(a0.precedes(a1))
        self.assertTrue(a0.precedes(a2))
        self.assertTrue(a0.precedes(a3))
        self.assertTrue(a0.precedes(a4))

        self.assertFalse(a1.precedes(a0))
        self.assertFalse(a1.precedes(a1))
        self.assertFalse(a1.precedes(a2))
        self.assertTrue(a1.precedes(a3))
        self.assertTrue(a1.precedes(a4))

        self.assertFalse(a2.precedes(a0))
        self.assertFalse(a2.precedes(a1))
        self.assertFalse(a2.precedes(a2))
        self.assertFalse(a2.precedes(a3))
        self.assertTrue(a2.precedes(a4))

        self.assertFalse(a3.precedes(a0))
        self.assertFalse(a3.precedes(a1))
        self.assertFalse(a3.precedes(a2))
        self.assertFalse(a3.precedes(a3))
        self.assertFalse(a3.precedes(a4))

        self.assertFalse(a4.precedes(a0))
        self.assertFalse(a4.precedes(a1))
        self.assertFalse(a4.precedes(a2))
        self.assertFalse(a4.precedes(a3))
        self.assertFalse(a4.precedes(a4))

        self.assertFalse(a0.precedes(0))
        self.assertTrue(a0.precedes(10))
        self.assertTrue(a0.precedes(20))
        self.assertTrue(a0.precedes(30))
        self.assertTrue(a0.precedes(40))

        self.assertFalse(a1.precedes(0))
        self.assertFalse(a1.precedes(10))
        self.assertTrue(a1.precedes(20))
        self.assertTrue(a1.precedes(30))
        self.assertTrue(a1.precedes(40))

        self.assertFalse(a2.precedes(0))
        self.assertFalse(a2.precedes(10))
        self.assertFalse(a2.precedes(20))
        self.assertTrue(a2.precedes(30))
        self.assertTrue(a2.precedes(40))

        self.assertFalse(a3.precedes(0))
        self.assertFalse(a3.precedes(10))
        self.assertFalse(a3.precedes(20))
        self.assertFalse(a3.precedes(30))
        self.assertTrue(a3.precedes(40))

        self.assertFalse(a4.precedes(0))
        self.assertFalse(a4.precedes(10))
        self.assertFalse(a4.precedes(20))
        self.assertFalse(a4.precedes(30))
        self.assertFalse(a4.precedes(40))

    def test_follows(self):
        a0 = Extent(end=10)
        a1 = Extent(start=0, end=20)
        a2 = Extent(start=10, end=30)
        a3 = Extent(start=20, end=40)
        a4 = Extent(start=30)
        self.assertFalse(a0.follows(a0))
        self.assertFalse(a0.follows(a1))
        self.assertFalse(a0.follows(a2))
        self.assertFalse(a0.follows(a3))
        self.assertFalse(a0.follows(a4))

        self.assertFalse(a1.follows(a0))
        self.assertFalse(a1.follows(a1))
        self.assertFalse(a1.follows(a2))
        self.assertFalse(a1.follows(a3))
        self.assertFalse(a1.follows(a4))

        self.assertTrue(a2.follows(a0))
        self.assertFalse(a2.follows(a1))
        self.assertFalse(a2.follows(a2))
        self.assertFalse(a2.follows(a3))
        self.assertFalse(a2.follows(a4))

        self.assertTrue(a3.follows(a0))
        self.assertTrue(a3.follows(a1))
        self.assertFalse(a3.follows(a2))
        self.assertFalse(a3.follows(a3))
        self.assertFalse(a3.follows(a4))

        self.assertTrue(a4.follows(a0))
        self.assertTrue(a4.follows(a1))
        self.assertTrue(a4.follows(a2))
        self.assertFalse(a4.follows(a3))
        self.assertFalse(a4.follows(a4))

        self.assertFalse(a0.follows(0))
        self.assertFalse(a0.follows(10))
        self.assertFalse(a0.follows(20))
        self.assertFalse(a0.follows(30))
        self.assertFalse(a0.follows(40))

        self.assertFalse(a1.follows(0))
        self.assertFalse(a1.follows(10))
        self.assertFalse(a1.follows(20))
        self.assertFalse(a1.follows(30))
        self.assertFalse(a1.follows(40))

        self.assertTrue(a2.follows(0))
        self.assertFalse(a2.follows(10))
        self.assertFalse(a2.follows(20))
        self.assertFalse(a2.follows(30))
        self.assertFalse(a2.follows(40))

        self.assertTrue(a3.follows(0))
        self.assertTrue(a3.follows(10))
        self.assertFalse(a3.follows(20))
        self.assertFalse(a3.follows(30))
        self.assertFalse(a3.follows(40))

        self.assertTrue(a4.follows(0))
        self.assertTrue(a4.follows(10))
        self.assertTrue(a4.follows(20))
        self.assertFalse(a4.follows(30))
        self.assertFalse(a4.follows(40))

    def test_overlaps(self):
        a0 = Extent(end=10)
        a1 = Extent(start=0, end=20)
        a2 = Extent(start=10, end=30)
        a3 = Extent(start=20, end=40)
        a4 = Extent(start=30)
        self.assertTrue(a0.overlaps(a0))
        self.assertTrue(a0.overlaps(a1))
        self.assertFalse(a0.overlaps(a2))
        self.assertFalse(a0.overlaps(a3))
        self.assertFalse(a0.overlaps(a4))

        self.assertTrue(a1.overlaps(a0))
        self.assertTrue(a1.overlaps(a1))
        self.assertTrue(a1.overlaps(a2))
        self.assertFalse(a1.overlaps(a3))
        self.assertFalse(a1.overlaps(a4))

        self.assertFalse(a2.overlaps(a0))
        self.assertTrue(a2.overlaps(a1))
        self.assertTrue(a2.overlaps(a2))
        self.assertTrue(a2.overlaps(a3))
        self.assertFalse(a2.overlaps(a4))

        self.assertFalse(a3.overlaps(a0))
        self.assertFalse(a3.overlaps(a1))
        self.assertTrue(a3.overlaps(a2))
        self.assertTrue(a3.overlaps(a3))
        self.assertTrue(a3.overlaps(a4))

        self.assertFalse(a4.overlaps(a0))
        self.assertFalse(a4.overlaps(a1))
        self.assertFalse(a4.overlaps(a2))
        self.assertTrue(a4.overlaps(a3))
        self.assertTrue(a4.overlaps(a4))

        self.assertTrue(a0.overlaps(0))
        self.assertFalse(a0.overlaps(10))
        self.assertFalse(a0.overlaps(20))
        self.assertFalse(a0.overlaps(30))
        self.assertFalse(a0.overlaps(40))

        self.assertTrue(a1.overlaps(0))
        self.assertTrue(a1.overlaps(10))
        self.assertFalse(a1.overlaps(20))
        self.assertFalse(a1.overlaps(30))
        self.assertFalse(a1.overlaps(40))

        self.assertFalse(a2.overlaps(0))
        self.assertTrue(a2.overlaps(10))
        self.assertTrue(a2.overlaps(20))
        self.assertFalse(a2.overlaps(30))
        self.assertFalse(a2.overlaps(40))

        self.assertFalse(a3.overlaps(0))
        self.assertFalse(a3.overlaps(10))
        self.assertTrue(a3.overlaps(20))
        self.assertTrue(a3.overlaps(30))
        self.assertFalse(a3.overlaps(40))

        self.assertFalse(a4.overlaps(0))
        self.assertFalse(a4.overlaps(10))
        self.assertFalse(a4.overlaps(20))
        self.assertTrue(a4.overlaps(30))
        self.assertTrue(a4.overlaps(40))

    def test_spans(self):
        a0 = Extent()
        a1 = Extent(start=10, end=40)
        a2 = Extent(start=0, end=20)
        a3 = Extent(start=20, end=30)

        self.assertTrue(a0.spans(a0))
        self.assertTrue(a0.spans(a1))
        self.assertTrue(a0.spans(a2))
        self.assertTrue(a0.spans(a3))

        self.assertFalse(a1.spans(a0))
        self.assertTrue(a1.spans(a1))
        self.assertFalse(a1.spans(a2))
        self.assertTrue(a1.spans(a3))

        self.assertFalse(a2.spans(a0))
        self.assertFalse(a2.spans(a1))
        self.assertTrue(a2.spans(a2))
        self.assertFalse(a2.spans(a3))

        self.assertFalse(a3.spans(a0))
        self.assertFalse(a3.spans(a1))
        self.assertFalse(a3.spans(a2))
        self.assertTrue(a3.spans(a3))

        self.assertTrue(a0.spans(0))
        self.assertTrue(a0.spans(10))
        self.assertTrue(a0.spans(20))
        self.assertTrue(a0.spans(30))
        self.assertTrue(a0.spans(40))

        self.assertFalse(a1.spans(0))
        self.assertTrue(a1.spans(10))
        self.assertTrue(a1.spans(20))
        self.assertTrue(a1.spans(30))
        self.assertFalse(a1.spans(40))

        self.assertTrue(a2.spans(0))
        self.assertTrue(a2.spans(10))
        self.assertFalse(a2.spans(20))
        self.assertFalse(a2.spans(30))
        self.assertFalse(a2.spans(40))

        self.assertFalse(a3.spans(0))
        self.assertFalse(a3.spans(10))
        self.assertTrue(a3.spans(20))
        self.assertFalse(a3.spans(30))
        self.assertFalse(a3.spans(40))

    def test_union(self):
        a0 = Extent()
        a1 = Extent(start=0, end=10)
        a2 = Extent(start=20, end=30)

        self.assertTrue(a0.equals(a0.union(a0)))
        self.assertTrue(a0.equals(a0.union(a1)))
        self.assertTrue(a0.equals(a0.union(a2)))

        self.assertTrue(a0.equals(a1.union(a0)))
        self.assertTrue(a1.equals(a1.union(a1)))
        self.assertTrue(Extent(start=0, end=30).equals(a1.union(a2)))

        self.assertTrue(a0.equals(a2.union(a0)))
        self.assertTrue(Extent(start=0, end=30).equals(a2.union(a1)))
        self.assertTrue(a2.equals(a2.union(a2)))

    def test_intersect(self):
        a0 = Extent()
        a1 = Extent(start=0, end=10)
        a2 = Extent(start=20, end=30)

        self.assertTrue(a0.equals(a0.intersect(a0)))
        self.assertTrue(a1.equals(a0.intersect(a1)))
        self.assertTrue(a2.equals(a0.intersect(a2)))

        self.assertTrue(a1.equals(a1.intersect(a0)))
        self.assertTrue(a1.equals(a1.intersect(a1)))
        self.assertIsNone(a1.intersect(a2))

        self.assertTrue(a2.equals(a2.intersect(a0)))
        self.assertIsNone(a2.intersect(a1))
        self.assertTrue(a2.equals(a2.intersect(a2)))

if __name__ == '__main__':
        unittest.main()
