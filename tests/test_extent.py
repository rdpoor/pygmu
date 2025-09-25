import unittest

from pygmu import Extent

class TestExtentBasics(unittest.TestCase):
    def test_ctor_defaults_and_str(self):
        e = Extent()
        self.assertTrue(e.is_indefinite())
        self.assertEqual(str(e), "[NINF, PINF)")

    def test_ctor_with_duration_from_start(self):
        e = Extent(start=10, duration=5)
        self.assertEqual(e.start(), 10)
        self.assertEqual(e.end(), 15)
        self.assertAlmostEqual(e.duration(), 5)

    def test_ctor_with_duration_from_end(self):
        e = Extent(end=20, duration=7)
        self.assertEqual(e.start(), 13)
        self.assertEqual(e.end(), 20)
        self.assertAlmostEqual(e.duration(), 7)

    def test_ctor_conflicting_duration_raises(self):
        with self.assertRaises(ValueError):
            Extent(0, 10, duration=11)

    def test_empty_and_point(self):
        e = Extent(5, 5)
        self.assertTrue(e.is_empty())
        self.assertTrue(e.is_point())
        self.assertEqual(e.duration(), 0.0)

    def test_is_finite(self):
        self.assertTrue(Extent(0, 1).is_finite())
        self.assertFalse(Extent(Extent.NINF, 1).is_finite())
        self.assertFalse(Extent(0, Extent.PINF).is_finite())

    def test_offset(self):
        e = Extent(3, 7).offset(10)
        self.assertEqual((e.start(), e.end()), (13, 17))

    def test_with_start_end(self):
        e = Extent(10, 20).with_start(2)
        self.assertEqual((e.start(), e.end()), (2, 20))
        e2 = Extent(10, 20).with_end(25)
        self.assertEqual((e2.start(), e2.end()), (10, 25))

    def test_contains_time(self):
        e = Extent(10, 20)
        self.assertTrue(e.contains_time(10))
        self.assertTrue(e.contains_time(19.999))
        self.assertFalse(e.contains_time(20))
        self.assertFalse(e.contains_time(9.999))


class TestRelations(unittest.TestCase):
    def test_precedes_follows(self):
        a = Extent(0, 10)
        b = Extent(10, 20)
        c = Extent(5, 15)
        self.assertTrue(a.precedes(b))
        self.assertTrue(b.follows(a))
        self.assertFalse(a.precedes(c))
        self.assertFalse(c.follows(a))

    def test_overlaps_spans_equals(self):
        a = Extent(0, 10)
        b = Extent(5, 15)
        c = Extent(2, 8)
        self.assertTrue(a.overlaps(b))
        self.assertTrue(b.overlaps(a))
        self.assertTrue(a.spans(c))
        self.assertFalse(c.spans(a))
        self.assertTrue(Extent(1, 2).equals(Extent(1, 2)))
        self.assertFalse(Extent(1, 2).equals(Extent(1, 3)))

    def test_is_adjacent_and_overlap_length(self):
        a = Extent(0, 10)
        b = Extent(10, 20)
        c = Extent(8, 12)
        self.assertTrue(a.is_adjacent(b))
        self.assertEqual(a.overlap_length(b), 0.0)
        self.assertAlmostEqual(a.overlap_length(c), 2.0)


