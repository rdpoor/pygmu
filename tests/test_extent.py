# tests/test_extent.py
import unittest

from pygmu import Extent


class TestExtentBasics(unittest.TestCase):
    def test_ctor_and_str(self):
        e = Extent(0, 10)
        self.assertEqual(e.start(), 0)
        self.assertEqual(e.end(), 10)
        self.assertFalse(e.is_indefinite())
        self.assertFalse(e.is_empty())
        self.assertEqual(e.duration(), 10)
        s = str(e)
        self.assertIn("[0,", s)
        self.assertIn(", 10)", s)

    def test_indefinite_ctor_and_duration(self):
        e = Extent(Extent.NINF, 5)
        self.assertTrue(e.is_indefinite())
        self.assertEqual(e.duration(), Extent.INDEFINITE_DURATION)
        e2 = Extent(0, Extent.PINF)
        self.assertTrue(e2.is_indefinite())

    def test_empty_and_null(self):
        e = Extent(5, 5)
        self.assertTrue(e.is_empty())
        self.assertEqual(e.duration(), 0.0)
        self.assertEqual(Extent.null(), Extent(0, 0))

    def test_ctor_with_duration_resolution(self):
        self.assertEqual(Extent(end=10, duration=3), Extent(7, 10))
        self.assertEqual(Extent(start=5, duration=2), Extent(5, 7))
        with self.assertRaises(ValueError):
            _ = Extent(Extent.NINF, Extent.PINF, duration=1)
        with self.assertRaises(ValueError):
            _ = Extent(0, 10, duration=-1)
        with self.assertRaises(ValueError):
            _ = Extent(0, 10, duration=11)  # conflicts with start/end

    def test_type_and_order_validation(self):
        with self.assertRaises(TypeError):
            _ = Extent("a", 5)  # type: ignore
        with self.assertRaises(TypeError):
            _ = Extent(0, 5, duration="x")  # type: ignore
        with self.assertRaises(ValueError):
            _ = Extent(10, 0)

    def test_offset_and_duration_ops(self):
        self.assertEqual(Extent(0, 10).offset(5), Extent(5, 15))

        # set_duration
        self.assertEqual(Extent(0, 10).set_duration(5, anchor="start"), Extent(0, 5))
        self.assertEqual(Extent(0, 10).set_duration(5, anchor="end"), Extent(5, 10))
        self.assertEqual(Extent(0, 10).set_duration(4, anchor="center"), Extent(3, 7))
        with self.assertRaises(ValueError):
            _ = Extent(Extent.NINF, 10).set_duration(1)  # indefinite not allowed
        with self.assertRaises(TypeError):
            _ = Extent(0, 10).set_duration("x")  # type: ignore

        # extend
        # start anchored: start fixed, end moves
        self.assertEqual(Extent(0, 10).extend(-3, anchor="start"), Extent(0, 7))
        # end anchored: end fixed, start moves
        self.assertEqual(Extent(0, 10).extend(-3, anchor="end"), Extent(3, 10))
        # center anchored: center fixed, both ends move symmetrically
        self.assertEqual(Extent(0, 10).extend(+4, anchor="center"), Extent(-2, 12))
        with self.assertRaises(ValueError):
            _ = Extent(0, 10).extend(-11)
        with self.assertRaises(ValueError):
            _ = Extent(Extent.NINF, 10).extend(+1)  # indefinite not allowed
        with self.assertRaises(TypeError):
            _ = Extent(0, 10).extend(None)  # type: ignore

        # stretch
        self.assertEqual(Extent(0, 10).stretch(2.0, anchor="start"), Extent(0, 20))
        self.assertEqual(Extent(0, 10).stretch(0.5, anchor="end"), Extent(5, 10))
        with self.assertRaises(ValueError):
            _ = Extent(0, 10).stretch(0)
        with self.assertRaises(ValueError):
            _ = Extent(Extent.NINF, 10).stretch(2.0)
        with self.assertRaises(TypeError):
            _ = Extent(0, 10).stretch("x")  # type: ignore

    def test_pad(self):
        e = Extent(10, 20).pad(left=2.5, right=1.0)
        self.assertEqual(e, Extent(7.5, 21.0))
        with self.assertRaises(ValueError):
            _ = Extent(10, 20).pad(left=-0.1)
        with self.assertRaises(ValueError):
            _ = Extent(10, 20).pad(right=-0.1)


