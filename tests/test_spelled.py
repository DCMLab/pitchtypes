from unittest import TestCase
from pitchtypes import Spelled

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
        "P4", "P1", "P5", "M2", "M6", "M3", "M7",
        "A4", "A1", "A5", "A2", "A6", "A3", "A7",
        "AA4", "AA1", "AA5", "AA2", "AA6", "AA3", "AA7",
        "AAA4", "AAA1", "AAA5", "AAA2", "AAA6", "AAA3", "AAA7"
    ]

    def test_init(self):
        for is_class in [False, True]:
            for idx, p in enumerate(self.line_of_fifths):
                if not is_class:
                    p += "4"
                pp = Spelled(p)
                self.assertEqual(is_class, pp.is_class)
                self.assertTrue(pp.is_pitch)
                self.assertFalse(pp.is_interval)
                self.assertEqual(str(pp), p)
                self.assertEqual(pp.fifth_steps(), idx - 26)
            for idx, (i, ir) in enumerate(zip(self.line_of_intervals, reversed(self.line_of_intervals))):
                i = "+" + i
                ir = "-" + ir
                if not is_class:
                    i += ":4"
                    ir += ":4"
                ii = Spelled(i)
                iir = Spelled(ir)
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
            p = Spelled(p)
            i = Spelled("+" + i)
            ref = Spelled("C")
            delta = p - ref
            self.assertEqual(delta, i)
            self.assertEqual(ref + delta, p)

            p1 = Spelled("C#4")
            p2 = Spelled("Gb5")
            # i1 = Spelled("+dd5:1")
            # i2 = Spelled("-AA4:-1")
            # print(i1, i2)
            # i = p2 - p1
            # print(i)
            # print(f"{p2} + {i} = {p2 + i}")
            # print(f"{p2} - {i} = {p2 - i}")
            # print(i)
            # print(f"{i} - {i} = {i - i}")
            # print(f"{i} + {i} = {i + i}")
            self.assertRaises(TypeError, lambda: p1 + p2)
            self.assertRaises(TypeError, lambda: Spelled("G") - Spelled("G4"))

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
