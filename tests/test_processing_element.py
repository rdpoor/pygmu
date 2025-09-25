import unittest
import numpy as np

from pygmu import Extent, FrameBuffer, ProcessingElement


class TestProcessingElementABC(unittest.TestCase):
    def test_cannot_instantiate_base(self):
        # ABC should not be instantiable without implementing abstract methods
        with self.assertRaises(TypeError):
            _ = ProcessingElement()  # type: ignore[abstract]


class SilencePE(ProcessingElement):
    """Minimal concrete PE for testing: returns zeros for the requested extent."""
    def __init__(self, frame_rate=48000, channels=2):
        self._fr = int(frame_rate)
        self._ch = int(channels)

    def frame_rate(self) -> int:
        return self._fr

    def channels(self) -> int:
        return self._ch

    def render(self, extent: Extent) -> FrameBuffer:
        s = int(extent.start())
        e = int(extent.end())
        n = max(0, e - s)
        return FrameBuffer.zeros(self._ch, n, self._fr, Extent(s, e))
    # Note: we intentionally do NOT override content_extent() or latency()
    # to test the base defaults (None, 0).


class TestProcessingElementContract(unittest.TestCase):
    def test_defaults_from_base_helpers(self):
        pe = SilencePE()
        self.assertIsNone(pe.content_extent())  # default from base
        self.assertEqual(pe.latency(), 0)       # default from base

    def test_render_returns_framebuffer(self):
        pe = SilencePE(frame_rate=44100, channels=1)
        req = Extent(100, 110)
        fb = pe.render(req)

        self.assertIsInstance(fb, FrameBuffer)
        self.assertEqual(fb.frame_rate, 44100)
        self.assertEqual(fb.channels, 1)
        self.assertEqual(fb.nframes, 10)
        self.assertEqual(fb.extent, req)

        arr = np.asarray(fb)
        self.assertEqual(arr.shape, (1, 10))
        self.assertTrue(np.allclose(arr, 0.0))
        self.assertEqual(arr.dtype, np.float32)

    def test_multiple_channels_and_empty_request(self):
        pe = SilencePE(frame_rate=48000, channels=2)
        req = Extent(0, 0)  # empty request
        fb = pe.render(req)

        self.assertEqual(fb.channels, 2)
        self.assertEqual(fb.nframes, 0)

        # Non-empty request
        req2 = Extent(5, 25)
        fb2 = pe.render(req2)
        self.assertEqual(fb2.channels, 2)
        self.assertEqual(fb2.nframes, 20)


if __name__ == "__main__":
    unittest.main()
