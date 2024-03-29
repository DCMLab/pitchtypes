from unittest import TestCase
from unittest.mock import patch

import re
import numpy as np
from pitchtypes import Spelled, AbstractSpelledInterval, AbstractSpelledPitch, SpelledPitch, SpelledInterval, SpelledPitchClass, SpelledIntervalClass, Enharmonic


class TestSpelled(TestCase):
    def arrayEqual(self, a, b):
        if not np.array_equal(a, b):
            raise self.failureException(f"{a} is not equal to {b}")

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

    line_of_fifths_unicode = [
        "D♭♭♭♭", "A♭♭♭♭", "E♭♭♭♭", "B♭♭♭♭",
        "F♭♭♭", "C♭♭♭", "G♭♭♭", "D♭♭♭", "A♭♭♭", "E♭♭♭", "B♭♭♭",
        "F♭♭", "C♭♭", "G♭♭", "D♭♭", "A♭♭", "E♭♭", "B♭♭",
        "F♭", "C♭", "G♭", "D♭", "A♭", "E♭", "B♭",
        "F", "C", "G", "D", "A", "E", "B",
        "F♯", "C♯", "G♯", "D♯", "A♯", "E♯", "B♯",
        "F♯♯", "C♯♯", "G♯♯", "D♯♯", "A♯♯", "E♯♯", "B♯♯",
        "F♯♯♯", "C♯♯♯", "G♯♯♯", "D♯♯♯", "A♯♯♯", "E♯♯♯", "B♯♯♯",
    ]

    line_of_intervals = [
        "ddd2", "ddd6", "ddd3", "ddd7",
        "ddd4", "ddd1", "ddd5", "dd2", "dd6", "dd3", "dd7",
        "dd4", "dd1", "dd5", "d2", "d6", "d3", "d7",
        "d4", "d1", "d5", "m2", "m6", "m3", "m7",
        "P4", "P1", "P5", "M2", "M6", "M3", "M7",
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

        def sign(n):
            if n == 0:
                return 0
            if n > 0:
                return 1
            else:
                return -1

        # create class and non-class objects
        for is_class in [True, False]:
            # create pitch (class) objects
            for idx, p in enumerate(self.line_of_fifths):
                if is_class:
                    pp = SpelledPitchClass(p)
                    # test factory functions
                    self.assertEqual(pp, SpelledPitchClass.from_fifths(fifths=pp.fifths()))
                    # check conversion to enharmonic
                    self.assertEqual(pp.convert_to(Enharmonic.PitchClass), Enharmonic.PitchClass(p))
                    # test class conversion
                    self.assertEqual(pp, pp.pc())
                    # test string representation
                    self.assertEqual(str(pp), p)
                    # test embed(), internal_octaves()
                    self.assertEqual(str(pp) + "0", str(pp.embed()))
                    self.assertEqual(pp.internal_octaves(), 0)
                else:
                    for oct in range(-3, 10):
                        p_oct = p + str(oct)
                        pp = SpelledPitch(p_oct)
                        # test factory functions
                        self.assertEqual(pp, SpelledPitch.from_fifths_and_octaves(fifths=pp.fifths(),
                                                                                  octaves=pp.internal_octaves()))
                        # check conversion to enharmonic
                        self.assertEqual(pp.convert_to(Enharmonic.Pitch), Enharmonic.Pitch(p_oct))
                        # check octaves / internal octaves
                        self.assertEqual(pp.octaves(), pp.value[0] + (pp.fifths() * 4) // 7)
                        self.assertEqual(pp.internal_octaves(), pp.value[0])
                        # test class conversion
                        self.assertEqual(pp.to_class(), SpelledPitchClass(p))
                        self.assertEqual(pp.pc(), SpelledPitchClass(p))
                        # test string representation
                        self.assertEqual(str(pp), p_oct)
                        # test embed()
                        self.assertEqual(pp, pp.embed())
                # check base type is set on object
                self.assertEqual(pp._base_type, Spelled)
                # check class property is correct
                self.assertEqual(is_class, pp.is_class)
                # check pitch property is correct
                self.assertTrue(pp.is_pitch)
                # check interval property is correct
                self.assertFalse(pp.is_interval)
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
                    # test factory functions
                    self.assertEqual(interval, SpelledIntervalClass.from_fifths(fifths=interval.fifths()))
                    # check conversion to enharmonic
                    self.assertEqual(interval.convert_to(Enharmonic.IntervalClass),
                                     Enharmonic.IntervalClass(interval_class_str))
                    # test class conversion
                    self.assertEqual(interval, interval.ic())
                    # test unison(), octave(), embed(), internal_octaves(), direction(), abs()
                    self.assertEqual(SpelledIntervalClass.unison(), SpelledIntervalClass("P1"))
                    self.assertEqual(SpelledIntervalClass.octave(), SpelledIntervalClass("P1"))
                    if interval.diatonic_steps() != 0: # exclude unisons, for which this doesn't hold
                        self.assertEqual(str(interval) + ":0", str(interval.embed()))
                        self.assertEqual(interval.direction(), sign((float(interval_class_str[-1]) + 2) % 7 - 3))
                    self.assertEqual(interval.internal_octaves(), 0)
                    # test print output
                    self.assertEqual(interval_class_str, str(interval))
                    self.assertEqual(interval_class_str, interval.name())
                else:
                    for oct in range(0, 10):
                        # add octave for non-class
                        interval_str = interval_class_str + f":{oct}"
                        inverse_interval_str = inverse_interval_class_str + f":{oct}"
                        # create objects
                        interval = SpelledInterval(interval_str)
                        inverse_interval = SpelledInterval(inverse_interval_str)
                        # check octaves / internal octaves
                        self.assertEqual(interval.octaves(),
                                         interval.value[0] + interval.diatonic_steps_from_fifths(interval.fifths()) // 7)
                        self.assertEqual(interval.internal_octaves(), interval.value[0])
                        # test factory functions
                        self.assertEqual(interval,
                                         SpelledInterval.from_fifths_and_octaves(fifths=interval.fifths(),
                                                                                 octaves=interval.internal_octaves()))
                        # check conversion to enharmonic
                        self.assertEqual(interval.convert_to(Enharmonic.Interval), Enharmonic.Interval(interval_str))
                        # test class conversion
                        self.assertEqual(interval.to_class(), SpelledIntervalClass(interval_class_str))
                        self.assertEqual(interval.ic(), SpelledIntervalClass(interval_class_str))
                        # test unison(), octave(), embed()
                        self.assertEqual(SpelledInterval.unison(), SpelledInterval("P1:0"))
                        self.assertEqual(SpelledInterval.octave(), SpelledInterval("P1:1"))
                        self.assertEqual(interval, interval.embed())
                        # test print output
                        if interval.diatonic_steps() != 0: # doesn't hold for unisons
                            self.assertEqual(interval_str, str(interval))
                            self.assertEqual(interval_str, interval.name())
                # check link to base type
                self.assertEqual(interval._base_type, Spelled)
                self.assertEqual(inverse_interval._base_type, Spelled)
                # check class, pitch, and interval property
                self.assertEqual(is_class, interval.is_class)
                self.assertEqual(is_class, inverse_interval.is_class)
                self.assertFalse(interval.is_pitch)
                self.assertTrue(interval.is_interval)
                # only for classes
                if is_class:
                    # the inverse is equivalent
                    self.assertEqual(interval, inverse_interval)
                    # so they also print the same
                    self.assertEqual(interval_class_str, inverse_interval.name())
                    # and subtracting gives a perfect unison p1
                    self.assertEqual(SpelledIntervalClass("P1"), interval - inverse_interval)
                    # the inverse name corresponds to the inverse input
                    self.assertEqual(inverse_interval_class_str, interval.name(inverse=True))
                    self.assertEqual(inverse_interval_class_str, inverse_interval.name(inverse=True))
                self.assertEqual(interval.fifths(), idx - 26)

    def test_bad_regex(self):
        self.assertRaises(ValueError, lambda: SpelledInterval("xyz"))      # not meaningful at all
        self.assertRaises(ValueError, lambda: SpelledIntervalClass("p3"))  # there is no perfect third
        self.assertRaises(ValueError, lambda: SpelledIntervalClass("m5"))  # there is no major fifth
        self.assertRaises(ValueError, lambda: SpelledIntervalClass("M5"))  # there is no minor fifth

    def test_arithmetics(self):
        for p, p_unicode, i in zip(self.line_of_fifths, self.line_of_fifths_unicode, self.line_of_intervals):
            p = SpelledPitchClass(p)
            self.assertEqual(p, SpelledPitchClass(p_unicode))
            i = SpelledIntervalClass("+" + i)
            ref = SpelledPitchClass("C")
            delta = p - ref
            self.assertEqual(delta, i)
            self.assertEqual(ref + delta, p)
        p1 = SpelledPitch("C#4")
        p2 = SpelledPitch("Gb5")
        self.assertRaises(TypeError, lambda: p1 + p2)
        self.assertRaises(TypeError, lambda: SpelledPitchClass("G") - SpelledPitch("G4"))
        self.assertRaises(TypeError, lambda: SpelledPitch("Ebb4").interval_from(1))
        self.assertRaises(TypeError, lambda: SpelledPitchClass("Ebb").interval_from(1))
        self.assertEqual(SpelledPitch("G4").interval_from(SpelledPitch("C#4")), SpelledInterval("d5:0"))
        self.assertEqual(SpelledPitch("G4").interval_to(SpelledPitch("C#4")), SpelledInterval("-d5:0"))
        self.assertEqual(SpelledPitchClass("G").interval_from(SpelledPitchClass("C#")), SpelledIntervalClass("d5"))
        self.assertEqual(SpelledPitchClass("G").interval_to(SpelledPitchClass("C#")), SpelledIntervalClass("-d5"))
        self.assertEqual(4 * SpelledInterval("M2:0"), SpelledInterval("a5:0"))
        self.assertEqual(4 * SpelledIntervalClass("M2"), SpelledIntervalClass("a5"))

    def test_from_fifths_functions(self):
        print(SpelledInterval("ddd2:4"))
        print(SpelledInterval("-aaa7:4"))
        for fifths, diatonic, interval_class, inverse_interval_class in [(-1, -4, 'P4', 'P5'),
                                                                         (0, 0, 'P1', 'P1'),
                                                                         (1, 4, 'P5', 'P4'),
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
        # test for bad interval quality
        Spelled._interval_regex = re.compile("^(?P<generic0>[1-7])(?P<quality0>[a-z])$")
        self.assertRaises(RuntimeError, lambda: Spelled.parse_interval("1x"))
        # test for bad quality/generic matching (mixing up indices)
        Spelled._interval_regex = re.compile("^("
                                             "(?P<generic0>1)(?P<quality1>a)|"
                                             "(?P<generic1>2)(?P<quality0>b)|"
                                             "(?P<generic2>3)(?P<quality2>c)"
                                             ")$")
        self.assertRaises(RuntimeError, lambda: Spelled.parse_interval("1a"))
        # change back to not mess up other tests
        Spelled._interval_regex = old_regex

        # check bad input
        self.assertRaises(ValueError, lambda: Spelled.fifths_from_diatonic_pitch_class("X"))
        self.assertRaises(ValueError, lambda: Spelled.fifths_from_generic_interval_class("X"))

    def test_constructors(self):
        self.assertEqual(SpelledInterval.from_independent(2,0), SpelledInterval("M2:0"))
        self.assertEqual(SpelledPitch.from_independent(2,4), SpelledPitch("D4"))

    @patch.multiple(AbstractSpelledInterval, __abstractmethods__=set())
    @patch.multiple(AbstractSpelledPitch, __abstractmethods__=set())
    def test_abstract_base_functions(self):
        s = Spelled("x", True, True)
        self.assertRaises(NotImplementedError, lambda: s.name())
        self.assertRaises(NotImplementedError, lambda: s.fifths())
        self.assertRaises(NotImplementedError, lambda: s.octaves())
        self.assertRaises(NotImplementedError, lambda: s.internal_octaves())
        self.assertRaises(NotImplementedError, lambda: s.alteration())
        self.assertRaises(NotImplementedError, lambda: s.compare(1))
        self.assertRaises(NotImplementedError, lambda: s.onehot())
        
        self.assertRaises(NotImplementedError, lambda: AbstractSpelledInterval().generic())
        self.assertRaises(NotImplementedError, lambda: AbstractSpelledInterval().diatonic_steps())
        self.assertRaises(NotImplementedError, lambda: AbstractSpelledPitch().letter())
 
    def test_general_interface(self):
        self.assertEqual(SpelledInterval.unison(), SpelledInterval("P1:0"))
        self.assertEqual(SpelledIntervalClass.unison(), SpelledIntervalClass("P1"))
        self.assertEqual(SpelledInterval.octave(), SpelledInterval("P1:1"))
        self.assertEqual(SpelledIntervalClass.octave(), SpelledIntervalClass("P1"))
        
        self.assertEqual(SpelledInterval("m2:0").direction(), 1)
        self.assertEqual(SpelledInterval("P1:0").direction(), 0)
        self.assertEqual(SpelledInterval("d1:0").direction(), -1)
        self.assertEqual(SpelledInterval("a1:0").direction(), 1)
        self.assertEqual(SpelledInterval("-m3:0").direction(), -1)
        self.assertEqual(SpelledInterval("P4:0").direction(), 1)
        self.assertEqual(SpelledInterval("-M7:0").direction(), -1)
        self.assertEqual(SpelledInterval("-m3:0").abs(), SpelledInterval("m3:0"))
        self.assertEqual(SpelledInterval("m3:0").abs(), SpelledInterval("m3:0"))
        self.assertEqual(SpelledIntervalClass("m2").direction(), 1)
        self.assertEqual(SpelledIntervalClass("P1").direction(), 0)
        self.assertEqual(SpelledIntervalClass("d1").direction(), -1)
        self.assertEqual(SpelledIntervalClass("a1").direction(), 1)
        self.assertEqual(SpelledIntervalClass("P4").direction(), 1)
        self.assertEqual(SpelledIntervalClass("-M7").direction(), 1)
        self.assertEqual(SpelledIntervalClass("aaaaa4").direction(), 1)
        self.assertEqual(SpelledIntervalClass("ddddd5").direction(), -1)
        self.assertEqual(SpelledIntervalClass("-m3").abs(), SpelledIntervalClass("m3"))
        self.assertEqual(SpelledIntervalClass("m3").abs(), SpelledIntervalClass("m3"))

        self.assertEqual(SpelledInterval.chromatic_semitone(), SpelledInterval("a1:0"))
        self.assertEqual(SpelledIntervalClass.chromatic_semitone(), SpelledIntervalClass("a1"))
        
        self.assertEqual(SpelledInterval("d1:0").is_step(), True)
        self.assertEqual(SpelledInterval("P1:0").is_step(), True)
        self.assertEqual(SpelledInterval("a1:0").is_step(), True)
        self.assertEqual(SpelledInterval("d2:0").is_step(), True)
        self.assertEqual(SpelledInterval("m2:0").is_step(), True)
        self.assertEqual(SpelledInterval("M2:0").is_step(), True)
        self.assertEqual(SpelledInterval("a2:0").is_step(), True)
        self.assertEqual(SpelledInterval("-d2:0").is_step(), True)
        self.assertEqual(SpelledInterval("-m2:0").is_step(), True)
        self.assertEqual(SpelledInterval("-M2:0").is_step(), True)
        self.assertEqual(SpelledInterval("-a2:0").is_step(), True)

        self.assertEqual(SpelledInterval("d3:0").is_step(), False)
        self.assertEqual(SpelledInterval("-d3:0").is_step(), False)
        self.assertEqual(SpelledInterval("M7:0").is_step(), False)
        self.assertEqual(SpelledInterval("-M7:0").is_step(), False)
        self.assertEqual(SpelledInterval("P1:1").is_step(), False)
        self.assertEqual(SpelledInterval("-P1:1").is_step(), False)
        self.assertEqual(SpelledInterval("m2:1").is_step(), False)
        self.assertEqual(SpelledInterval("-m2:1").is_step(), False)

        self.assertEqual(SpelledIntervalClass("d1").is_step(), True)
        self.assertEqual(SpelledIntervalClass("P1").is_step(), True)
        self.assertEqual(SpelledIntervalClass("a1").is_step(), True)
        self.assertEqual(SpelledIntervalClass("d2").is_step(), True)
        self.assertEqual(SpelledIntervalClass("m2").is_step(), True)
        self.assertEqual(SpelledIntervalClass("M2").is_step(), True)
        self.assertEqual(SpelledIntervalClass("a2").is_step(), True)
        self.assertEqual(SpelledIntervalClass("-d2").is_step(), True)
        self.assertEqual(SpelledIntervalClass("-m2").is_step(), True)
        self.assertEqual(SpelledIntervalClass("-M2").is_step(), True)
        self.assertEqual(SpelledIntervalClass("-a2").is_step(), True)

        self.assertEqual(SpelledIntervalClass("d3").is_step(), False)
        self.assertEqual(SpelledIntervalClass("-d3").is_step(), False)

    def test_ordering(self):
        # ordering of intervals and pitches should follow the logical ordering of the pitch system
        self.assertTrue(SpelledInterval("aa4:0") < SpelledInterval("dd5:0"))
        self.assertTrue(SpelledPitch("C##4") < SpelledPitch("Dbb4"))
        self.assertTrue(SpelledPitch("C-1") > SpelledPitch("Cb-1"))
        self.assertFalse(SpelledPitch("C4") == 0)
        
        self.assertTrue(SpelledInterval("aa4:0") <= SpelledInterval("dd5:0"))
        self.assertTrue(SpelledPitch("C##4") <= SpelledPitch("Dbb4"))
        self.assertTrue(SpelledPitch("C-1") >= SpelledPitch("Cb-1"))

        # ordering of interval/pitch classes is arbitrary, for now it follows the line of fifths
        self.assertTrue(SpelledIntervalClass("P5") > SpelledIntervalClass("P1"))
        self.assertTrue(SpelledPitchClass("G") > SpelledPitchClass("C"))

    def test_spelled_accessors(self):
        self.assertEqual(SpelledInterval("M3:1").octaves(),  1)
        self.assertEqual(SpelledInterval("M3:1").internal_octaves(),  -1)
        self.assertEqual(SpelledInterval("M3:1").fifths(),  4)
        self.assertEqual(SpelledInterval("M3:1").degree(),  2)
        self.assertEqual(SpelledInterval("M3:1").generic(),  2)
        self.assertEqual(SpelledInterval("M3:1").diatonic_steps(),  9)
        self.assertEqual(SpelledInterval("M3:1").alteration(),  0)
        self.assertEqual(SpelledInterval("-M3:1").octaves(),  -2)
        self.assertEqual(SpelledInterval("-M3:1").internal_octaves(),  1)
        self.assertEqual(SpelledInterval("-M3:1").fifths(),  -4)
        self.assertEqual(SpelledInterval("-M3:1").degree(),  5)
        self.assertEqual(SpelledInterval("-M3:1").generic(),  -2)
        self.assertEqual(SpelledInterval("-M3:1").diatonic_steps(),  -9)
        self.assertEqual(SpelledInterval("-M3:1").alteration(),  0)
        
        self.assertEqual(SpelledIntervalClass("a5").octaves(),  0)
        self.assertEqual(SpelledIntervalClass("a5").internal_octaves(),  0)
        self.assertEqual(SpelledIntervalClass("a5").fifths(),  8)
        self.assertEqual(SpelledIntervalClass("a5").degree(),  4)
        self.assertEqual(SpelledIntervalClass("a5").generic(),  4)
        self.assertEqual(SpelledIntervalClass("a5").diatonic_steps(),  4)
        self.assertEqual(SpelledIntervalClass("a5").alteration(),  1)
        
        self.assertEqual(SpelledPitch("Ebb5").octaves(),  5)
        self.assertEqual(SpelledPitch("Ebb5").fifths(),  -10)
        self.assertEqual(SpelledPitch("Ebb5").degree(),  2)
        self.assertEqual(SpelledPitch("Ebb5").alteration(),  -2)
        self.assertEqual(SpelledPitch("Ebb5").letter(),  'E')
        
        self.assertEqual(SpelledPitchClass("F#").octaves(), 0)
        self.assertEqual(SpelledPitchClass("F#").fifths(), 6)
        self.assertEqual(SpelledPitchClass("F#").degree(), 3)
        self.assertEqual(SpelledPitchClass("F#").alteration(), 1)
        self.assertEqual(SpelledPitchClass("F#").letter(), 'F')
        
        # edge cases
        self.assertEqual(SpelledIntervalClass("P4").alteration(),  0)
        self.assertEqual(SpelledIntervalClass("M7").alteration(),  0)
        self.assertEqual(SpelledInterval("-P4:0").alteration(),  0)
        self.assertEqual(SpelledInterval("-M7:0").alteration(),  0)
        self.assertEqual(SpelledInterval("a4:0").alteration(),  1)
        self.assertEqual(SpelledInterval("m7:0").alteration(),  -1)
        self.assertEqual(SpelledInterval("-a4:0").alteration(),  1)
        self.assertEqual(SpelledInterval("-m7:0").alteration(),  -1)
        self.assertEqual(SpelledPitchClass("F").alteration(),  0)
        self.assertEqual(SpelledPitchClass("B").alteration(),  0)
        self.assertEqual(SpelledPitchClass("F").alteration(),  0)
        self.assertEqual(SpelledPitchClass("B").alteration(),  0)
        self.assertEqual(SpelledPitch("Cb-1").alteration(), -1)
        self.assertEqual(SpelledPitch("C#-1").alteration(), 1)
        self.assertEqual(SpelledPitch("D-1").degree(), 1)

    def test_onehot(self):
        self.arrayEqual(SpelledInterval("M2:0").onehot((-2,2), (-1,1)),
                        np.array([[0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,1,0]]))
        self.assertRaises(ValueError, lambda: SpelledInterval("M2:0").onehot((-2,1), (-1,1)))
        self.assertRaises(ValueError, lambda: SpelledInterval("M2:2").onehot((-2,2), (-1,1)))
        self.assertEqual(SpelledInterval.from_onehot(SpelledInterval("a4:2").onehot((-8,8), (-2,2)), -8, -2),
                         SpelledInterval("a4:2"))
        self.assertRaises(ValueError, lambda: SpelledInterval.from_onehot(np.array([1,0,1]), 0, 0))
        
        self.arrayEqual(SpelledIntervalClass("M2").onehot((-2,3)),
                        np.array([0, 0, 0, 0, 1, 0]))
        self.assertRaises(ValueError, lambda: SpelledIntervalClass("M6").onehot((-2,2)))
        self.assertEqual(SpelledIntervalClass.from_onehot(SpelledIntervalClass("a4").onehot((-8,8)), -8),
                         SpelledIntervalClass("a4"))
        self.assertRaises(ValueError, lambda: SpelledIntervalClass.from_onehot(np.array([1,0,1]), 0))
        
        self.arrayEqual(SpelledPitch("D4").onehot((-2,2), (3,5)),
                        np.array([[0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,1,0]]))
        self.assertRaises(ValueError, lambda: SpelledPitch("D4").onehot((-2,1), (3,5)))
        self.assertRaises(ValueError, lambda: SpelledPitch("D6").onehot((-2,2), (3,5)))
        self.assertEqual(SpelledPitch.from_onehot(SpelledPitch("F#4").onehot((-8,8), (0,6)), -8, 0),
                         SpelledPitch("F#4"))
        self.assertRaises(ValueError, lambda: SpelledPitch.from_onehot(np.array([1,0,1]), 0, 0))
        
        self.arrayEqual(SpelledPitchClass("D").onehot((-2,3)),
                        np.array([0, 0, 0, 0, 1, 0]))
        self.assertRaises(ValueError, lambda: SpelledPitchClass("A").onehot((-2,2)))
        self.assertEqual(SpelledPitchClass.from_onehot(SpelledPitchClass("F#").onehot((-8,8)), -8),
                         SpelledPitchClass("F#"))
        self.assertRaises(ValueError, lambda: SpelledPitchClass.from_onehot(np.array([1,0,1]), 0))

    def test_exceptions(self):
        self.assertRaises(TypeError, lambda: SpelledInterval("M2:0") < 0)
        self.assertRaises(TypeError, lambda: SpelledIntervalClass("M2") < 0)
        self.assertRaises(TypeError, lambda: SpelledPitch("C4") < 0)
        self.assertRaises(TypeError, lambda: SpelledPitchClass("C") < 0)
