# tests/test_strict_validation.py
import os
import unittest
import numpy as np

from pygmu import (
    Extent,
    FrameBuffer,
    ProcessingElement,
    BaseTransport,
    ContractViolationError,
)


def _with_env(var: str, value: str):
    """Simple context manager to set/restore an env var."""
    class _Ctx:
        def __enter__(self):
            self._old = os.environ.get(var)
            os.environ[var] = value
        def __exit__(self, exc_type, exc, tb):
            if self._old is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = self._old
    return _Ctx()


# ----- Test doubles for bad behavior -----

class BadChannelsPE(ProcessingElement):
    """Declares 2 channels but returns a 1-channel FrameBuffer."""
    def frame_rate(self) -> int: return 48000
    def channels(self) -> int: return 2
    def render(self, extent: Extent) -> FrameBuffer:
        n = int(extent.duration())
        data = np.zeros((1, n), dtype=np.float32)  # 1 channel only!
        return FrameBuffer(data, self.frame_rate(), extent)


class BadFrameRatePE(ProcessingElement):
    """Reports 48000 but returns FrameBuffer tagged with 44100."""
    def frame_rate(self) -> int: return 48000
    def channels(self) -> int: return 1
    def render(self, extent: Extent) -> FrameBuffer:
        n = int(extent.duration())
        data = np.zeros((1, n), dtype=np.float32)
        # Mismatch here: fb.frame_rate != pe.frame_rate()
        return FrameBuffer(data, 44100, extent)


class OutsideExtentPE(ProcessingElement):
    """Returns a FrameBuffer whose extent lies outside the requested window."""
    def __init__(self, fr=48000, ch=1):
        self._fr = fr
        self._ch = ch
    def frame_rate(self) -> int: return self._fr
    def channels(self) -> int: return self._ch
    def render(self, extent: Extent) -> FrameBuffer:
        # Request might be [100, 110); we'll *ignore* it and return [200,210)
        out = Extent(200, 210)
        data = np.zeros((self._ch, int(out.duration())), dtype=np.float32)
        return FrameBuffer(data, self._fr, out)


class NonFiniteExtentPE(ProcessingElement):
    """Returns a FrameBuffer with an indefinite extent (+inf end)."""
    def frame_rate(self) -> int: return 48000
    def channels(self) -> int: return 1
    def render(self, extent: Extent) -> FrameBuffer:
        out = Extent(0, Extent.PINF)   # non-finite
        # Give a finite array anyway; validator should reject non-finite fb.extent.
        data = np.zeros((1, 8), dtype=np.float32)
        return FrameBuffer(data, self.frame_rate(), out)


# ----- Tests -----

class TestStrictValidation(unittest.TestCase):
    def test_channels_mismatch_raises(self):
        with _with_env("PYGMU_STRICT", "1"):
            pe = BadChannelsPE()
            t = BaseTransport(pe, block_size=8)
            with self.assertRaises(ContractViolationError):
                t.render(0, 8, lambda arr, fr: None)

    def test_frame_rate_mismatch_raises(self):
        with _with_env("PYGMU_STRICT", "1"):
            pe = BadFrameRatePE()
            t = BaseTransport(pe, block_size=8)
            with self.assertRaises(ContractViolationError):
                t.render(0, 8, lambda arr, fr: None)

    def test_extent_outside_request_raises(self):
        with _with_env("PYGMU_STRICT", "1"):
            pe = OutsideExtentPE()
            t = BaseTransport(pe, block_size=16)
            with self.assertRaises(ContractViolationError):
                t.render(100, 110, lambda arr, fr: None)

    def test_non_finite_extent_raises(self):
        with _with_env("PYGMU_STRICT", "1"):
            pe = NonFiniteExtentPE()
            t = BaseTransport(pe, block_size=8)
            with self.assertRaises(ContractViolationError):
                t.render(0, 8, lambda arr, fr: None)


if __name__ == "__main__":
    unittest.main()
