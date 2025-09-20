import unittest
import sys
import os

# Add the directory containing extent.py to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../pygmu')

# Now import that source file
from extent import Extent

class TestExtent(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.finite_extent = Extent(0, 10)
        self.empty_extent = Extent(5, 5)
        self.infinite_start = Extent(Extent.NINF, 10)
        self.infinite_end = Extent(0, Extent.PINF)
        self.infinite_both = Extent.infinite()

    # ================================================================
    # Test Constructor
    # ================================================================

    def test_constructor_basic(self):
        """Test basic constructor functionality."""
        # Test finite extent
        e = Extent(0, 10)
        self.assertEqual(e.s, 0)
        self.assertEqual(e.e, 10)

        # Test empty extent
        e = Extent(5, 5)
        self.assertEqual(e.s, 5)
        self.assertEqual(e.e, 5)

        # Test infinite extent
        e = Extent(Extent.NINF, Extent.PINF)
        self.assertEqual(e.s, Extent.NINF)
        self.assertEqual(e.e, Extent.PINF)

    def test_constructor_with_duration(self):
        """Test constructor with duration parameter."""
        # From start + duration
        e = Extent(start=0, duration=10)
        self.assertEqual(e.s, 0)
        self.assertEqual(e.e, 10)

        # From end + duration
        e = Extent(end=10, duration=5)
        self.assertEqual(e.s, 5)
        self.assertEqual(e.e, 10)

        # Validation of consistency
        e = Extent(start=0, end=10, duration=10)
        self.assertEqual(e.s, 0)
        self.assertEqual(e.e, 10)

    def test_constructor_validation(self):
        """Test constructor validation."""
        # End before start
        with self.assertRaises(ValueError):
            Extent(10, 0)

        # Negative duration
        with self.assertRaises(ValueError):
            Extent(start=0, duration=-5)

        # Duration conflict
        with self.assertRaises(ValueError):
            Extent(start=0, end=10, duration=5)

        # Both infinite with duration
        with self.assertRaises(ValueError):
            Extent(start=Extent.NINF, end=Extent.PINF, duration=10)

        # Type errors
        with self.assertRaises(TypeError):
            Extent(start="not number", end=10)
        with self.assertRaises(TypeError):
            Extent(start=0, end=10, duration="not number")

    # ================================================================
    # Test Basic Properties
    # ================================================================

    def test_start_end(self):
        """Test start() and end() methods."""
        self.assertEqual(self.finite_extent.start(), 0)
        self.assertEqual(self.finite_extent.end(), 10)
        self.assertEqual(self.infinite_start.start(), Extent.NINF)
        self.assertEqual(self.infinite_end.end(), Extent.PINF)

    def test_is_indefinite(self):
        """Test is_indefinite() method."""
        self.assertFalse(self.finite_extent.is_indefinite())
        self.assertTrue(self.infinite_start.is_indefinite())
        self.assertTrue(self.infinite_end.is_indefinite())
        self.assertTrue(self.infinite_both.is_indefinite())

    def test_is_empty(self):
        """Test is_empty() method."""
        self.assertFalse(self.finite_extent.is_empty())
        self.assertTrue(self.empty_extent.is_empty())
        self.assertFalse(self.infinite_start.is_empty())

    def test_duration(self):
        """Test duration() method."""
        self.assertEqual(self.finite_extent.duration(), 10)
        self.assertEqual(self.empty_extent.duration(), 0)
        self.assertEqual(self.infinite_start.duration(), Extent.INDEFINITE_DURATION)
        self.assertEqual(self.infinite_end.duration(), Extent.INDEFINITE_DURATION)
        self.assertEqual(self.infinite_both.duration(), Extent.INDEFINITE_DURATION)

    # ================================================================
    # Test Offset
    # ================================================================

    def test_offset(self):
        """Test offset() method."""
        # Finite extent
        offset_extent = self.finite_extent.offset(5)
        self.assertEqual(offset_extent.s, 5)
        self.assertEqual(offset_extent.e, 15)

        # Empty extent
        offset_empty = self.empty_extent.offset(3)
        self.assertEqual(offset_empty.s, 8)
        self.assertEqual(offset_empty.e, 8)

        # Infinite extent
        offset_inf = self.infinite_start.offset(5)
        self.assertEqual(offset_inf.s, Extent.NINF)
        self.assertEqual(offset_inf.e, 15)

    def test_offset_validation(self):
        """Test offset() validation."""
        with self.assertRaises(TypeError):
            self.finite_extent.offset("not number")

    # ================================================================
    # Test Logical Operations
    # ================================================================

    def test_precedes(self):
        """Test precedes() method."""
        # With other extent
        e1 = Extent(0, 5)
        e2 = Extent(5, 10)
        self.assertTrue(e1.precedes(e2))
        self.assertFalse(e2.precedes(e1))

        # With scalar
        self.assertTrue(e1.precedes(5))
        self.assertFalse(e1.precedes(4))

    def test_follows(self):
        """Test follows() method."""
        # With other extent
        e1 = Extent(5, 10)
        e2 = Extent(0, 5)
        self.assertTrue(e1.follows(e2))
        self.assertFalse(e2.follows(e1))

        # With scalar - extent starts at 5, so it follows times < 5
        self.assertTrue(e1.follows(4.9))   # Should be True
        self.assertTrue(e1.follows(5))     # Should be True (5 is an end time)
        self.assertFalse(e1.follows(6))    # Should be False (starts before 6)

    def test_follows(self):
        """Test follows() method."""
        # With other extent
        e1 = Extent(5, 10)
        e2 = Extent(0, 5)
        self.assertTrue(e1.follows(e2))
        self.assertFalse(e2.follows(e1))

        # With scalar
        self.assertTrue(e1.follows(5))
        self.assertFalse(e1.follows(6))

    def test_overlaps(self):
        """Test overlaps() method."""
        # Overlapping extents
        e1 = Extent(0, 10)
        e2 = Extent(5, 15)
        self.assertTrue(e1.overlaps(e2))
        self.assertTrue(e2.overlaps(e1))

        # Non-overlapping
        e3 = Extent(10, 15)
        self.assertFalse(e1.overlaps(e3))

        # With scalar
        self.assertTrue(e1.overlaps(5))
        self.assertFalse(e1.overlaps(10))

    def test_spans(self):
        """Test spans() method."""
        # Larger spans smaller
        large = Extent(0, 20)
        small = Extent(5, 15)
        self.assertTrue(large.spans(small))
        self.assertFalse(small.spans(large))

        # With scalar
        self.assertTrue(large.spans(10))
        self.assertFalse(small.spans(20))

    def test_equals(self):
        """Test equals() method."""
        e1 = Extent(0, 10)
        e2 = Extent(0, 10)
        e3 = Extent(0, 15)

        self.assertTrue(e1.equals(e2))
        self.assertFalse(e1.equals(e3))

        with self.assertRaises(TypeError):
            e1.equals("not extent")

    # ================================================================
    # Test Duration Modification
    # ================================================================

    def test_set_duration(self):
        """Test set_duration() method."""
        # Anchor at start
        new_extent = self.finite_extent.set_duration(5, 'start')
        self.assertEqual(new_extent.s, 0)
        self.assertEqual(new_extent.e, 5)

        # Anchor at end
        new_extent = self.finite_extent.set_duration(5, 'end')
        self.assertEqual(new_extent.s, 5)
        self.assertEqual(new_extent.e, 10)

        # Anchor at center
        new_extent = self.finite_extent.set_duration(6, 'center')
        self.assertEqual(new_extent.s, 2)
        self.assertEqual(new_extent.e, 8)

    def test_set_duration_validation(self):
        """Test set_duration() validation."""
        # Negative duration
        with self.assertRaises(ValueError):
            self.finite_extent.set_duration(-5)

        # Indefinite extent
        with self.assertRaises(ValueError):
            self.infinite_start.set_duration(10)

        # Invalid anchor
        with self.assertRaises(ValueError):
            self.finite_extent.set_duration(10, 'invalid')

        # Type error
        with self.assertRaises(TypeError):
            self.finite_extent.set_duration("not number")

    def test_extend(self):
        """Test extend() method."""
        # Extend positive from start (end moves, start stays fixed)
        new_extent = self.finite_extent.extend(5, 'start')
        self.assertEqual(new_extent.s, 0)  # Start should stay at 0
        self.assertEqual(new_extent.e, 15)  # End should move to 15

        # Extend negative from start (end moves back, start stays fixed)
        new_extent = self.finite_extent.extend(-3, 'start')
        self.assertEqual(new_extent.s, 0)  # Start should stay at 0
        self.assertEqual(new_extent.e, 7)   # End should move to 7

    def test_extend_validation(self):
        """Test extend() validation."""
        # Resulting negative duration
        with self.assertRaises(ValueError):
            self.finite_extent.extend(-15)

        # Indefinite extent
        with self.assertRaises(ValueError):
            self.infinite_start.extend(10)

    def test_stretch(self):
        """Test stretch() method."""
        # Stretch by factor
        new_extent = self.finite_extent.stretch(2.0, 'center')
        self.assertEqual(new_extent.s, -5)
        self.assertEqual(new_extent.e, 15)
        self.assertEqual(new_extent.duration(), 20)

        # Shrink by factor
        new_extent = self.finite_extent.stretch(0.5, 'center')
        self.assertEqual(new_extent.s, 2.5)
        self.assertEqual(new_extent.e, 7.5)
        self.assertEqual(new_extent.duration(), 5)

    # ================================================================
    # Test Multi-Extent Operations
    # ================================================================

    def test_union(self):
        """Test union operations."""
        e1 = Extent(0, 5)
        e2 = Extent(3, 8)
        e3 = Extent(10, 15)

        # Instance method
        union_result = e1.union(e2)
        self.assertEqual(union_result.s, 0)
        self.assertEqual(union_result.e, 8)

        # Multiple arguments
        union_result = e1.union(e2, e3)
        self.assertEqual(union_result.s, 0)
        self.assertEqual(union_result.e, 15)

        # Class method
        union_result = Extent.union_all([e1, e2, e3])
        self.assertEqual(union_result.s, 0)
        self.assertEqual(union_result.e, 15)

        # Empty list
        self.assertEqual(Extent.union_all([]), Extent.null())

    def test_intersect(self):
        """Test intersect operations."""
        e1 = Extent(0, 10)
        e2 = Extent(5, 15)
        e3 = Extent(12, 20)

        # Instance method
        intersect_result = e1.intersect(e2)
        self.assertEqual(intersect_result.s, 5)
        self.assertEqual(intersect_result.e, 10)

        # No intersection
        intersect_result = e1.intersect(e3)
        self.assertTrue(intersect_result.is_empty())

        # Class method
        intersect_result = Extent.intersect_all([e1, e2])
        self.assertEqual(intersect_result.s, 5)
        self.assertEqual(intersect_result.e, 10)

        # Empty list
        self.assertEqual(Extent.intersect_all([]), Extent.null())

    def test_find_gaps(self):
        """Test find_gaps() method."""
        # Sorted, non-overlapping extents
        extents = [Extent(0, 5), Extent(7, 10), Extent(12, 15)]
        gaps = Extent.find_gaps(extents)

        self.assertEqual(len(gaps), 2)
        self.assertEqual(gaps[0].s, 5)
        self.assertEqual(gaps[0].e, 7)
        self.assertEqual(gaps[1].s, 10)
        self.assertEqual(gaps[1].e, 12)

        # Overlapping extents should raise error
        overlapping = [Extent(0, 5), Extent(4, 8)]
        with self.assertRaises(ValueError):
            Extent.find_gaps(overlapping)

    # ================================================================
    # Test Utility Methods
    # ================================================================

    def test_null_and_infinite(self):
        """Test null() and infinite() class methods."""
        null_extent = Extent.null()
        self.assertTrue(null_extent.is_empty())

        infinite_extent = Extent.infinite()
        self.assertTrue(infinite_extent.is_indefinite())
        self.assertEqual(infinite_extent.s, Extent.NINF)
        self.assertEqual(infinite_extent.e, Extent.PINF)

    # ================================================================
    # Test String Representations
    # ================================================================

    def test_string_representations(self):
        """Test __str__ and __repr__ methods."""
        # Finite extent
        e = Extent(0, 10)
        self.assertIn("0", str(e))
        self.assertIn("10", str(e))

        # Infinite extent
        e = Extent.infinite()
        self.assertIn("NINF", str(e))
        self.assertIn("PINF", str(e))
        self.assertIn("NINF", repr(e))
        self.assertIn("PINF", repr(e))

    # ================================================================
    # Test Hash and Equality
    # ================================================================

    def test_hash_and_equality(self):
        """Test hash() and equals() consistency."""
        e1 = Extent(0, 10)
        e2 = Extent(0, 10)
        e3 = Extent(0, 15)

        self.assertEqual(hash(e1), hash(e2))
        self.assertNotEqual(hash(e1), hash(e3))
        self.assertTrue(e1.equals(e2))
        self.assertFalse(e1.equals(e3))

if __name__ == '__main__':
    unittest.main()
