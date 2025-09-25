import math
from typing import Union, Optional, List, Iterable, Sequence

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
                start = end - duration
            elif end == self.PINF:
                end = start + duration
            else:
                if abs((end - start) - duration) > 1e-10:
                    raise ValueError(f"Duration {duration} conflicts with start/end range {end - start}")

        # Validation
        if end < start:
            raise ValueError(f"End ({end}) cannot be before start ({start})")

        self.s, self.e = start, end

    # ------------------------------------------------------------------
    # Representations

    def __str__(self) -> str:
        start_str = "NINF" if self.s == self.NINF else str(self.s)
        end_str = "PINF" if self.e == self.PINF else str(self.e)
        return f"[{start_str}, {end_str})"

    def __repr__(self) -> str:
        st = "NINF" if self.s == self.NINF else str(self.s)
        et = "PINF" if self.e == self.PINF else str(self.e)
        return f"<Extent {self.__hash__()}: s={st}, e={et}>"

    def __eq__(self, other):
        if not isinstance(other, Extent):
            return NotImplemented
        return self.s == other.s and self.e == other.e

    def __hash__(self) -> int:
        return hash((self.s, self.e))

    # ------------------------------------------------------------------
    # Basic accessors

    def start(self) -> float:
        """Return the start time (inclusive)."""
        return self.s

    def end(self) -> float:
        """Return the end time (exclusive)."""
        return self.e

    def is_indefinite(self) -> bool:
        """Return True if the extent has indefinite duration (open on either side)."""
        return self.s == self.NINF or self.e == self.PINF

    def is_finite(self) -> bool:
        """Return True if both start and end are finite."""
        return math.isfinite(self.s) and math.isfinite(self.e)

    def is_empty(self) -> bool:
        """Return True if the extent is empty (zero duration or inverted after quantization)."""
        return self.s >= self.e

    def is_point(self, eps: float = 0.0) -> bool:
        """Return True if the extent collapses to a single instant within tolerance eps."""
        return abs(self.e - self.s) <= eps

    def duration(self) -> float:
        """Return the duration of the extent, or INDEFINITE_DURATION if indefinite."""
        if self.is_indefinite():
            return self.INDEFINITE_DURATION
        elif self.is_empty():
            return 0.0
        else:
            return self.e - self.s

    def offset(self, delay: float) -> 'Extent':
        """Return a new Extent offset by the specified delay."""
        if not isinstance(delay, (int, float)):
            raise TypeError("Delay must be numeric")
        return Extent(self.s + delay, self.e + delay)

    def with_start(self, start: float) -> 'Extent':
        """Return a copy with a new start (end unchanged)."""
        return Extent(start, self.e)

    def with_end(self, end: float) -> 'Extent':
        """Return a copy with a new end (start unchanged)."""
        return Extent(self.s, end)

    def contains_time(self, t: float) -> bool:
        """Return True if t ∈ [start, end)."""
        return self.s <= t < self.e

    # ------------------------------------------------------------------
    # Relations / predicates vs other extents or times

    def precedes(self, other: Union['Extent', float]) -> bool:
        """Return True if self strictly precedes other."""
        if isinstance(other, Extent):
            return self.e <= other.s
        elif isinstance(other, (int, float)):
            return self.e <= other
        else:
            raise TypeError("Other must be Extent or numeric")

    def follows(self, other: Union['Extent', float]) -> bool:
        """Return True if self strictly follows other."""
        if isinstance(other, Extent):
            return other.e <= self.s
        elif isinstance(other, (int, float)):
            return other <= self.s
        else:
            raise TypeError("Other must be Extent or numeric")

    def overlaps(self, other: Union['Extent', float]) -> bool:
        """Return True if any part of self overlaps other."""
        if isinstance(other, Extent):
            return not (self.e <= other.s or other.e <= self.s)
        elif isinstance(other, (int, float)):
            return self.s <= other < self.e
        else:
            raise TypeError("Other must be Extent or numeric")

    def spans(self, other: Union['Extent', float]) -> bool:
        """Return True if self completely encompasses other."""
        if isinstance(other, Extent):
            return self.s <= other.s and self.e >= other.e
        elif isinstance(other, (int, float)):
            return self.s <= other < self.e
        else:
            raise TypeError("Other must be Extent or numeric")

    def equals(self, other: 'Extent') -> bool:
        """Return True if extents are identical."""
        if not isinstance(other, Extent):
            raise TypeError("Other must be an Extent")
        return self.s == other.s and self.e == other.e

    def is_adjacent(self, other: 'Extent', eps: float = 0.0) -> bool:
        """Return True if the extents touch but do not overlap (within eps)."""
        return abs(self.e - other.s) <= eps or abs(other.e - self.s) <= eps

    def overlap_length(self, other: 'Extent') -> float:
        """Return the length of the overlap with other (0 if none)."""
        s = max(self.s, other.s)
        e = min(self.e, other.e)
        return max(0.0, e - s)

    # ------------------------------------------------------------------
    # Logical ops on one or more extents

    def union(self, *others: 'Extent') -> 'Extent':
        """Return the union of self with one or more other extents."""
        for other in others:
            if not isinstance(other, Extent):
                raise TypeError("All arguments must be Extent objects")
        return Extent.union_all([self] + list(others))

    @classmethod
    def union_all(cls, extents: Iterable['Extent']) -> 'Extent':
        """Create the union of multiple extents."""
        extents = list(extents)
        if not extents:
            return cls.null()
        starts = [e.s for e in extents]
        ends = [e.e for e in extents]
        return cls(min(starts), max(ends))

    def intersect(self, *others: 'Extent') -> 'Extent':
        """Return the intersection of self with one or more other extents (may be empty)."""
        for other in others:
            if not isinstance(other, Extent):
                raise TypeError("All arguments must be Extent objects")
        return Extent.intersect_all([self] + list(others))

    @classmethod
    def intersect_all(cls, extents: Iterable['Extent']) -> 'Extent':
        """Return the intersection of multiple extents (may be empty)."""
        extents = list(extents)
        if not extents:
            return cls.null()
        s = max(e.s for e in extents)
        e = min(e.e for e in extents)
        if s <= e:
            return cls(s, e)
        else:
            return cls.null()

    def clamp_to(self, bounds: 'Extent') -> 'Extent':
        """
        Clip self to the given bounds.
        Returns an empty extent if there is no overlap.
        """
        if not isinstance(bounds, Extent):
            raise TypeError("bounds must be an Extent")
        if not self.overlaps(bounds):
            return Extent.null()
        return Extent(max(self.s, bounds.s), min(self.e, bounds.e))

    def difference(self, other: 'Extent') -> List['Extent']:
        """
        Return self / other as 0, 1, or 2 extents.
        """
        if not isinstance(other, Extent):
            raise TypeError("other must be an Extent")
        if not self.overlaps(other):
            return [Extent(self.s, self.e)]
        out: List[Extent] = []
        if other.s > self.s:
            out.append(Extent(self.s, min(self.e, other.s)))
        if other.e < self.e:
            out.append(Extent(max(self.s, other.e), self.e))
        return [e for e in out if e.s < e.e]

    def split_at(self, cuts: Iterable[float]) -> List['Extent']:
        """
        Split self at the given cut times strictly inside [s, e).
        Returns a list of 1..(len(cuts)+1) extents.
        """
        pts = sorted(t for t in cuts if self.s < t < self.e)
        if not pts:
            return [Extent(self.s, self.e)]
        out: List[Extent] = []
        cur = self.s
        for t in pts:
            out.append(Extent(cur, t))
            cur = t
        out.append(Extent(cur, self.e))
        return out

    def pad(self, left: float = 0.0, right: float = 0.0) -> 'Extent':
        """
        Asymmetrically expand self by left/right amounts.
        Raises if extent is indefinite.
        """
        if self.is_indefinite():
            raise ValueError("Cannot pad indefinite extent")
        return Extent(self.s - left, self.e + right)

    def quantize(self, step: float, mode: str = "floor") -> 'Extent':
        """
        Snap start and end to a grid of size 'step'.
        Infinities remain infinite.
        """
        if step <= 0:
            raise ValueError("step must be positive")
        if mode not in ("floor", "ceil", "round"):
            raise ValueError("mode must be 'floor'|'ceil'|'round'")
        q = math.floor if mode == "floor" else (math.ceil if mode == "ceil" else round)

        def snap(x: float) -> float:
            return x if not math.isfinite(x) else q(x / step) * step

        return Extent(snap(self.s), snap(self.e))

    def bounded(self, min_start: float, max_end: float) -> 'Extent':
        """
        Replace infinities with finite guards (useful before allocation).
        """
        s = self.s if math.isfinite(self.s) else min_start
        e = self.e if math.isfinite(self.e) else max_end
        return Extent(s, e)

    def next_edge_after(self, t: float) -> Optional[float]:
        """
        Return the next boundary at or after time t:
        - start if t < start,
        - end if start <= t < end,
        - None if t >= end.
        """
        if t < self.s:
            return self.s
        if t < self.e:
            return self.e
        return None

    def prev_edge_before(self, t: float) -> Optional[float]:
        """
        Return the previous boundary at or before time t:
        - end if t > end,
        - start if start < t <= end,
        - None if t <= start.
        """
        if t > self.e:
            return self.e
        if t > self.s:
            return self.s
        return None

    # ------------------------------------------------------------------
    # Collection utilities

    @classmethod
    def find_gaps(cls, extents: List['Extent']) -> List['Extent']:
        """
        Return the gaps between sorted, non-overlapping extents.

        Args:
            extents: List of Extent objects, must be sorted and non-overlapping
        """
        if len(extents) <= 1:
            return []
        for i in range(len(extents) - 1):
            if extents[i].e > extents[i + 1].s:
                raise ValueError("Extents must be sorted and non-overlapping")
        gaps: List[Extent] = []
        for i in range(len(extents) - 1):
            gap_start = extents[i].e
            gap_end = extents[i + 1].s
            if gap_start < gap_end:
                gaps.append(cls(gap_start, gap_end))
        return gaps

    @classmethod
    def merge_adjacent(cls, extents: Sequence['Extent'], eps: float = 0.0) -> List['Extent']:
        """
        Merge overlapping or touching (within eps) extents.
        Assumes extents are in arbitrary order.
        """
        if not extents:
            return []
        xs = sorted(extents, key=lambda e: (e.s, e.e))
        out: List[Extent] = [xs[0]]
        for e in xs[1:]:
            last = out[-1]
            # overlap or touch
            if e.s <= last.e + eps:
                out[-1] = Extent(last.s, max(last.e, e.e))
            else:
                out.append(e)
        return out

    @classmethod
    def total_covered_length(cls, extents: Sequence['Extent']) -> float:
        """
        Length of the union of all extents (merging overlaps/touches).
        """
        merged = cls.merge_adjacent(list(extents))
        return sum(max(0.0, e.e - e.s) for e in merged)

    # ------------------------------------------------------------------
    # Utility factories

    @classmethod
    def null(cls) -> 'Extent':
        """Return an empty (null) extent."""
        return cls(0, 0)

    @classmethod
    def infinite(cls) -> 'Extent':
        """Return an infinite extent."""
        return cls(cls.NINF, cls.PINF)
