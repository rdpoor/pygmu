# src/pygmu/frame_buffer.py
from __future__ import annotations
import numpy as np
import math
from .extent import Extent

class FrameBuffer:
    __slots__ = ("_data", "_frame_rate", "_extent")

    DEFAULT_DTYPE = np.float32
    GRID_STEP = 1.0  # 1 frame

    def __init__(self, data: np.ndarray, frame_rate: int, extent: Extent, *, quantize_mode: str = "floor"):
        if data.ndim != 2:
            raise ValueError("FrameBuffer data must be 2-D (channels, frames).")
        if data.dtype != self.DEFAULT_DTYPE:
            data = data.astype(self.DEFAULT_DTYPE, copy=False)
        if not extent.is_finite():
            raise ValueError("FrameBuffer extent must be finite.")

        # Quantize to frame grid for internal consistency
        qext = extent.quantize(self.GRID_STEP, quantize_mode)
        s, e = int(qext.start()), int(qext.end())
        if e < s:
            raise ValueError("Extent end before start after quantization.")
        if data.shape[1] != (e - s):
            raise ValueError("Data length != extent length after quantization.")

        self._data = data
        self._frame_rate = int(frame_rate)
        self._extent = Extent(s, e)

    def __array__(self, dtype=None) -> np.ndarray:
        return np.asarray(self._data, dtype=dtype)

    @property
    def data(self) -> np.ndarray: return self._data
    @property
    def frame_rate(self) -> int:  return self._frame_rate
    @property
    def extent(self) -> Extent:   return self._extent
    @property
    def channels(self) -> int:    return self._data.shape[0]
    @property
    def nframes(self) -> int:     return self._data.shape[1]
    @property
    def dtype(self):              return self._data.dtype

    # -------------------- DRY helpers --------------------

    @classmethod
    def _prepare_alloc(
        cls,
        channels: int,
        nframes: int,
        frame_rate: int,
        extent: Extent,
        *,
        quantize_mode: str = "floor",
    ) -> tuple[int, int, int, Extent]:
        """Normalize & validate inputs for buffer allocation."""
        if not extent.is_finite():
            raise ValueError("Extent must be finite for allocation.")
        if channels < 1:
            raise ValueError("channels must be >= 1")
        if nframes < 0:
            raise ValueError("nframes must be >= 0")

        qext = extent.quantize(cls.GRID_STEP, quantize_mode)
        expected = int(qext.duration())
        if nframes != expected:
            raise ValueError(f"Extent duration ({expected}) must match nframes ({nframes})")

        return int(channels), int(nframes), int(frame_rate), qext

    @classmethod
    def _new_with_init(
        cls,
        channels: int,
        nframes: int,
        frame_rate: int,
        extent: Extent,
        *,
        quantize_mode: str,
        init: str,  # "zeros" | "empty"
    ) -> "FrameBuffer":
        ch, nf, fr, qext = cls._prepare_alloc(channels, nframes, frame_rate, extent, quantize_mode=quantize_mode)
        if init == "zeros":
            data = np.zeros((ch, nf), dtype=cls.DEFAULT_DTYPE)
        elif init == "empty":
            data = np.empty((ch, nf), dtype=cls.DEFAULT_DTYPE)
        else:
            raise ValueError("init must be 'zeros' or 'empty'")
        return cls(data, fr, qext, quantize_mode=quantize_mode)

    # -------------------- Public factories --------------------

    @classmethod
    def zeros(
        cls,
        channels: int,
        nframes: int,
        frame_rate: int,
        extent: Extent,
        *,
        quantize_mode: str = "floor",
    ) -> "FrameBuffer":
        """Create a zero-filled FrameBuffer."""
        return cls._new_with_init(channels, nframes, frame_rate, extent, quantize_mode=quantize_mode, init="zeros")

    @classmethod
    def empty(
        cls,
        channels: int,
        nframes: int,
        frame_rate: int,
        extent: Extent,
        *,
        quantize_mode: str = "floor",
    ) -> "FrameBuffer":
        """Create an uninitialized FrameBuffer (values are arbitrary)."""
        return cls._new_with_init(channels, nframes, frame_rate, extent, quantize_mode=quantize_mode, init="empty")

    def slice_time(self, sub: Extent) -> "FrameBuffer":
        """
        Extract a time-based slice from this FrameBuffer.

        Args:
            sub (Extent): The requested extent in *absolute* frame coordinates.
                - If the request is partially outside this buffer's extent, the
                  result will be clipped and silent-filled as needed.
                - If the request is infinite in either direction, it is clipped
                  to this buffer's finite extent.

        Returns:
            FrameBuffer: A new buffer covering [sub.start(), sub.end()), with:
                - Zeros outside the overlap with this buffer's data
                - Copied samples where the extents overlap
                - Always finite, possibly length 0 if e_req <= s_req
        """
        # --- Step 1: Resolve possibly infinite request into finite start/end
        s_req = sub.start()
        e_req = sub.end()
        if not math.isfinite(s_req) or not math.isfinite(e_req):
            # Clip infinities to this buffer's own finite extent
            s_req = self._extent.start() if not math.isfinite(s_req) else s_req
            e_req = self._extent.end()   if not math.isfinite(e_req) else e_req

        # --- Step 2: Quantize to integer frame indices (floor mode)
        qreq = Extent(s_req, e_req).quantize(step=1.0, mode="floor")
        s_req, e_req = int(qreq.start()), int(qreq.end())

        if e_req <= s_req:
            # Return an empty buffer of the right channel count and frame rate
            return FrameBuffer.zeros(
                self.channels, 0, self.frame_rate, Extent(s_req, s_req)
            )

        # --- Step 3: Compute overlap with this buffer's finite extent
        ov = self._extent.intersect(Extent(s_req, e_req))
        out = np.zeros((self.channels, e_req - s_req), dtype=np.float32)

        if not ov.is_empty():
            # Source indices relative to this buffer
            src_s = int(ov.start() - self._extent.start())
            src_e = int(ov.end()   - self._extent.start())
            # Destination indices relative to the new slice
            dst_s = int(ov.start() - s_req)
            dst_e = dst_s + int(ov.end() - ov.start())
            # Copy overlapping region
            out[:, dst_s:dst_e] = self._data[:, src_s:src_e]

        return FrameBuffer(out, self.frame_rate, Extent(s_req, e_req))
