import unittest
import numpy as np

from pygmu import Extent, FrameBuffer, ProcessingElement
from pygmu import OfflineTransport, BaseTransport


class RampPE(ProcessingElement):
    """
    Simple PE that outputs a ramp per channel over the requested extent.
    channels=2 -> ch0: range, ch1: range + 1000.  Declares finite content extent.
    """
    def __init__(self, frame_rate=48000, channels=2, total_frames=48000):
        self._fr = frame_rate
        self._ch = channels
        self._total = int(total_frames)

    def frame_rate(self) -> int:
        return self._fr

    def channels(self) -> int:
        return self._ch

    def content_extent(self):
        return Extent(0, self._total)

    def render(self, extent: Extent) -> FrameBuffer:
        # Ensure integer frame indices
        s = int(extent.start())
        e = int(extent.end())
        n = max(0, e - s)
        if n == 0:
            return FrameBuffer(np.zeros((self._ch, 0), np.float32), self._fr, Extent(s, s))
        base = np.arange(s, e, dtype=np.float32).reshape(1, -1)
        data = np.vstack([base + 1000 * c for c in range(self._ch)]).astype(np.float32)
        return FrameBuffer(data, self._fr, Extent(s, e))


class TestOfflineTransport(unittest.TestCase):
    def test_single_shot_render_to_array(self):
        root = RampPE(total_frames=1000)
        t = OfflineTransport(root, try_single_shot=True)

        arr = t.render_to_array(0, 1000)  # (C, N)
        self.assertEqual(arr.shape, (root.channels(), 1000))
        # spot check values
        self.assertEqual(arr[0, 0], 0.0)
        self.assertEqual(arr[0, -1], 999.0)
        self.assertEqual(arr[1, 0], 1000.0)

    def test_block_loop_when_single_shot_disabled(self):
        root = RampPE(total_frames=3000)
        t = OfflineTransport(root, block_size=512, try_single_shot=False)

        arr = t.render_to_array(0, 1500)
        self.assertEqual(arr.shape, (root.channels(), 1500))
        self.assertEqual(arr[0, 0], 0.0)
        self.assertEqual(arr[0, 1499], 1499.0)

    def test_render_to_blocks_collects_multiple_chunks(self):
        root = RampPE(total_frames=4096)
        t = OfflineTransport(root, block_size=1000, try_single_shot=False)
        blocks = t.render_to_blocks(0, 2500)

        self.assertGreater(len(blocks), 1)
        self.assertEqual(sum(b.shape[1] for b in blocks), 2500)
        self.assertTrue(all(b.shape[0] == root.channels() for b in blocks))

    def test_render_sink_callback(self):
        root = RampPE(total_frames=2000)
        t = OfflineTransport(root, block_size=700, try_single_shot=False)
        seen = []

        def sink(arr: np.ndarray, rate: int):
            seen.append((arr.shape, rate))

        t.render(0, 2000, sink)
        # Expect 3 calls: 700 + 700 + 600
        self.assertEqual(len(seen), 3)
        self.assertEqual(seen[0][0], (root.channels(), 700))
        self.assertEqual(seen[-1][0], (root.channels(), 600))
        self.assertEqual(seen[0][1], root.frame_rate())

    def test_infer_end_from_content_extent(self):
        root = RampPE(total_frames=1234)
        t = OfflineTransport(root, try_single_shot=True)
        arr = t.render_to_array(0)  # infer end from content_extent()
        self.assertEqual(arr.shape, (root.channels(), 1234))

    def test_infer_end_raises_when_content_extent_unknown(self):
        class UnknownExtentPE(RampPE):
            def content_extent(self):
                return None

        root = UnknownExtentPE(total_frames=1000)
        t = OfflineTransport(root)
        with self.assertRaises(ValueError):
            _ = t.render_to_array(0)  # no end and unknown content extent

    def test_base_transport_blocking_behavior(self):
        root = RampPE(total_frames=1800)
        t = BaseTransport(root, block_size=512)
        totals = 0

        def sink(arr: np.ndarray, rate: int):
            nonlocal totals
            totals += arr.shape[1]
            self.assertEqual(rate, root.frame_rate())

        t.render(0, 1500, sink)
        self.assertEqual(totals, 1500)


if __name__ == "__main__":
    unittest.main()
