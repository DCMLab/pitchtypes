import re
from unittest import TestCase
from pitchtypes import Spelled, SpelledPitch, SpelledInterval, SpelledPitchClass, SpelledIntervalClass, Enharmonic


class TestSpelled(TestCase):
    line_of_fifths = [
        "Dbbbb", "Abbbb", "Ebbbb", "Bbbbb",
        "Fbbb", "Cbbb", "Gbbb", "Dbbb", "Abbb", "Ebbb", "Bbbb",
        "Fbb", "Cbb", "Gbb", "Dbb", "Abb", "Ebb", "Bbb",
        "Fb", "Cb", "Gb", "Db", "Ab", "Eb", "Bb",
        "F", "C", "G", "D", "A", "E", "B",
        "F#", "C#", "G#", "D#", "A#", "E#", "B#",
        "F##", "C##", "G##", "D##", "A##", "E##", "B##",
        "F###", "C###", "G###", "D###", "A###", "E###", "B###",
    ]

    line_of_intervals = [
        "ddd2", "ddd6", "ddd3", "ddd7",
        "ddd4", "ddd1", "ddd5", "dd2", "dd6", "dd3", "dd7",
        "dd4", "dd1", "dd5", "d2", "d6", "d3", "d7",
        "d4", "d1", "d5", "m2", "m6", "m3", "m7",
        "p4", "p1", "p5", "M2", "M6", "M3", "M7",
        "a4", "a1", "a5", "a2", "a6", "a3", "a7",
        "aa4", "aa1", "aa5", "aa2", "aa6", "aa3", "aa7",
        "aaa4", "aaa1", "aaa5", "aaa2", "aaa6", "aaa3", "aaa7"
    ]

    def test_types(self):
        # make sure the types are linking correctly
        self.assertEqual(Spelled.Pitch, SpelledPitch)
        self.assertEqual(Spelled.Interval, SpelledInterval)
        self.assertEqual(Spelled.PitchClass, SpelledPitchClass)
        self.assertEqual(Spelled.IntervalClass, SpelledIntervalClass)
        self.assertEqual(SpelledPitch._base_type, Spelled)
        self.assertEqual(SpelledInterval._base_type, Spelled)
        self.assertEqual(SpelledPitchClass._base_type, Spelled)
        self.assertEqual(SpelledIntervalClass._base_type, Spelled)

    def test_init(self):
        # create class and non-class objects
        for is_class in [True, False]:
            # create pitch (class) objects
            for idx, p in enumerate(self.line_of_fifths):
                if is_class:
                    pp = SpelledPitchClass(p)
                    # check conversion to enharmonic
                    self.assertEqual(pp.convert_to_enharmonic(), Enharmonic.PitchClass(p))
                    self.assertEqual(pp.convert_to(Enharmonic.PitchClass), Enharmonic.PitchClass(p))
                else:
                    p += "4"
                    pp = SpelledPitch(p)
                    # check conversion to enharmonic
                    self.assertEqual(pp.convert_to_enharmonic(), Enharmonic.Pitch(p))
                    self.assertEqual(pp.convert_to(Enharmonic.Pitch), Enharmonic.Pitch(p))
                # check base type is set on object
                self.assertEqual(pp._base_type, Spelled)
                # check class property is correct
                self.assertEqual(is_class, pp.is_class)
                # check pitch property is correct
                self.assertTrue(pp.is_pitch)
                # check interval property is correct
                self.assertFalse(pp.is_interval)
                # check string representation is correct
                self.assertEqual(str(pp), p)
                # check fifths steps are corrects
                self.assertEqual(pp.fifths(), idx - 26)
            # create interval (class) objects
            for idx, (interval_class_str,
                      inverse_interval_class_str) in enumerate(zip(self.line_of_intervals,
                                                                   reversed(self.line_of_intervals))):
                inverse_interval_class_str = "-" + inverse_interval_class_str
                if is_class:
                    # create objects
                    interval = SpelledIntervalClass(interval_class_str)
                    inverse_interval = SpelledIntervalClass(inverse_interval_class_str)
                    # check conversion to enharmonic
                    self.assertEqual(interval.convert_to_enharmonic(),
                                     Enharmonic.IntervalClass(interval_class_str))
                    self.assertEqual(interval.convert_to(Enharmonic.IntervalClass),
                                     Enharmonic.IntervalClass(interval_class_str))
                else:
                    # add octave for non-class
                    interval_class_str += ":4"
                    inverse_interval_class_str += ":4"
                    # create objects
                    interval = SpelledInterval(interval_class_str)
                    inverse_interval = SpelledInterval(inverse_interval_class_str)
                    # check conversion to enharmonic
                    self.assertEqual(interval.convert_to_enharmonic(),
                                     Enharmonic.Interval(interval_class_str))
                    self.assertEqual(interval.convert_to(Enharmonic.Interval),
                                     Enharmonic.Interval(interval_class_str))
                # check link to base type
                self.assertEqual(interval._base_type, Spelled)
                self.assertEqual(inverse_interval._base_type, Spelled)
                # check class, pitch, and interval property
                self.assertEqual(is_class, interval.is_class)
                self.assertEqual(is_class, inverse_interval.is_class)
                self.assertFalse(interval.is_pitch)
                self.assertTrue(interval.is_interval)
                # check they print the same as the input
                self.assertEqual(interval_class_str, str(interval))
                self.assertEqual(interval_class_str, interval.name())
                # only for classes
                if is_class:
                    # the inverse is equivalent
                    self.assertEqual(interval, inverse_interval)
                    # so they also print the same
                    self.assertEqual(interval_class_str, inverse_interval.name())
                    # and subtracting gives a perfect unison p1
                    self.assertEqual(SpelledIntervalClass("p1"), interval - inverse_interval)
                    # the inverse name corresponds to the inverse input
                    self.assertEqual(inverse_interval_class_str, interval.name(inverse=True))
                    self.assertEqual(inverse_interval_class_str, inverse_interval.name(inverse=True))
                self.assertEqual(interval.fifths(), idx - 26)

    def test_arithmetics(self):
        for p, i in zip(self.line_of_fifths, self.line_of_intervals):
            p = SpelledPitchClass(p)
            i = SpelledIntervalClass("+" + i)
            ref = SpelledPitchClass("C")
            delta = p - ref
            self.assertEqual(delta, i)
            self.assertEqual(ref + delta, p)
            p1 = SpelledPitch("C#4")
            p2 = SpelledPitch("Gb5")
            self.assertRaises(TypeError, lambda: p1 + p2)
            self.assertRaises(TypeError, lambda: SpelledPitchClass("G") - SpelledPitch("G4"))

    def test_from_fifths_functions(self):
        print(SpelledInterval("ddd2:4"))
        print(SpelledInterval("-aaa7:4"))
        for fifths, diatonic, interval_class, inverse_interval_class in [(-1, -4, 'p4', 'p5'),
                                                                         (0, 0, 'p1', 'p1'),
                                                                         (1, 4, 'p5', 'p4'),
                                                                         (2, 8, 'M2', 'm7'),
                                                                         (3, 12, 'M6', 'm3'),
                                                                         (4, 16, 'M3', 'm6'),
                                                                         (5, 20, 'M7', 'm2'),
                                                                         (6, 24, 'a4', 'd5'),
                                                                         (7, 28, 'a1', 'd1'),
                                                                         (8, 32, 'a5', 'd4')]:
            self.assertEqual(diatonic, Spelled.diatonic_steps_from_fifths(fifths))
            self.assertEqual(diatonic % 7 + 1, Spelled.generic_interval_class_from_fifths(fifths))
            self.assertEqual(interval_class, Spelled.interval_class_from_fifths(fifths, inverse=False))
            self.assertEqual(inverse_interval_class, Spelled.interval_class_from_fifths(fifths, inverse=True))

    def test_parsing(self):
        # attempt to parse non-string should raise TypeError
        self.assertRaises(TypeError, lambda: Spelled.parse_pitch(5))
        self.assertRaises(TypeError, lambda: Spelled.parse_interval(5))
        # bad string input should raise ValueError
        self.assertRaises(ValueError, lambda: Spelled.parse_pitch("xxx"))
        self.assertRaises(ValueError, lambda: Spelled.parse_interval("yyy"))
        # temporally introduce a bug by changing regex
        old_regex = Spelled._interval_regex
        Spelled._interval_regex = re.compile("^(?P<generic>[1-7])(?P<quality>[a-z])$")
        self.assertRaises(RuntimeError, lambda: Spelled.parse_interval("1x"))
        # change back to not mess up other tests
        Spelled._interval_regex = old_regex

        # check bad input
        self.assertRaises(ValueError, lambda: Spelled.fifths_from_diatonic_pitch_class("X"))
        self.assertRaises(ValueError, lambda: Spelled.fifths_from_generic_interval_class("X"))

        # name and fifths not implemented in base class
        s = Spelled("x", True, True)
        self.assertRaises(NotImplementedError, lambda: s.name())
        self.assertRaises(NotImplementedError, lambda: s.fifths())
