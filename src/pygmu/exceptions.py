# src/pygmu/exceptions.py
class PygmuError(Exception):
    """Base class for all pygmu exceptions."""


class InvalidExtentError(PygmuError):
    """Raised when an extent is malformed or violates assumptions."""


class FrameRateMismatchError(PygmuError):
    """Raised when two connected components disagree on frame rate."""


class ChannelMismatchError(PygmuError):
    """Raised when two connected components disagree on channel count."""


class ContractViolationError(PygmuError):
    """
    Raised when a ProcessingElement violates the render() contract:
    wrong dtype/shape, bad extent, wrong frame_rate/channels, etc.
    """
