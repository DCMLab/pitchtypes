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
                self.assertEqual(pp.fifth_steps(), idx - 26)
            # create interval (class) objects
            for idx, (i, ir) in enumerate(zip(self.line_of_intervals, reversed(self.line_of_intervals))):
                i = "+" + i
                ir = "-" + ir
                if is_class:
                    ii = SpelledIntervalClass(i)
                    iir = SpelledIntervalClass(ir)
                    ii.convert_to_enharmonic()
                    self.assertEqual(ii.convert_to_enharmonic(), Enharmonic.IntervalClass(i))
                    self.assertEqual(ii.convert_to(Enharmonic.IntervalClass), Enharmonic.IntervalClass(i))
                else:
                    i += ":4"
                    ir += ":4"
                    ii = SpelledInterval(i)
                    iir = SpelledInterval(ir)
                    # check conversion to enharmonic
                    self.assertEqual(ii.convert_to_enharmonic(), Enharmonic.Interval(i))
                    self.assertEqual(ii.convert_to(Enharmonic.Interval), Enharmonic.Interval(i))
                self.assertEqual(ii._base_type, Spelled)
                self.assertEqual(iir._base_type, Spelled)
                self.assertEqual(is_class, ii.is_class)
                self.assertEqual(is_class, iir.is_class)
                self.assertEqual(ii, iir)
                self.assertFalse(ii.is_pitch)
                self.assertTrue(ii.is_interval)
                self.assertEqual(str(ii), i)
                self.assertEqual(ii.name(), i)
                self.assertEqual(iir.name(), i)
                if is_class:
                    self.assertEqual(ii.name(negative=True), ir)
                    self.assertEqual(iir.name(negative=True), ir)
                else:
                    self.assertRaises(ValueError, lambda: ii.name(negative=True))
                    self.assertRaises(ValueError, lambda: iir.name(negative=True))
                self.assertEqual(ii.fifth_steps(), idx - 26)

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
            # i1 = Spelled("+dd5:1")
            # i2 = Spelled("-aa4:-1")
            # print(i1, i2)
            # i = p2 - p1
            # print(i)
            # print(f"{p2} + {i} = {p2 + i}")
            # print(f"{p2} - {i} = {p2 - i}")
            # print(i)
            # print(f"{i} - {i} = {i - i}")
            # print(f"{i} + {i} = {i + i}")
            self.assertRaises(TypeError, lambda: p1 + p2)
            self.assertRaises(TypeError, lambda: SpelledPitchClass("G") - SpelledPitch("G4"))

        # for idx_1, p_1 in enumerate(line_of_fifths):
        #     pp_1 = Spelled(p_1)
        #     self.assertTrue(pp_1.is_pitch)
        #     self.assertTrue(pp_1.is_class)
        #     # self.assertEqual(str(pp_1), p_1)
        #     self.assertEqual(pp_1.fifth_steps(), idx_1 - 22)
        #
        #     print(f"reference point: {p_1}")
        #     for idx_2, p_2 in enumerate(line_of_fifths):
        #         pp_2 = Spelled(p_2)
        #         print(f"{pp_2} - {pp_1} = {pp_2 - pp_1}")
        #     print("")

    # def test_to_class(self):
    #     self.fail()
    #
    # def test_name(self):
    #     self.fail()
    #
    # def test_fifth_steps(self):
    #     self.fail()
    #
    # def test_octave(self):
    #     self.fail()
