# src/pygmu/validation.py
from __future__ import annotations

import os
from typing import Optional, Protocol

import numpy as np
from numpy.typing import NDArray

from .extent import Extent
from .frame_buffer import FrameBuffer
from .exceptions import ContractViolationError


class _HasPEInterface(Protocol):
    """
    Minimal protocol for the ProcessingElement methods that validation relies on.
    This avoids a hard import on ProcessingElement and circular imports.
    """
    def frame_rate(self) -> int: ...
    def channels(self) -> int: ...


def strict_mode_enabled() -> bool:
    """
    Returns True iff strict validation is enabled via the PYGMU_STRICT env var.

    Accepted "falsey" values (case-insensitive): "", "0", "false", "no"
    Any other value enables strict mode.
    """
    v = os.environ.get("PYGMU_STRICT", "")
    return v not in ("", "0", "false", "False", "no", "No")

# ---------------------------------------------------------------------------

def _err(msg: str) -> None:
    """Internal helper to raise the standard contract violation."""
    raise ContractViolationError(msg)


def validate_render_output(
    pe: _HasPEInterface,
    fb: FrameBuffer,
    requested: Extent,
) -> None:
    """
    Lightweight validator for a PE's render() result relative to a request.

    This function is intended for call-sites where you already know `fb` is a
    FrameBuffer (e.g., after type-safe construction). It focuses on *contract*
    relations between the request, the PE’s declared interface, and the
    FrameBuffer’s header-level fields.

    Checks performed (only when strict_mode_enabled() is True):
      1) fb is a FrameBuffer (type check).
      2) fb.extent is finite.
      3) fb.extent is contained within the requested window (subset allowed).
      4) fb.frame_rate == pe.frame_rate().
      5) fb.channels   == pe.channels().

    Raises:
        ContractViolationError: if any invariant is violated in strict mode.
    """
    if not strict_mode_enabled():
        return

    # 1) Type
    if not isinstance(fb, FrameBuffer):
        _err(f"{pe.__class__.__name__}.render() must return FrameBuffer, got {type(fb)}")

    # 2) Finite extent
    if not isinstance(fb.extent, Extent) or not fb.extent.is_finite():
        _err(f"{pe.__class__.__name__} returned non-finite extent: {fb.extent!r}")

    # 3) Containment: produced frames may be fewer than requested,
    #    but must not extend outside the request.
    if fb.extent.start < requested.start or fb.extent.end > requested.end:
        _err(
            f"{pe.__class__.__name__} returned extent {fb.extent} outside request {requested}"
        )

    # 4) Frame rate match
    try:
        pe_fr = pe.frame_rate()
    except Exception:
        pe_fr = None
    if pe_fr is not None and fb.frame_rate != pe_fr:
        _err(
            f"{pe.__class__.__name__} frame rate mismatch: fb={fb.frame_rate}, pe={pe_fr}"
        )

    # 5) Channel count match
    try:
        pe_ch = pe.channels()
    except Exception:
        pe_ch = None
    if pe_ch is not None and fb.channels != pe_ch:
        _err(
            f"{pe.__class__.__name__} channels mismatch: fb={fb.channels}, pe={pe_ch}"
        )


def validate_framebuffer(
    *,
    pe: _HasPEInterface,
    fb: FrameBuffer,
    requested: Extent,
) -> None:
    """
    Comprehensive validator for a FrameBuffer produced by a ProcessingElement.

    Use this in strict contexts (e.g., transports or unit tests) to assert the
    full set of invariants, including array shape/dtype and internal header
    consistency. This function does *not* gate on strict_mode_enabled(); call
    sites should decide when to invoke it. For convenience in existing code,
    you may guard it with `if STRICT:` or `if strict_mode_enabled():`.

    Checks performed:
      - ndarray is 2-D (C, N) and dtype float32
      - fb.channels == array.shape[0]
      - fb.nframes  == array.shape[1]
      - fb.extent is finite
      - int(fb.extent.duration) == fb.nframes
      - fb.extent is contained within the requested window (subset allowed)
      - fb.frame_rate == pe.frame_rate()
      - fb.channels   == pe.channels()

    Raises:
        ContractViolationError: if any invariant is violated.
    """
    arr: NDArray[np.float32] = np.asarray(fb)

    # Shape / dtype
    if arr.ndim != 2:
        _err("render() must return 2-D (channels, nframes) array")
    if arr.dtype != np.float32:
        _err(f"render() must return float32 data, got {arr.dtype}")

    # Channel / frame counts
    ch, nf = arr.shape
    if fb.channels != ch:
        _err(f"channels mismatch: fb.channels={fb.channels} vs data={ch}")
    if fb.nframes != nf:
        _err(f"nframes mismatch: fb.nframes={fb.nframes} vs data={nf}")

    # Extent consistency
    if not fb.extent.is_finite():
        _err("fb.extent must be finite")

    # We quantize Extent elsewhere to frame grid; use int() equality here.
    if int(fb.extent.duration) != nf:
        _err(f"extent duration {fb.extent.duration} != nframes {nf}")

    # Produced region must be within the requested window (subset allowed)
    if fb.extent.start < requested.start or fb.extent.end > requested.end:
        _err(f"fb.extent {fb.extent} is outside requested {requested}")

    # PE contract parameters
    if fb.frame_rate != pe.frame_rate():
        _err(f"frame_rate mismatch: fb={fb.frame_rate} vs pe={pe.frame_rate()}")
    if fb.channels != pe.channels():
        _err(f"channel mismatch: fb={fb.channels} vs pe={pe.channels()}")