class TestLogicalOps(unittest.TestCase):
    def test_union_and_union_all(self):
        a = Extent(0, 10)
        b = Extent(5, 20)
        u = a.union(b)
        self.assertEqual((u.start(), u.end()), (0, 20))
        u2 = Extent.union_all([Extent(1, 2), Extent(-1, 0), Extent(1.5, 3)])
        self.assertEqual((u2.start(), u2.end()), (-1, 3))

    def test_intersect_and_intersect_all(self):
        a = Extent(0, 10)
        b = Extent(5, 20)
        i = a.intersect(b)
        self.assertEqual((i.start(), i.end()), (5, 10))
        i2 = Extent.intersect_all([Extent(0, 10), Extent(3, 8), Extent(4, 20)])
        self.assertEqual((i2.start(), i2.end()), (4, 8))
        i3 = Extent(0, 1).intersect(Extent(1, 2))
        self.assertTrue(i3.is_empty())

    def test_clamp_to(self):
        e = Extent(0, 10).clamp_to(Extent(3, 6))
        self.assertEqual((e.start(), e.end()), (3, 6))
        e2 = Extent(0, 2).clamp_to(Extent(3, 4))
        self.assertTrue(e2.is_empty())

    def test_difference(self):
        a = Extent(0, 10)
        b = Extent(3, 7)
        parts = a.difference(b)
        self.assertEqual(len(parts), 2)
        self.assertEqual((parts[0].start(), parts[0].end()), (0, 3))
        self.assertEqual((parts[1].start(), parts[1].end()), (7, 10))
        # Non-overlapping
        self.assertEqual(Extent(0, 5).difference(Extent(6, 7))[0], Extent(0, 5))

    def test_split_at(self):
        e = Extent(0, 10)
        parts = e.split_at([2, 5, 9, -1, 20])  # outside cuts ignored
        self.assertEqual([(p.start(), p.end()) for p in parts],
                         [(0, 2), (2, 5), (5, 9), (9, 10)])

    def test_pad(self):
        e = Extent(10, 20).pad(left=2.5, right=1.0)
        self.assertEqual((e.start(), e.end()), (7.5, 21.0))
        with self.assertRaises(ValueError):
            Extent().pad(1, 1)  # indefinite

    def test_quantize(self):
        e = Extent(1.9, 10.2).quantize(step=1.0, mode="floor")
        self.assertEqual((e.start(), e.end()), (1.0, 10.0))
        e2 = Extent(1.2, 10.8).quantize(step=0.5, mode="ceil")
        self.assertEqual((e2.start(), e2.end()), (1.5, 11.0))
        e3 = Extent(Extent.NINF, 10.3).quantize(1.0)
        self.assertEqual(e3.start(), Extent.NINF)
        self.assertEqual(e3.end(), 10.0)
        with self.assertRaises(ValueError):
            Extent(0, 1).quantize(step=0.0)

    def test_bounded(self):
        e = Extent(Extent.NINF, Extent.PINF).bounded(-100, 200)
        self.assertEqual((e.start(), e.end()), (-100, 200))

    def test_next_prev_edge(self):
        e = Extent(10, 20)
        self.assertEqual(e.next_edge_after(0), 10)
        self.assertEqual(e.next_edge_after(15), 20)
        self.assertIsNone(e.next_edge_after(25))
        self.assertEqual(e.prev_edge_before(25), 20)
        self.assertEqual(e.prev_edge_before(15), 10)
        self.assertIsNone(e.prev_edge_before(5))


class TestCollections(unittest.TestCase):
    def test_find_gaps(self):
        xs = [Extent(0, 5), Extent(7, 10), Extent(12, 14)]
        gaps = Extent.find_gaps(xs)
        self.assertEqual([(g.start(), g.end()) for g in gaps], [(5, 7), (10, 12)])
        # Overlap should raise
        with self.assertRaises(ValueError):
            Extent.find_gaps([Extent(0, 5), Extent(4, 6)])

    def test_merge_adjacent(self):
        xs = [Extent(0, 5), Extent(5, 7), Extent(10, 12), Extent(11, 20)]
        merged = Extent.merge_adjacent(xs, eps=0.0)
        self.assertEqual([(m.start(), m.end()) for m in merged], [(0, 7), (10, 20)])

    def test_total_covered_length(self):
        xs = [Extent(0, 5), Extent(4, 10), Extent(12, 15)]
        self.assertAlmostEqual(Extent.total_covered_length(xs), 10 + 3)  # [0,10) U [12,15) => 13

class TestFactories(unittest.TestCase):
    def test_null_and_infinite(self):
        self.assertTrue(Extent.null().is_empty())
        inf = Extent.infinite()
        self.assertTrue(inf.is_indefinite())
        self.assertFalse(inf.is_finite())


if __name__ == "__main__":
    unittest.main()