class TestLogicalRelations(unittest.TestCase):
    def test_relations_with_extents(self):
        a = Extent(0, 10)
        b = Extent(10, 20)
        c = Extent(5, 15)
        self.assertTrue(a.precedes(b))
        self.assertTrue(b.follows(a))
        self.assertFalse(a.overlaps(b))
        self.assertTrue(a.overlaps(c))
        self.assertTrue(b.spans(Extent(12, 13)))
        self.assertFalse(a.spans(b))

    def test_relations_with_scalars(self):
        e = Extent(10, 20)
        self.assertTrue(e.precedes(20))
        self.assertFalse(e.precedes(19))
        self.assertTrue(e.follows(5))
        self.assertFalse(e.follows(19))
        self.assertTrue(e.overlaps(10))
        self.assertTrue(e.overlaps(19.999))
        self.assertFalse(e.overlaps(20))
        self.assertTrue(e.spans(15))
        self.assertFalse(e.spans(25))

    def test_equals_method_typecheck(self):
        self.assertTrue(Extent(0, 1).equals(Extent(0, 1)))
        with self.assertRaises(TypeError):
            _ = Extent(0, 1).equals(123)  # type: ignore


class TestCollections(unittest.TestCase):
    def test_union_and_intersect(self):
        e1 = Extent(0, 5)
        e2 = Extent(3, 7)
        self.assertEqual(e1.union(e2), Extent(0, 7))
        self.assertEqual(e1.intersect(e2), Extent(3, 5))

    def test_union_intersect_all_empty(self):
        self.assertEqual(Extent.union_all([]), Extent.null())
        self.assertEqual(Extent.intersect_all([]), Extent.null())

    def test_find_gaps_sorted_non_overlapping(self):
        xs = [Extent(0, 5), Extent(7, 10), Extent(12, 14)]
        gaps = Extent.find_gaps(xs)
        self.assertEqual(gaps, [Extent(5, 7), Extent(10, 12)])

    def test_find_gaps_overlap_raises(self):
        with self.assertRaises(ValueError):
            _ = Extent.find_gaps([Extent(0, 5), Extent(4, 6)])

    def test_total_covered_length(self):
        xs = [Extent(0, 5), Extent(4, 10), Extent(12, 15)]
        self.assertAlmostEqual(Extent.total_covered_length(xs), 13.0)
        self.assertAlmostEqual(Extent.total_covered_length([]), 0.0)
        self.assertAlmostEqual(Extent.total_covered_length([Extent(1, 4)]), 3.0)


class TestQuantize(unittest.TestCase):
    def test_quantize_floor_and_ceil(self):
        e = Extent(1.9, 10.2).quantize(step=1.0, mode="floor")
        self.assertEqual(e, Extent(1.0, 10.0))
        e2 = Extent(1.2, 10.8).quantize(step=0.5, mode="ceil")
        self.assertEqual(e2, Extent(1.5, 11.0))

    def test_quantize_handles_infinity(self):
        e = Extent(Extent.NINF, 10.3).quantize(step=1.0)
        self.assertEqual(e.start(), Extent.NINF)
        self.assertEqual(e.end(), 10.0)

    def test_quantize_errors(self):
        with self.assertRaises(ValueError):
            _ = Extent(10, 20).quantize(step=0.0)
        with self.assertRaises(ValueError):
            _ = Extent(10, 20).quantize(step=1.0, mode="bogus")


if __name__ == "__main__":
    unittest.main()
