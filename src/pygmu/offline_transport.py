# src/pygmu/offline_transport.py
from __future__ import annotations
from typing import Optional, List, Callable
import numpy as np
from .extent import Extent
from .base_transport import BaseTransport
from .processing_element import ProcessingElement
from .validation import STRICT, validate_framebuffer

# A sink consumes chunks of audio: (channels, frames), frame_rate
Sink = Callable[[np.ndarray, int], None]


class OfflineTransport(BaseTransport):
    """
    Optimized for offline (non-realtime) rendering.
    Contract: pull as quickly as possible.

    - Single-shot render when full extent is known (fewer graph traversals).
    - Convenience helpers to get one big array or collect blocks.
    """

    def __init__(
        self,
        root: ProcessingElement,
        *,
        block_size: int = 262144,
        try_single_shot: bool = True,
    ):
        """
        try_single_shot=True attempts one large render when 'end' is known.
        Larger default block_size than BaseTransport to reduce overhead.
        """
        super().__init__(root, block_size=block_size)
        self.try_single_shot = bool(try_single_shot)

    def render(self, start: int, end: Optional[int], sink: Sink) -> None:
        """
        If end is provided (finite) and try_single_shot is True, do a single
        render; else fall back to the fast block loop from BaseTransport.
        """
        if end is not None and self.try_single_shot:
            fr = self.root.frame_rate()
            req = Extent(int(start), int(end))
            fb = self.root.render(req)
            if STRICT:
                validate_framebuffer(pe=self.root, fb=fb, requested=req)
            sink(np.asarray(fb), fr)
            return

        # Unknown end or single-shot disabled: block loop (no sleeps).
        super().render(start, end, sink)

    # -------- Convenience helpers --------

    def render_to_blocks(self, start: int, end: int) -> List[np.ndarray]:
        """Render [start, end) and return a list of (C, N_i) blocks."""
        blocks: List[np.ndarray] = []

        def _collect(arr: np.ndarray, _: int) -> None:
            blocks.append(arr)

        self.render(start, end, _collect)
        return blocks

    def render_to_array(self, start: int, end: Optional[int] = None) -> np.ndarray:
        """
        Render to a single ndarray (C, N). If 'end' is None, tries to infer it
        from root.content_extent(); raises if still unknown/indefinite.
        """
        if end is None:
            ce = self.root.content_extent()
            if ce is None or not ce.is_finite():
                raise ValueError("end is None and content extent is unknown/indefinite")
            start = int(start)
            end = int(ce.end()) if start <= ce.end() else start

        if self.try_single_shot:
            fb = self.root.render(Extent(int(start), int(end)))
            return np.asarray(fb)

        blocks = self.render_to_blocks(int(start), int(end))
        if not blocks:
            return np.zeros((self.root.channels(), 0), dtype=np.float32)
        return np.concatenate(blocks, axis=1)

    def test_base_transport_rejects_non_positive_block_size():
        from pygmu import BaseTransport, ProcessingElement, Extent, FrameBuffer
        class P(ProcessingElement):
            def frame_rate(self): return 48000
            def channels(self): return 1
            def render(self, ex): return FrameBuffer.zeros(1, int(ex.duration()), 48000, ex)
        with self.assertRaises(ValueError):
            _ = BaseTransport(P(), block_size=0)
        with self.assertRaises(ValueError):
            _ = BaseTransport(P(), block_size=-128)

    def test_base_transport_end_none_and_unknown_content_extent_raises():
        from pygmu import BaseTransport, ProcessingElement
        class P(ProcessingElement):
            def frame_rate(self): return 48000
            def channels(self): return 1
            def content_extent(self): return None  # unknown
            def render(self, ex): raise AssertionError("should not render")
        t = BaseTransport(P(), block_size=256)
        with self.assertRaises(ValueError):
            t.render(0, None, lambda arr, fr: None)

    def test_offline_transport_single_shot_calls_sink_once():
        from pygmu import OfflineTransport, ProcessingElement, Extent, FrameBuffer
        class P(ProcessingElement):
            def frame_rate(self): return 48000
            def channels(self): return 2
            def render(self, ex): return FrameBuffer.zeros(2, int(ex.duration()), 48000, ex)
        root = P()
        t = OfflineTransport(root, try_single_shot=True)
        calls = []
        t.render(100, 200, lambda arr, fr: calls.append((arr.shape, fr)))
        assert calls == [((2, 100), 48000)]

    def test_offline_transport_render_to_array_empty_range():
        from pygmu import OfflineTransport, ProcessingElement, Extent, FrameBuffer
        class P(ProcessingElement):
            def frame_rate(self): return 48000
            def channels(self): return 1
            def render(self, ex): return FrameBuffer.zeros(1, int(ex.duration()), 48000, ex)
        t = OfflineTransport(P(), try_single_shot=False, block_size=256)
        out = t.render_to_array(1000, 1000)
        assert out.shape == (1, 0)
