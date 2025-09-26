# src/pygmu/base_transport.py
from __future__ import annotations
from typing import Optional, Callable
import numpy as np

from .extent import Extent
from .processing_element import ProcessingElement
from .validation import STRICT, validate_framebuffer

# Callable sink signature: (channels x frames array, frame_rate)
Sink = Callable[[np.ndarray, int], None]


class BaseTransport:
    """
    Pull-based transport: repeatedly requests blocks from the root PE and
    pushes them to a sink. Designed to be subclassed (e.g., for real-time or
    offline use). This base class performs no sleeping; it just advances.
    """

    def __init__(self, root: ProcessingElement, *, block_size: int = 65536):
        if not isinstance(block_size, int) or block_size <= 0:
            raise ValueError("block_size must be a positive integer")
        self.root = root
        self.block_size = block_size

    def render(self, start: int, end: Optional[int], sink: Sink) -> None:
        """
        Render from [start, end). If end is None, attempt to infer from
        root.content_extent(); if unavailable/indefinite, raise ValueError.

        Safety guards:
          - If a PE returns 0 frames for a non-empty request, raise RuntimeError
            to avoid infinite loops.
          - If a PE returns fewer frames than requested, advance by what we got.
        """
        fr = int(self.root.frame_rate())

        # Resolve end
        if end is None:
            # Try to infer from content extent
            ce = getattr(self.root, "content_extent", lambda: None)()
            if ce is None or not ce.is_finite():
                raise ValueError("end is None and content extent is unknown/indefinite")
            end = int(ce.end())

        cur = int(start)
        final = int(end)
        if final < cur:
            # Empty request -> nothing to send
            return

        while cur < final:
            req_end = min(cur + self.block_size, final)
            fb = self.root.render(Extent(cur, req_end))
            arr = np.asarray(fb)

            if arr.ndim != 2:
                raise TypeError("ProcessingElement.render must return 2-D (C, N) data")

            got = int(arr.shape[1])

            # ---- SAFETY GUARD: prevent infinite loop on 0-length output
            if got == 0 and req_end > cur:
                raise RuntimeError(
                    f"ProcessingElement.render returned 0 frames for non-empty request [{cur},{req_end})"
                )
            # -------------------------------------------------------------

            sink(arr, fr)

            # If PE returns fewer than requested, advance by what we got.
            # This still guarantees forward progress and eventual termination.
            cur += got if got > 0 else (req_end - cur)
