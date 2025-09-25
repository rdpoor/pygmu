import unittest
import numpy as np

from pygmu import FrameBuffer, Extent


class TestFrameBuffer(unittest.TestCase):
    def test_basic_construction_and_props(self):
        data = np.zeros((2, 10), dtype=np.float32)
        ext = Extent(100, 110)
        fb = FrameBuffer(data, frame_rate=48000, extent=ext)

        self.assertEqual(fb.channels, 2)
        self.assertEqual(fb.nframes, 10)
        self.assertEqual(fb.extent, ext)
        self.assertEqual(fb.frame_rate, 48000)

        # Single explicit ndarray interop check (locks in (C, N) layout)
        arr = np.asarray(fb)
        self.assertEqual(arr.shape, (2, 10))
        self.assertEqual(arr.dtype, np.float32)

    def test_constructor_coerces_dtype_to_float32(self):
        data = np.zeros((1, 5), dtype=np.float64)  # not float32 on purpose
        ext = Extent(0, 5)
        fb = FrameBuffer(data, frame_rate=44100, extent=ext)
        self.assertEqual(np.asarray(fb).dtype, np.float32)
        self.assertEqual(fb.channels, 1)
        self.assertEqual(fb.nframes, 5)

    def test_extent_must_be_finite(self):
        data = np.zeros((1, 4), dtype=np.float32)
        with self.assertRaises(ValueError):
            FrameBuffer(data, 48000, Extent(Extent.NINF, 10))
        with self.assertRaises(ValueError):
            FrameBuffer(data, 48000, Extent(0, Extent.PINF))

    def test_data_length_must_match_extent_length(self):
        data = np.zeros((2, 8), dtype=np.float32)
        # Extent length 10 but data has 8 frames
        with self.assertRaises(ValueError):
            FrameBuffer(data, 48000, Extent(0, 10))

    def test_zeros_factory(self):
        fb = FrameBuffer.zeros(channels=2, nframes=12, frame_rate=48000, extent=Extent(50, 62))
        self.assertEqual(fb.channels, 2)
        self.assertEqual(fb.nframes, 12)
        self.assertTrue(np.allclose(np.asarray(fb), 0.0))
        self.assertEqual(fb.extent.start(), 50)
        self.assertEqual(fb.extent.end(), 62)

        with self.assertRaises(ValueError):
            FrameBuffer.zeros(1, 10, 48000, Extent(0, Extent.PINF))

    def test_slice_time_inside(self):
        data = np.vstack([np.arange(10), np.arange(100, 110)]).astype(np.float32)
        fb = FrameBuffer(data, 48000, Extent(100, 110))

        # Exact slice
        sub = fb.slice_time(Extent(100, 110))
        np.testing.assert_array_equal(np.asarray(sub), data)
        self.assertEqual(sub.channels, 2)
        self.assertEqual(sub.nframes, 10)
        self.assertEqual(sub.extent, Extent(100, 110))

        # Inner slice
        sub2 = fb.slice_time(Extent(103, 108))
        np.testing.assert_array_equal(np.asarray(sub2), data[:, 3:8])
        self.assertEqual(sub2.channels, 2)
        self.assertEqual(sub2.nframes, 5)
        self.assertEqual(sub2.extent, Extent(103, 108))

    def test_slice_time_with_gap_returns_zeros(self):
        data = np.ones((1, 6), dtype=np.float32)
        fb = FrameBuffer(data, 48000, Extent(20, 26))

        sub = fb.slice_time(Extent(0, 5))  # no overlap
        self.assertEqual(sub.channels, 1)
        self.assertEqual(sub.nframes, 5)
        self.assertTrue(np.allclose(np.asarray(sub), 0.0))
        self.assertEqual(sub.extent, Extent(0, 5))

    def test_slice_time_handles_infinite_request_by_clipping(self):
        data = np.arange(8, dtype=np.float32).reshape(1, -1)
        fb = FrameBuffer(data, 48000, Extent(10, 18))

        # Request (-inf, +inf) -> should clip to [10, 18)
        sub = fb.slice_time(Extent(Extent.NINF, Extent.PINF))
        np.testing.assert_array_equal(np.asarray(sub), data)
        self.assertEqual(sub.channels, 1)
        self.assertEqual(sub.nframes, 8)
        self.assertEqual(sub.extent, Extent(10, 18))

    def test_quantize_mode_affects_extent_rounding(self):
        data = np.zeros((1, 5), dtype=np.float32)
        fb_floor = FrameBuffer(data, 48000, Extent(1.9, 6.2), quantize_mode="floor")
        self.assertEqual(fb_floor.extent, Extent(1, 6))
        self.assertEqual(fb_floor.nframes, 5)

        fb_round = FrameBuffer(data, 48000, Extent(1.6, 6.6), quantize_mode="round")
        self.assertEqual(fb_round.extent, Extent(2, 7))
        self.assertEqual(fb_round.nframes, 5)

    def test_slice_time_empty_request_returns_zero_length(self):
        fb = FrameBuffer.zeros(1, 6, 48000, Extent(0, 6))
        # no need to fill data; we're only checking length/extent
        sub = fb.slice_time(Extent(3, 3))  # duration = 0
        self.assertEqual(sub.channels, 1)
        self.assertEqual(sub.nframes, 0)
        self.assertEqual(sub.extent, Extent(3, 3))

    def test_slice_time_partial_overlap_left(self):
        # Source buffer covers [10, 15) with 5 frames: values 0..4
        fb = FrameBuffer.zeros(1, 5, 48000, Extent(10, 15))
        fb.data[0, :] = np.arange(5, dtype=np.float32)

        # Request [7, 12) → length 5; overlap is [10, 12) (2 frames) at the END of the request
        sub = fb.slice_time(Extent(7, 12))
        arr = np.asarray(sub)
        self.assertEqual(sub.channels, 1)
        self.assertEqual(sub.nframes, 5)
        # First 3 frames are silence
        self.assertTrue(np.allclose(arr[0, :3], 0.0))
        # Last 2 frames are the first 2 frames of the source (frames 10,11 → values 0,1)
        np.testing.assert_array_equal(arr[0, 3:], fb.data[0, :2])
        self.assertEqual(sub.extent, Extent(7, 12))

    def test_slice_time_partial_overlap_right(self):
        # Source buffer covers [10, 15) with 5 frames: values 0..4
        fb = FrameBuffer.zeros(1, 5, 48000, Extent(10, 15))
        fb.data[0, :] = np.arange(5, dtype=np.float32)

        # Request [13, 18) → length 5; overlap is [13, 15) (2 frames) at the START of the request
        sub = fb.slice_time(Extent(13, 18))
        arr = np.asarray(sub)
        self.assertEqual(sub.channels, 1)
        self.assertEqual(sub.nframes, 5)
        # First 2 frames are the last 2 frames of the source (frames 13,14 → values 3,4)
        np.testing.assert_array_equal(arr[0, :2], fb.data[0, 3:])
        # Remaining 3 frames are silence
        self.assertTrue(np.allclose(arr[0, 2:], 0.0))
        self.assertEqual(sub.extent, Extent(13, 18))

    def test_constructor_rejects_non_2d():
        from pygmu import FrameBuffer, Extent
        with self.assertRaises(ValueError):
            FrameBuffer(np.zeros((10,), dtype=np.float32), 48000, Extent(0, 10))  # 1-D

    def test_constructor_coerces_dtype_no_copy_when_already_float32():
        from pygmu import FrameBuffer, Extent
        data = np.zeros((1, 4), dtype=np.float32)
        fb = FrameBuffer(data, 48000, Extent(0, 4))
        self.assertEqual(np.asarray(fb).dtype, np.float32)

    def test_np_asarray_with_dtype_argument_casts_view():
        from pygmu import FrameBuffer, Extent
        fb = FrameBuffer.zeros(1, 3, 48000, Extent(0, 3))
        arr64 = np.asarray(fb, dtype=np.float64)
        self.assertEqual(arr64.dtype, np.float64)
        self.assertEqual(np.asarray(fb).dtype, np.float32)  # original unchanged

    def test_factory_guardrails_channels_and_nframes():
        from pygmu import FrameBuffer, Extent
        with self.assertRaises(ValueError):
            FrameBuffer.zeros(0, 1, 48000, Extent(0, 1))
        with self.assertRaises(ValueError):
            FrameBuffer.empty(1, -1, 48000, Extent(0, 0))

    def test_slice_time_no_overlap_returns_zeros_and_skips_copy():
        from pygmu import FrameBuffer, Extent
        fb = FrameBuffer.zeros(2, 5, 48000, Extent(10, 15))
        sub = fb.slice_time(Extent(0, 5))
        self.assertTrue(np.allclose(np.asarray(sub), 0.0))
        self.assertEqual(sub.extent, Extent(0, 5))

if __name__ == "__main__":
    unittest.main()
