# src/pygmu/exceptions.py
from __future__ import annotations

from typing import Any, Optional


class PygmuError(Exception):
    """
    Base class for all pygmu exceptions.

    Catch this to handle any pygmu-specific error without trapping unrelated
    built-in exceptions.
    """


class ContractViolationError(PygmuError):
    """
    A ProcessingElement or related component violated a declared contract.

    Typical causes include:
      - returning arrays with the wrong dtype or shape,
      - producing an extent outside the requested window,
      - mismatched frame rate or channel count,
      - inconsistent header fields (extent vs nframes).

    Optional context fields can be passed when raising to improve diagnostics
    and enable programmatic handling in tests or higher-level code.
    """

    def __init__(
        self,
        message: str,
        *,
        pe_name: Optional[str] = None,
        expected: Any = None,
        actual: Any = None,
        requested: Any = None,
        produced: Any = None,
    ) -> None:
        """
        Args:
            message: Human-readable error description.
            pe_name: Name or class name of the offending ProcessingElement.
            expected: Value that was expected (frame rate, channels, etc).
            actual: The value that was actually observed.
            requested: The request object/extent (if relevant).
            produced: The produced object/extent (if relevant).
        """
        super().__init__(message)
        self.pe_name: Optional[str] = pe_name
        self.expected: Any = expected
        self.actual: Any = actual
        self.requested: Any = requested
        self.produced: Any = produced


class FrameRateMismatchError(ContractViolationError):
    """
    Two connected components disagree on frame rate.

    Inherit from ContractViolationError so callers can choose to catch the
    specific mismatch or the broader contract violation.
    """


class ChannelMismatchError(ContractViolationError):
    """
    Two connected components disagree on channel count.

    Inherit from ContractViolationError so callers can choose to catch the
    specific mismatch or the broader contract violation.
    """


class InvalidExtentError(PygmuError, ValueError):
    """
    Extent is malformed or violates assumptions.

    Dual-inherits from ValueError for ergonomic catching alongside built-ins
    where appropriate.
    """


class TransportError(PygmuError):
    """
    Transport/render driver failure.

    Use for issues in BaseTransport/OfflineTransport such as loop invariants,
    scheduling assumptions, or sink-call contract failures.
    """


class ProcessingError(PygmuError):
    """
    ProcessingElement failed to render or process audio.

    Use when wrapping lower-level exceptions arising within render() or other
    PE methods. Prefer `raise ProcessingError(...) from e` to preserve context.
    """

class InvalidFrameRateError(PygmuError, ValueError):
    """Frame rate is non-positive or otherwise invalid."""

class InvalidChannelsError(PygmuError, ValueError):
    """Channel count is invalid (e.g., <1)."""

__all__ = [
    "PygmuError",
    "ContractViolationError",
    "FrameRateMismatchError",
    "ChannelMismatchError",
    "InvalidExtentError",
    "TransportError",
    "ProcessingError",
    "InvalidFrameRateError",
    "InvalidChannelsError",
]
