# tests/test_offline_transport.py
import unittest
import numpy as np

from pygmu import Extent, FrameBuffer, ProcessingElement, BaseTransport, OfflineTransport


# --------- Test doubles ---------

class SilentPE(ProcessingElement):
    """Produces silence with known frame_rate/channels; content extent configurable."""
    def __init__(self, frame_rate=48000, channels=1, content: Extent | None = None):
        self._fr = frame_rate
        self._ch = channels
        self._content = content

    def frame_rate(self) -> int:
        return self._fr

    def channels(self) -> int:
        return self._ch

    def content_extent(self) -> Extent | None:
        return self._content

    def render(self, extent: Extent) -> FrameBuffer:
        n = max(0, int(extent.duration()))
        return FrameBuffer.zeros(self._ch, n, self._fr, extent)


class CountingPE(ProcessingElement):
    """Emits per-channel increasing integers (useful to validate concatenation order)."""
    def __init__(self, frame_rate=44100, channels=2, content: Extent | None = None):
        self._fr = frame_rate
        self._ch = channels
        self._content = content

    def frame_rate(self) -> int:
        return self._fr

    def channels(self) -> int:
        return self._ch

    def content_extent(self) -> Extent | None:
        return self._content

    def render(self, extent: Extent) -> FrameBuffer:
        n = max(0, int(extent.duration()))
        start = int(extent.start())
        # absolute sequence: start, start+1, ..., start+n-1
        row = np.arange(start, start + n, dtype=np.float32)
        data = np.vstack([row for _ in range(self._ch)])
        return FrameBuffer(data, self._fr, extent)

# --------- Tests ---------

class TestBaseTransport(unittest.TestCase):
    def test_rejects_non_positive_block_size(self):
        pe = SilentPE()
        with self.assertRaises(ValueError):
            _ = BaseTransport(pe, block_size=0)
        with self.assertRaises(ValueError):
            _ = BaseTransport(pe, block_size=-128)

    def test_end_none_and_unknown_content_extent_raises(self):
        class UnknownExtentPE(SilentPE):
            def content_extent(self):  # override to ensure None
                return None

        t = BaseTransport(UnknownExtentPE(), block_size=256)
        with self.assertRaises(ValueError):
            t.render(0, None, lambda arr, fr: None)

    def test_block_loop_calls_sink_multiple_times(self):
        # Small block_size forces multiple sink calls.
        pe = CountingPE(frame_rate=48000, channels=2)
        t = BaseTransport(pe, block_size=5)
        calls = []

        def sink(arr: np.ndarray, fr: int) -> None:
            calls.append((arr.shape, fr, arr.copy()))

        t.render(10, 23, sink)  # length = 13; blocks -> 5,5,3
        self.assertEqual([c[0] for c in calls], [ (2, 5), (2, 5), (2, 3) ])
        self.assertTrue(all(fr == 48000 for _, fr, _ in calls))
        # Check first block content is 0..4 relative to its requested slice
        np.testing.assert_array_equal(
            calls[0][2],
            np.vstack([np.arange(10, 15), np.arange(10, 15)]).astype(np.float32))


class TestOfflineTransport(unittest.TestCase):
    def test_single_shot_calls_sink_once(self):
        root = SilentPE(frame_rate=48000, channels=2)
        t = OfflineTransport(root, try_single_shot=True)
        calls = []
        t.render(100, 200, lambda arr, fr: calls.append((arr.shape, fr)))
        self.assertEqual(calls, [((2, 100), 48000)])

    def test_fallback_to_block_loop_when_single_shot_disabled(self):
        root = CountingPE(frame_rate=44100, channels=1)
        t = OfflineTransport(root, try_single_shot=False, block_size=4)
        sizes = []
        t.render(0, 10, lambda arr, fr: sizes.append(arr.shape[1]))
        self.assertEqual(sizes, [4, 4, 2])

    def test_render_to_blocks_collects_all(self):
        root = CountingPE(frame_rate=48000, channels=1)
        t = OfflineTransport(root, try_single_shot=False, block_size=6)
        blocks = t.render_to_blocks(0, 15)  # 6 + 6 + 3
        self.assertEqual([b.shape for b in blocks], [(1, 6), (1, 6), (1, 3)])
        # Verify last block content continuity (starts at 12)
        np.testing.assert_array_equal(blocks[-1], np.arange(12, 15, dtype=np.float32).reshape(1, -1))

    def test_render_to_array_single_shot_path(self):
        root = CountingPE(frame_rate=48000, channels=2)
        t = OfflineTransport(root, try_single_shot=True)
        out = t.render_to_array(10, 20)
        self.assertEqual(out.shape, (2, 10))
        # Channel 0 is 0..9, channel 1 same pattern
        np.testing.assert_array_equal(out[0], np.arange(10, 20, dtype=np.float32))
        np.testing.assert_array_equal(out[1], np.arange(10, 20, dtype=np.float32))

    def test_render_to_array_block_concat_path(self):
        root = CountingPE(frame_rate=48000, channels=1)
        t = OfflineTransport(root, try_single_shot=False, block_size=4)
        out = t.render_to_array(5, 13)  # 8 frames
        self.assertEqual(out.shape, (1, 8))
        np.testing.assert_array_equal(out, np.arange(5, 13, dtype=np.float32).reshape(1, -1))

    def test_render_to_array_infers_end_from_content_extent(self):
        # content_extent says audio exists until 250
        root = CountingPE(frame_rate=48000, channels=1, content=Extent(0, 250))
        t = OfflineTransport(root, try_single_shot=True)
        out = t.render_to_array(100, end=None)  # infer end from content extent
        self.assertEqual(out.shape, (1, 150))
        np.testing.assert_array_equal(
            out, np.arange(100, 250, dtype=np.float32).reshape(1, -1))

    def test_render_to_array_end_none_but_unknown_extent_raises(self):
        root = SilentPE(frame_rate=48000, channels=1, content=None)
        t = OfflineTransport(root, try_single_shot=True)
        with self.assertRaises(ValueError):
            _ = t.render_to_array(0, end=None)

    def test_render_to_array_empty_range_returns_empty_array(self):
        root = SilentPE(frame_rate=48000, channels=1)
        t = OfflineTransport(root, try_single_shot=False, block_size=8)
        out = t.render_to_array(1000, 1000)
        self.assertEqual(out.shape, (1, 0))


if __name__ == "__main__":
    unittest.main()
