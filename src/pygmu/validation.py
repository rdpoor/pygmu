# src/pygmu/validation.py
from __future__ import annotations
import os
import numpy as np
from .extent import Extent
from .frame_buffer import FrameBuffer
from .exceptions import ContractViolationError

STRICT = os.getenv("PYGMU_STRICT", "0") not in ("", "0", "false", "False", "no", "No")


def validate_framebuffer(
    *,
    pe,                        # ProcessingElement
    fb: FrameBuffer,
    requested: Extent,         # the extent we asked the PE to render
) -> None:
    """
    Validate basic contract invariants for a FrameBuffer produced by a PE.
    Raises ContractViolationError if anything is off.

    Rules (kept practical and non-overbearing):
      - ndarray is 2D (C, N) and dtype float32
      - fb.channels == array.shape[0]
      - fb.nframes == array.shape[1]
      - fb.extent is finite and fb.nframes == fb.extent.duration()
      - fb.frame_rate == pe.frame_rate()
      - fb.channels    == pe.channels()
      - fb.extent lies within the requested extent (subset is allowed)
    """
    arr = np.asarray(fb)

    # Shape / dtype
    if arr.ndim != 2:
        raise ContractViolationError("render() must return 2-D (channels, nframes) array")
    if arr.dtype != np.float32:
        raise ContractViolationError(f"render() must return float32 data, got {arr.dtype}")

    # Channel / frame counts
    ch, nf = arr.shape
    if fb.channels != ch:
        raise ContractViolationError(f"channels mismatch: fb.channels={fb.channels} vs data={ch}")
    if fb.nframes != nf:
        raise ContractViolationError(f"nframes mismatch: fb.nframes={fb.nframes} vs data={nf}")

    # Extent consistency
    if not fb.extent.is_finite():
        raise ContractViolationError("fb.extent must be finite")
    if int(fb.extent.duration()) != nf:
        raise ContractViolationError(
            f"extent duration {fb.extent.duration()} != nframes {nf}"
        )
    # Must be within the requested window (subset allowed)
    if not requested.spans(fb.extent):
        raise ContractViolationError(
            f"fb.extent {fb.extent} is outside requested {requested}"
        )

    # PE contract parameters
    if fb.frame_rate != pe.frame_rate():
        raise ContractViolationError(
            f"frame_rate mismatch: fb={fb.frame_rate} vs pe={pe.frame_rate()}"
        )
    if fb.channels != pe.channels():
        raise ContractViolationError(
            f"channel mismatch: fb={fb.channels} vs pe={pe.channels()}"
        )
