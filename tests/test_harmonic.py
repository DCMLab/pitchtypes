from unittest import TestCase
import numpy as np
from pitchtypes import Harmonic


class TestHarmonic(TestCase):

    def test_init(self):
        # check parsing
        # check its converting to int even with float input
        self.assertEqual(Harmonic.parse_exponents([1, -2, 3, -4.00]).dtype, int)
        # for non-class
        self.assertTrue(
            np.array_equal(
                np.array([1, -2, 3, -4.0]), Harmonic.parse_exponents([1, -2, 3, -4])
            )
        )
        self.assertTrue(
            np.array_equal(
                np.array([1, -2, 3, -4]), Harmonic.parse_exponents([1, -2, 3, -4.00])
            )
        )
        self.assertTrue(
            np.array_equal(
                np.array([1, -2, 3, -4]), Harmonic.parse_exponents("[1, -2, 3, -4]")
            )
        )
        # raise on bad input
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("1, -2, 3, -4]"))
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("[1, -2, 3, -4"))
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("[1, 2, -3; 4]"))
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("[1, X, -3, 4]"))
        self.assertRaises(
            ValueError, lambda: Harmonic.parse_exponents("[1, 2, -3.5, 4]")
        )
        self.assertRaises(
            ValueError, lambda: Harmonic.parse_exponents("[1, 2, -3, 4.0]")
        )

        # Interval
        # initialise from list
        # ToDo: fix string representation to get red of np.int
        self.assertEqual(
            "HarmonicInterval([np.int64(1), np.int64(-2), np.int64(3), np.int64(-4)])",
            str(Harmonic.Interval([1, -2, 3, -4])),
        )
        # initialise from string
        self.assertEqual(
            "HarmonicInterval([np.int64(1), np.int64(-2), np.int64(3), np.int64(-4)])",
            str(Harmonic.Interval("[1, -2, 3, -4]")),
        )

        # IntervalClass
        # initialise from list
        self.assertEqual(
            "HarmonicIntervalClass([None, np.int64(1), np.int64(-2), np.int64(3), np.int64(-4)])",
            str(Harmonic.IntervalClass([1, -2, 3, -4])),
        )
        # initialise from string
        self.assertEqual(
            "HarmonicIntervalClass([None, np.int64(1), np.int64(-2), np.int64(3), np.int64(-4)])",
            str(Harmonic.IntervalClass("[1, -2, 3, -4]")),
        )

    def test_to_class(self):
        self.assertEqual(
            Harmonic.Interval([1, 2, 3, 4, 5]).to_class(),
            Harmonic.IntervalClass([2, 3, 4, 5]),
        )
