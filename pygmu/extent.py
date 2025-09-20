import numpy as np
import math
from typing import Union, Optional, List, Iterable

class Extent(object):
    """
    Represents a temporal extent with support for indefinite durations.

    An extent is defined by (start, end) where start is inclusive and end is exclusive.
    If start is NINF or end is PINF, the extent is of indefinite duration.
    Otherwise, duration is end - start.

    Using math.inf allows natural arithmetic: PINF + x == PINF, NINF + x == NINF.
    """

    NINF = -math.inf
    PINF = math.inf
    INDEFINITE_DURATION = math.inf

    def __init__(self, start: float = NINF, end: float = PINF, duration: Optional[float] = None):
        """
        Initialize an Extent.

        Args:
            start: Start time (inclusive). Defaults to NINF.
            end: End time (exclusive). Defaults to PINF.
            duration: If provided, used to calculate missing start or end.
                     Conflicts with provided start/end values raise ValueError.

        Raises:
            TypeError: If start, end, or duration are not numeric
            ValueError: If end < start or duration conflicts with start/end
        """
        # Type checking
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise TypeError("Start and end must be numeric")
        if duration is not None and not isinstance(duration, (int, float)):
            raise TypeError("Duration must be None or numeric")

        # Duration handling
        if duration is not None:
            if duration < 0:
                raise ValueError("Duration cannot be negative")
            if start == self.NINF and end == self.PINF:
                raise ValueError("Cannot set duration when both start and end are infinite")
            elif start == self.NINF:
                # Start not given: use end - duration
                start = end - duration
            elif end == self.PINF:
                # End not given: use start + duration
                end = start + duration
            else:
                # Both finite: validate consistency
                if abs((end - start) - duration) > 1e-10:
                    raise ValueError(f"Duration {duration} conflicts with start/end range {end - start}")

        # Validation
        if end < start:
            raise ValueError(f"End ({end}) cannot be before start ({start})")

        self.s, self.e = start, end

    def __str__(self) -> str:
        """Return human-readable string representation."""
        start_str = "NINF" if self.s == self.NINF else str(self.s)
        end_str = "PINF" if self.e == self.PINF else str(self.e)
        return f"[{start_str}, {end_str})"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        st = "NINF" if self.s == self.NINF else str(self.s)
        et = "PINF" if self.e == self.PINF else str(self.e)
        return f"<Extent {self.__hash__()}: s={st}, e={et}>"

    def __eq__(self, other):
        """Return True if extents have the same start and end."""
        if not isinstance(other, Extent):
            return NotImplemented
        return self.s == other.s and self.e == other.e

    def __hash__(self) -> int:
        """Return hash based on start and end values."""
        return hash((self.s, self.e))

    # ================================================================
    # operations on a single extent

    def start(self) -> float:
        """Return the start time (inclusive)."""
        return self.s

    def end(self) -> float:
        """Return the end time (exclusive)."""
        return self.e

    def is_indefinite(self) -> bool:
        """Return True if the extent has indefinite duration."""
        return self.s == self.NINF or self.e == self.PINF

    def is_empty(self) -> bool:
        """Return True if the extent is empty (zero duration)."""
        return self.s >= self.e

    def duration(self) -> float:
        """Return the duration of the extent, or INDEFINITE_DURATION if indefinite."""
        if self.is_indefinite():
            return self.INDEFINITE_DURATION
        elif self.is_empty():
            return 0.0
        else:
            return self.e - self.s

    def offset(self, delay: float) -> 'Extent':
        """
        Return a new Extent offset by the specified delay.

        Args:
            delay: Time offset to apply

        Returns:
            Extent: New offset extent
        """
        if not isinstance(delay, (int, float)):
            raise TypeError("Delay must be numeric")
        return Extent(self.s + delay, self.e + delay)

    # ================================================================
    # logical operations on an extent

    def precedes(self, other: Union['Extent', float]) -> bool:
        """
        Return True if self strictly precedes other.

        Args:
            other: Extent or scalar time value

        Returns:
            bool: True if self ends before other starts
        """
        if isinstance(other, Extent):
            return self.e <= other.s
        elif isinstance(other, (int, float)):
            return self.e <= other
        else:
            raise TypeError("Other must be Extent or numeric")

    def follows(self, other: Union['Extent', float]) -> bool:
        """
        Return True if self strictly follows other.

        Args:
            other: Extent or scalar time value

        Returns:
            bool: True if self starts after other ends
        """
        if isinstance(other, Extent):
            return other.e <= self.s
        elif isinstance(other, (int, float)):
            return other <= self.s
        else:
            raise TypeError("Other must be Extent or numeric")

    def overlaps(self, other: Union['Extent', float]) -> bool:
        """
        Return True if any part of self overlaps other.

        Args:
            other: Extent or scalar time value

        Returns:
            bool: True if there is any overlap
        """
        if isinstance(other, Extent):
            return not (self.e <= other.s or other.e <= self.s)
        elif isinstance(other, (int, float)):
            return self.s <= other < self.e
        else:
            raise TypeError("Other must be Extent or numeric")

    def spans(self, other: Union['Extent', float]) -> bool:
        """
        Return True if self completely encompasses other.

        Args:
            other: Extent or scalar time value

        Returns:
            bool: True if other is entirely within self
        """
        if isinstance(other, Extent):
            return self.s <= other.s and self.e >= other.e
        elif isinstance(other, (int, float)):
            return self.s <= other < self.e
        else:
            raise TypeError("Other must be Extent or numeric")

    def equals(self, other: 'Extent') -> bool:
        """
        Return True if self and other have identical start and end times.

        Args:
            other: Extent to compare

        Returns:
            bool: True if extents are identical
        """
        if not isinstance(other, Extent):
            raise TypeError("Other must be an Extent")
        return self.s == other.s and self.e == other.e

    # ================================================================
    # Modifying duration

    def _modify_duration(self, duration: float, anchor: str) -> 'Extent':
        """
        Create a new extent with specified duration anchored relative to self.

        Private helper method for set_duration and extend.
        """
        if self.is_indefinite():
            raise ValueError("Cannot operate on indefinite extent")
        if anchor == 'start':
            return Extent(start=self.s, duration=duration)
        elif anchor == 'end':
            return Extent(end=self.e, duration=duration)
        elif anchor == 'center':
            center = (self.s + self.e) / 2
            half_dur = duration / 2
            return Extent(start=center - half_dur, end=center + half_dur)
        else:
            raise ValueError("Anchor must be 'start', 'end', or 'center'")

    def set_duration(self, duration: float, anchor: str = 'start') -> 'Extent':
        """
        Return a copy with the specified duration, anchored at the specified point.

        Args:
            duration: New duration (must be non-negative)
            anchor: Anchor point for scaling: 'start', 'end', or 'center'

        Returns:
            Extent: New extent with specified duration

        Raises:
            ValueError: If duration is negative or extent is indefinite
            TypeError: If duration is not numeric
        """
        if not isinstance(duration, (int, float)):
            raise TypeError("Duration must be numeric")
        if duration < 0:
            raise ValueError("Duration cannot be negative")

        # self is finite or empty
        return self._modify_duration(duration, anchor)

    def extend(self, delta: float, anchor: str = 'start') -> 'Extent':
        """
        Return a copy with duration changed by delta, anchored as specified.

        Args:
            delta: Change in duration (positive = longer, negative = shorter)
            anchor: 'start' (extend from start), 'end', or 'center'

        Returns:
            Extent: New extent with modified duration

        Raises:
            ValueError: If resulting duration would be negative or extent is indefinite
            TypeError: If delta is not numeric
        """
        if not isinstance(delta, (int, float)):
            raise TypeError("Delta must be numeric")

        duration = self.duration() + delta
        if duration < 0:
            raise ValueError("Resulting duration would be negative")

        return self._modify_duration(duration, anchor)

    def stretch(self, factor: float, anchor: str = 'start') -> 'Extent':
        """
        Stretch the extent by factor around anchor point.

        Args:
            factor: Multiplier for duration (<1.0 = shorter, >1.0=longer)
            anchor: 'start' (extend from start), 'end', or 'center'

        Returns:
            Extent: New extent with modified duration

        Raises:
            ValueError: If resulting duration would be negative or extent is indefinite
            TypeError: If factor is not numeric
        """
        if not isinstance(factor, (int, float)):
            raise TypeError("Factor must be numeric")
        if factor <= 0:
            raise ValueError("Factor must be positive")

        return self._modify_duration(self.duration() * factor, anchor)

    # ================================================================
    # operations on multiple extents

    def union(self, *others: 'Extent') -> 'Extent':
        """
        Return the union of self with one or more other extents.

        Args:
            *others: Zero or more Extent objects

        Returns:
            Extent: Union of all provided extents
        """
        for other in others:
            if not isinstance(other, Extent):
                raise TypeError("All arguments must be Extent objects")
        return Extent.union_all([self] + list(others))

    @classmethod
    def union_all(cls, extents: Iterable['Extent']) -> 'Extent':
        """
        Create the union of multiple extents.

        Args:
            extents: Iterable of Extent objects

        Returns:
            Extent: Union of all extents

        Raises:
            ValueError: If extents is empty
        """
        if not extents:
            return cls.null()

        starts = [e.s for e in extents]
        ends = [e.e for e in extents]

        return cls(min(starts), max(ends))

    def intersect(self, *others: 'Extent') -> 'Extent':
        """
        Return the intersection of self with one or more other extents.

        Args:
            *others: Zero or more Extent objects

        Returns:
            Extent: Intersection of all provided extents (may be empty)
        """
        for other in others:
            if not isinstance(other, Extent):
                raise TypeError("All arguments must be Extent objects")
        return Extent.intersect_all([self] + list(others))

    @classmethod
    def intersect_all(cls, extents: Iterable['Extent']) -> 'Extent':
        """
        Return the intersection of multiple extents.

        Args:
            extents: Iterable of Extent objects

        Returns:
            Extent: Intersection of all extents (may be empty)
        """
        if not extents:
            return cls.null()

        s = max(e.s for e in extents)
        e = min(e.e for e in extents)

        if s <= e:
            return cls(s, e)
        else:
            return cls.null()

    @classmethod
    def find_gaps(cls, extents: List['Extent']) -> List['Extent']:
        """
        Return the gaps between sorted, non-overlapping extents.

        Args:
            extents: List of Extent objects, must be sorted and non-overlapping

        Returns:
            List[Extent]: List of gap extents between the input extents

        Raises:
            ValueError: If extents are not sorted or contain overlaps
        """
        if len(extents) <= 1:
            return []

        # Validate that extents are sorted and non-overlapping
        for i in range(len(extents) - 1):
            if extents[i].e > extents[i + 1].s:
                raise ValueError("Extents must be sorted and non-overlapping")

        gaps = []
        for i in range(len(extents) - 1):
            gap_start = extents[i].e
            gap_end = extents[i + 1].s
            if gap_start < gap_end:
                gaps.append(cls(gap_start, gap_end))

        return gaps

    # Utility class methods
    @classmethod
    def null(cls) -> 'Extent':
        """Return an empty (null) extent."""
        return cls(0, 0)

    @classmethod
    def infinite(cls) -> 'Extent':
        """Return an infinite extent."""
        return cls(cls.NINF, cls.PINF)
