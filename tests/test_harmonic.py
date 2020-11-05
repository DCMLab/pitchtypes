from unittest import TestCase
import numpy as np
from pitchtypes import Harmonic, LogFreqPitch


class TestHarmonic(TestCase):

    def test_init(self):
        # check parsing
        # check its converting to int even with float input
        self.assertEqual(Harmonic.parse_exponents([1, -2, 3, -4.00]).dtype, np.int)
        # for non-class
        self.assertTrue(np.array_equal(np.array([1, -2, 3, -4.]), Harmonic.parse_exponents([1, -2, 3, -4])))
        self.assertTrue(np.array_equal(np.array([1, -2, 3, -4]), Harmonic.parse_exponents([1, -2, 3, -4.00])))
        self.assertTrue(np.array_equal(np.array([1, -2, 3, -4]), Harmonic.parse_exponents("[1, -2, 3, -4]")))
        # raise on bad input
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("1, -2, 3, -4]"))
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("[1, -2, 3, -4"))
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("[1, 2, -3; 4]"))
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("[1, X, -3, 4]"))
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("[1, 2, -3.5, 4]"))
        self.assertRaises(ValueError, lambda: Harmonic.parse_exponents("[1, 2, -3, 4.0]"))

        # Pitch
        # initialise from list
        self.assertEqual("HarmonicPitch(440.Hz [1, -2, 3, -4])",
                         str(Harmonic.Pitch(LogFreqPitch(440, is_freq=True), [1, -2, 3, -4])))
        # initialise from string
        self.assertEqual("HarmonicPitch(3.53 [1, -2, 3, -4])",
                         str(Harmonic.Pitch(3.53, "[1, -2, 3, -4]")))

        # PitchClass
        # initialise from list
        self.assertEqual("HarmonicPitchClass(440.Hz [None, 1, -2, 3, -4])",
                         str(Harmonic.PitchClass(LogFreqPitch(440, is_freq=True), [1, -2, 3, -4])))
        # initialise from string
        self.assertEqual("HarmonicPitchClass(3.53 [None, 1, -2, 3, -4])",
                         str(Harmonic.PitchClass(3.53, "[1, -2, 3, -4]")))

        # Interval
        # initialise from list
        self.assertEqual("HarmonicInterval([1, -2, 3, -4])", str(Harmonic.Interval([1, -2, 3, -4])))
        # initialise from string
        self.assertEqual("HarmonicInterval([1, -2, 3, -4])", str(Harmonic.Interval("[1, -2, 3, -4]")))

        # IntervalClass
        # initialise from list
        self.assertEqual("HarmonicIntervalClass([None, 1, -2, 3, -4])", str(Harmonic.IntervalClass([1, -2, 3, -4])))
        # initialise from string
        self.assertEqual("HarmonicIntervalClass([None, 1, -2, 3, -4])", str(Harmonic.IntervalClass("[1, -2, 3, -4]")))

    def test_arithmetics(self):
        self.assertEqual("",
                         Harmonic.Pitch(LogFreqPitch(440, is_freq=True), [2, 3, 4]) -
                         Harmonic.Pitch(LogFreqPitch(220, is_freq=True), [1, 2, 3]))
