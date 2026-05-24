# src/pygmu/frame_buffer.py
from __future__ import annotations

import math
from typing import Tuple

import numpy as np
from numpy.typing import NDArray

from .extent import Extent
from .exceptions import InvalidFrameRateError, InvalidChannelsError


class FrameBuffer:
    """
    Audio sample container: (channels, nframes) float32 array + header.

    - Data layout: ndarray of shape (C, N), dtype float32 by default.
    - Header: `frame_rate` (samples/second) and `extent` (absolute time window).
    - Instances are immutable *with respect to header semantics*:
      while the numpy array is mutable, `frame_rate` and `extent` are fixed.

    Quantization:
        On construction (and allocation helpers), the `extent` is quantized to a
        frame grid with `step=1.0`. By default we use a *coverage-preserving*
        policy (`mode="cover"` = floor(start), ceil(end)) so you never lose a
        trailing frame when bounds are non-integral. You can override via the
        `quantize_mode` parameter (e.g., "floor" or "ceil" as defined in
        Extent.quantize()).
    """

    __slots__ = ("_data", "_frame_rate", "_extent")

    DEFAULT_DTYPE = np.float32
    GRID_STEP = 1.0  # 1 frame

    def __init__(
        self,
        data: NDArray[np.floating],
        frame_rate: int,
        extent: Extent,
        *,
        quantize_mode: str = "cover",
    ) -> None:
        """
        Args:
            data: ndarray of shape (channels, nframes). Will be cast to float32 if needed.
            frame_rate: samples per second; must be a positive integer.
            extent: absolute time window the data occupies; must be finite.
            quantize_mode: quantization policy for aligning extent to frame grid.
                - "cover" (default): floor(start), ceil(end)
                - "floor": floor(start), floor(end)
                - "ceil":  ceil(start),  ceil(end)

        Raises:
            InvalidFrameRateError: if frame_rate is non-integer or <= 0.
            ValueError: bad shapes, mismatched lengths, or non-finite extent.
        """
        # Basic shape check
        arr = np.asarray(data)
        if arr.ndim != 2:
            raise ValueError("FrameBuffer data must be 2-D (channels, frames).")

        # Dtype normalize (no copy if already float32)
        if arr.dtype != self.DEFAULT_DTYPE:
            arr = arr.astype(self.DEFAULT_DTYPE, copy=False)

        # Frame rate sanity
        if not isinstance(frame_rate, (int, np.integer)):
            raise InvalidFrameRateError("frame_rate must be an integer")
        if int(frame_rate) <= 0:
            raise InvalidFrameRateError("frame_rate must be > 0")

        # Extent must be finite
        if not extent.is_finite():
            raise ValueError("FrameBuffer extent must be finite.")

        # Quantize to the frame grid for internal consistency
        qext = extent.quantize(self.GRID_STEP, quantize_mode)
        s, e = int(qext.start), int(qext.end)
        if e < s:
            raise ValueError("Extent end before start after quantization.")

        # Verify data length matches quantized extent length
        if arr.shape[1] != (e - s):
            raise ValueError("Data length != extent length after quantization.")

        self._data: NDArray[np.float32] = arr
        self._frame_rate: int = int(frame_rate)
        self._extent: Extent = Extent(s, e)

    def __array__(self, dtype=None) -> NDArray[np.floating]:
        """NumPy protocol: returns the underlying data (optionally cast)."""
        return np.asarray(self._data, dtype=dtype)

    # -------------------- Properties --------------------

    @property
    def data(self) -> NDArray[np.float32]:
        """Underlying ndarray of shape (channels, nframes), dtype float32."""
        return self._data

    @property
    def frame_rate(self) -> int:
        """Samples per second (positive integer)."""
        return self._frame_rate

    @property
    def extent(self) -> Extent:
        """Absolute time window covered by this buffer (finite Extent)."""
        return self._extent

    @property
    def channels(self) -> int:
        """Number of channels (C)."""
        return int(self._data.shape[0])

    @property
    def nframes(self) -> int:
        """Number of frames (N)."""
        return int(self._data.shape[1])

    @property
    def dtype(self):
        """NumPy dtype of the underlying array (usually float32)."""
        return self._data.dtype

    # -------------------- DRY helpers --------------------

    @classmethod
    def _prepare_alloc(
        cls,
        channels: int,
        nframes: int,
        frame_rate: int,
        extent: Extent,
        *,
        quantize_mode: str = "cover",
    ) -> Tuple[int, int, int, Extent]:
        """
        Normalize & validate inputs for buffer allocation.

        Ensures:
            - extent is finite
            - channels >= 1
            - nframes >= 0
            - frame_rate is a positive integer
            - nframes equals quantized extent duration

        Returns:
            (channels, nframes, frame_rate, quantized_extent)

        Raises:
            InvalidChannelsError: if channels < 1.
            InvalidFrameRateError: if frame_rate is non-integer or <= 0.
            ValueError: if extent is not finite, nframes < 0, or duration mismatch.
        """
        if not extent.is_finite():
            raise ValueError("Extent must be finite for allocation.")
        if channels < 1:
            raise InvalidChannelsError("channels must be >= 1")
        if nframes < 0:
            raise ValueError("nframes must be >= 0")
        if not isinstance(frame_rate, (int, np.integer)):
            raise InvalidFrameRateError("frame_rate must be an integer")
        if int(frame_rate) <= 0:
            raise InvalidFrameRateError("frame_rate must be > 0")

        qext = extent.quantize(cls.GRID_STEP, quantize_mode)
        expected = int(qext.duration)
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
        """Allocate and initialize a new FrameBuffer."""
        ch, nf, fr, qext = cls._prepare_alloc(
            channels, nframes, frame_rate, extent, quantize_mode=quantize_mode
        )
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
        quantize_mode: str = "cover",
    ) -> "FrameBuffer":
        """Create a zero-filled FrameBuffer."""
        return cls._new_with_init(
            channels, nframes, frame_rate, extent, quantize_mode=quantize_mode, init="zeros"
        )

    @classmethod
    def empty(
        cls,
        channels: int,
        nframes: int,
        frame_rate: int,
        extent: Extent,
        *,
        quantize_mode: str = "cover",
    ) -> "FrameBuffer":
        """Create an uninitialized FrameBuffer (values are arbitrary)."""
        return cls._new_with_init(
            channels, nframes, frame_rate, extent, quantize_mode=quantize_mode, init="empty"
        )

    # -------------------- Ops --------------------

    def slice_time(self, sub: Extent) -> "FrameBuffer":
        """
        Extract a time-based slice from this FrameBuffer.

        Args:
            sub: Requested extent in absolute frame coordinates.
                 - Infinite bounds are clipped to this buffer's finite extent.
                 - Regions outside the overlap are zero-filled.

        Returns:
            FrameBuffer covering [sub.start, sub.end), with zeros outside the
            overlap and copied samples where the extents overlap. The result may
            be length 0 if the requested window is empty after clipping.
        """
        # --- Step 1: Resolve possibly infinite request into finite start/end
        s_req = sub.start
        e_req = sub.end
        if not math.isfinite(s_req) or not math.isfinite(e_req):
            # Clip infinities to this buffer's own finite extent
            s_req = self._extent.start if not math.isfinite(s_req) else s_req
            e_req = self._extent.end if not math.isfinite(e_req) else e_req

        # --- Step 2: Quantize to integer frame indices (floor mode)
        # Note: We'll construct an Extent with integer bounds so the quantization
        # inside FrameBuffer.__init__ is effectively a no-op.
        qreq = Extent(s_req, e_req).quantize(step=1.0, mode="floor")
        s_req_i, e_req_i = int(qreq.start), int(qreq.end)

        if e_req_i <= s_req_i:
            # Return an empty buffer of the right channel count and frame rate
            return FrameBuffer.zeros(
                self.channels, 0, self.frame_rate, Extent(s_req_i, s_req_i)
            )

        # --- Step 3: Compute overlap with this buffer's finite extent
        ov = self._extent.intersect(Extent(s_req_i, e_req_i))
        out = np.zeros((self.channels, e_req_i - s_req_i), dtype=self.DEFAULT_DTYPE)

        if not ov.is_empty():
            # Source indices relative to this buffer
            src_s = int(ov.start - self._extent.start)
            ov_dur = int(ov.end - ov.start)
            src_e = src_s + ov_dur
            # Destination indices relative to the new slice
            dst_s = int(ov.start - s_req_i)
            dst_e = dst_s + ov_dur
            # Copy overlapping region
            out[:, dst_s:dst_e] = self._data[:, src_s:src_e]

        # Using integer bounds; constructor quantization is a no-op here.
        return FrameBuffer(out, self.frame_rate, Extent(s_req_i, e_req_i))
