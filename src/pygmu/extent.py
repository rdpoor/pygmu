# src/pygmu/extent.py
import math
import warnings
from typing import Union, Optional, List, Iterable

class Extent:
    """
    Represents a temporal extent with support for indefinite start and/or end.

    An extent is defined by (start, end) where start is inclusive and end is exclusive.
    Start may be -inf, end may be +inf. Duration is end - start if both finite,
    0 if empty, or inf if indefinite.
    """

    NINF = -math.inf
    PINF = math.inf
    INDEFINITE_DURATION = math.inf

    def __init__(self, start: float = NINF, end: float = PINF, duration: Optional[float] = None):
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise TypeError("start and end must be numeric")
        if duration is not None and not isinstance(duration, (int, float)):
            raise TypeError("duration must be None or numeric")

        if duration is not None:
            if duration < 0:
                raise ValueError("duration cannot be negative")
            if start == self.NINF and end == self.PINF:
                raise ValueError("cannot set duration when both start and end are infinite")
            elif start == self.NINF:
                start = end - duration
            elif end == self.PINF:
                end = start + duration
            else:
                if abs((end - start) - duration) > 1e-10:
                    raise ValueError("duration conflicts with start/end")

        if end < start:
            raise ValueError(f"end {end} cannot be before start {start}")

        self.s, self.e = start, end

    # ------------------------------------------------------------------
    # Properties
    @property
    def start(self) -> float:
        return self.s

    @property
    def end(self) -> float:
        return self.e

    @property
    def duration(self) -> float:
        if self.is_indefinite():
            return self.INDEFINITE_DURATION
        if self.is_empty():
            return 0.0
        return self.e - self.s

    # ------------------------------------------------------------------
    # Representations
    def __str__(self) -> str:
        s = "NINF" if self.s == self.NINF else str(self.s)
        e = "PINF" if self.e == self.PINF else str(self.e)
        return f"[{s}, {e})"

    def __repr__(self) -> str:
        return f"<Extent s={self.s}, e={self.e}>"

    def __eq__(self, other) -> bool:
        return isinstance(other, Extent) and self.s == other.s and self.e == other.e

    def __hash__(self) -> int:
        return hash((self.s, self.e))

    # ------------------------------------------------------------------
    # Basic predicates
    def is_indefinite(self) -> bool:
        """True if either bound is infinite."""
        return not self.is_finite()F

    def is_finite(self) -> bool:
        """True if both bounds are finite."""
        return math.isfinite(self.s) and math.isfinite(self.e)

    def is_empty(self) -> bool:
        return self.s >= self.e

    # ------------------------------------------------------------------
    # Simple transforms
    def offset(self, delay: float) -> "Extent":
        if not isinstance(delay, (int, float)):
            raise TypeError("delay must be numeric")
        return Extent(self.s + delay, self.e + delay)

    def pad(self, *, left: float = 0.0, right: float = 0.0) -> "Extent":
        if left < 0 or right < 0:
            raise ValueError("pad() amounts must be non-negative")
        return Extent(self.s - left, self.e + right)

    # ------------------------------------------------------------------
    # Duration-changing helpers
    def _modify_duration(self, duration: float, anchor: str) -> "Extent":
        if not self.is_finite():
            raise ValueError("cannot modify indefinite extent")
        if duration < 0:
            raise ValueError("duration must be non-negative")
        if anchor == "start":
            return Extent(start=self.s, duration=duration)
        elif anchor == "end":
            return Extent(end=self.e, duration=duration)
        elif anchor == "center":
            c = (self.s + self.e) / 2.0
            h = duration / 2.0
            return Extent(c - h, c + h)
        else:
            raise ValueError("anchor must be 'start', 'end', or 'center'")

    def set_duration(self, duration: float, anchor: str = "start") -> "Extent":
        if not isinstance(duration, (int, float)):
            raise TypeError("duration must be numeric")
        return self._modify_duration(float(duration), anchor)

    def extend(self, delta: float, anchor: str = "start") -> "Extent":
        if not isinstance(delta, (int, float)):
            raise TypeError("delta must be numeric")
        cur = self.duration
        if cur is self.INDEFINITE_DURATION:
            raise ValueError("cannot extend indefinite extent")
        new = cur + float(delta)
        if new < 0:
            raise ValueError("resulting duration negative")
        return self._modify_duration(new, anchor)

    def stretch(self, factor: float, anchor: str = "start") -> "Extent":
        if not isinstance(factor, (int, float)):
            raise TypeError("factor must be numeric")
        if factor <= 0:
            raise ValueError("factor must be > 0")
        cur = self.duration
        if cur is self.INDEFINITE_DURATION:
            raise ValueError("cannot stretch indefinite extent")
        return self._modify_duration(cur * float(factor), anchor)

    # ------------------------------------------------------------------
    # Logical relations
    def precedes(self, other: Union["Extent", float]) -> bool:
        if isinstance(other, Extent):
            return self.e <= other.s
        return self.e <= other

    def follows(self, other: Union["Extent", float]) -> bool:
        if isinstance(other, Extent):
            return other.e <= self.s
        return other <= self.s

    def overlaps(self, other: Union["Extent", float]) -> bool:
        if isinstance(other, Extent):
            return not (self.e <= other.s or other.e <= self.s)
        return self.s <= other < self.e

    def spans(self, other: Union["Extent", float]) -> bool:
        if isinstance(other, Extent):
            return self.s <= other.s and self.e >= other.e
        return self.s <= other < self.e

    def equals(self, other: "Extent") -> bool:
        if not isinstance(other, Extent):
            raise TypeError("other must be an Extent")
        return self.s == other.s and self.e == other.e

    # ------------------------------------------------------------------
    # Collections
    def union(self, *others: "Extent") -> "Extent":
        return Extent.union_all([self] + list(others))

    @classmethod
    def union_all(cls, extents: Iterable["Extent"]) -> "Extent":
        extents = list(extents)
        if not extents:
            return cls.null()
        return cls(min(e.s for e in extents), max(e.e for e in extents))

    def intersect(self, *others: "Extent") -> "Extent":
        return Extent.intersect_all([self] + list(others))

    @classmethod
    def intersect_all(cls, extents: Iterable["Extent"]) -> "Extent":
        extents = list(extents)
        if not extents:
            return cls.null()
        s = max(e.s for e in extents)
        e = min(e.e for e in extents)
        return cls(s, e) if s <= e else cls.null()

    @classmethod
    def find_gaps(cls, extents: List["Extent"]) -> List["Extent"]:
        if len(extents) <= 1:
            return []
        for i in range(len(extents) - 1):
            if extents[i].e > extents[i + 1].s:
                raise ValueError("extents must be sorted and non-overlapping")
        gaps = []
        for i in range(len(extents) - 1):
            if extents[i].e < extents[i + 1].s:
                gaps.append(cls(extents[i].e, extents[i + 1].s))
        return gaps

    @classmethod
    def total_covered_length(cls, extents: List["Extent"]) -> float:
        """Return total covered length of the union of extents."""
        if not extents:
            return 0.0
        merged = sorted(extents, key=lambda e: e.s)
        total = 0.0
        cur_s, cur_e = merged[0].s, merged[0].e
        for e in merged[1:]:
            if e.s <= cur_e:
                cur_e = max(cur_e, e.e)
            else:
                total += cur_e - cur_s
                cur_s, cur_e = e.s, e.e
        total += cur_e - cur_s
        return total

    # ------------------------------------------------------------------
    # Utilities
    @classmethod
    def null(cls) -> "Extent":
        return cls(0, 0)

    @classmethod
    def infinite(cls) -> "Extent":
        return cls(cls.NINF, cls.PINF)

    def quantize(self, step: float, mode: str = "floor") -> "Extent":
        if step <= 0:
            raise ValueError("step must be > 0")
        if mode not in ("floor", "ceil"):
            raise ValueError("mode must be 'floor' or 'ceil'")

        def q(v: float, fn) -> float:
            return fn(v / step) * step if math.isfinite(v) else v

        if mode == "floor":
            return Extent(q(self.s, math.floor), q(self.e, math.floor))
        else:
            return Extent(q(self.s, math.ceil), q(self.e, math.ceil))
