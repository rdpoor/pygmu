"""Pygmu – Python generative-music framework (composer-first, pull-render graph).

Public API:
    Extent, FrameBuffer, ProcessingElement,
    BaseTransport, OfflineTransport,
    PygmuError and subclasses
"""

from .extent import Extent
from .frame_buffer import FrameBuffer
from .processing_element import ProcessingElement
from .base_transport import BaseTransport
from .offline_transport import OfflineTransport
from .exceptions import (
    PygmuError,
    InvalidExtentError,
    FrameRateMismatchError,
    ChannelMismatchError,
    ContractViolationError,
)

__all__ = [
    "Extent", "FrameBuffer", "ProcessingElement",
    "BaseTransport", "OfflineTransport",
    "PygmuError", "InvalidExtentError",
    "FrameRateMismatchError", "ChannelMismatchError",
    "ContractViolationError",
]
