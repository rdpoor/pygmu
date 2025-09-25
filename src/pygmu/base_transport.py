# src/pygmu/base_transport.py
from __future__ import annotations
from typing import Callable, Optional
import numpy as np
from .extent import Extent
from .processing_element import ProcessingElement

class BaseTransport:
    """
    Pulls audio from a root ProcessingElement in fixed-size blocks and
    forwards raw float32 arrays (C, N) to a sink callable.

    The sink signature is: sink(array: np.ndarray, frame_rate: int) -> None
    """

    def __init__(self, root: ProcessingElement, *, block_size: int = 65536):
        if block_size <= 0:
            raise ValueError("block_size must be > 0")
        self.root = root
        self.block = int(block_size)

    def render(self, start: int, end: Optional[int], sink: Callable[[np.ndarray, int], None]) -> None:
        """
        Render from start to end (end may be None for 'until stopped' use cases).
        """
        t = int(start)
        fr = self.root.frame_rate()
        while end is None or t < end:
            e = t + self.block if end is None else min(t + self.block, end)
            fb = self.root.render(Extent(t, e))
            arr = np.asarray(fb)  # (C, N)
            if arr.size == 0:
                if end is not None and e >= end:
                    break
                t = e
                continue
            sink(arr, fr)
            t = fb.extent.end()
            if end is not None and t >= end:
                break
