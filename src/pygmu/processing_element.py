# src/pygmu/processing_element.py
from __future__ import annotations
from abc import ABC, abstractmethod
from .extent import Extent
from .frame_buffer import FrameBuffer

class ProcessingElement(ABC):
    """
    Root interface for all PEs.
    Contract: render() returns a finite FrameBuffer for the requested Extent.
    """

    @abstractmethod
    def render(self, extent: Extent) -> FrameBuffer:
        """
        Return audio for [extent.start, extent.end).
        May receive an infinite extent; must return a finite FrameBuffer.
        """

    @abstractmethod
    def frame_rate(self) -> int:
        """Samples per second."""

    @abstractmethod
    def channels(self) -> int:
        """Number of output channels."""

    # Optional: where output can be non-zero (optimization hint)
    def content_extent(self) -> Extent | None:
        return None

    # Optional: algorithmic latency (frames)
    def latency(self) -> int:
        return 0
