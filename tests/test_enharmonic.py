from unittest import TestCase
from pitchtypes import Enharmonic, EnharmonicPitch, EnharmonicInterval, EnharmonicPitchClass, EnharmonicIntervalClass
import io
import sys


class TestEnharmonic(TestCase):

    def test_types(self):
        # make sure the types are linking correctly
        self.assertEqual(Enharmonic.Pitch, EnharmonicPitch)
        self.assertEqual(Enharmonic.Interval, EnharmonicInterval)
        self.assertEqual(Enharmonic.PitchClass, EnharmonicPitchClass)
        self.assertEqual(Enharmonic.IntervalClass, EnharmonicIntervalClass)
        self.assertEqual(EnharmonicPitch._base_type, Enharmonic)
        self.assertEqual(EnharmonicInterval._base_type, Enharmonic)
        self.assertEqual(EnharmonicPitchClass._base_type, Enharmonic)
        self.assertEqual(EnharmonicIntervalClass._base_type, Enharmonic)

    def test_init(self):
        for is_pitch in [True, False]:
            for is_class in [True, False]:
                if is_pitch:
                    if is_class:
                        p = EnharmonicPitchClass(61)
                    else:
                        p = EnharmonicPitch(61)
                else:
                    if is_class:
                        p = EnharmonicIntervalClass(61)
                    else:
                        p = EnharmonicInterval(61)
                # check base type is set on object
                self.assertEqual(p._base_type, Enharmonic)
                # check for pitch versus interval
                if is_pitch:
                    self.assertTrue(p.is_pitch)
                    self.assertFalse(p.is_interval)
                else:
                    self.assertFalse(p.is_pitch)
                    self.assertTrue(p.is_interval)
                # check class is correctly set
                if is_class:
                    self.assertTrue(p.is_class)
                else:
                    self.assertFalse(p.is_class)
                    pc = p.to_class()
                    self.assertTrue(pc.is_class)
                    if pc.is_pitch:
                        self.assertEqual("C#", str(pc))
                        self.assertEqual(1, int(pc))
                    else:
                        self.assertEqual(1, int(pc))
                # check str is correct
                if p.is_pitch:
                    if p.is_class:
                        self.assertEqual(str(p), "C#")
                        self.assertEqual(p.name(), "C#")
                        self.assertEqual(p.name(flat_sharp='sharp'), "C#")
                        self.assertEqual(p.name(flat_sharp='flat'), "Db")
                        self.assertRaises(ValueError, lambda: p.name(flat_sharp='invalid'))
                    else:
                        self.assertEqual(str(p), "C#4")
                        self.assertEqual(p.name(), "C#4")
                        self.assertEqual(p.name(flat_sharp='sharp'), "C#4")
                        self.assertEqual(p.name(flat_sharp='flat'), "Db4")
                        self.assertRaises(ValueError, lambda: p.name(flat_sharp='invalid'))
                else:
                    if p.is_class:
                        self.assertEqual(str(p), "+1")
                        self.assertEqual(p.name(), "+1")
                    else:
                        self.assertEqual(str(p), "+61")
                        self.assertEqual(p.name(), "+61")
        # raise for non-integer number input
        self.assertRaises(ValueError, lambda: Enharmonic(1.1, True, True))

    def test_name(self):
        e = Enharmonic(1, is_pitch=True, is_class=True)
        self.assertRaises(NotImplementedError, lambda: e.name())

    def test_convert_to_logfreq(self):
        for x in [EnharmonicPitch("C4"), EnharmonicPitchClass("C"), EnharmonicInterval(1), EnharmonicIntervalClass(1)]:
            x.convert_to_logfreq()

    def test_print_options(self):
        # bad input raises
        self.assertRaises(ValueError, lambda: EnharmonicPitch.print_options(flat_sharp="x"))
        self.assertRaises(ValueError, lambda: EnharmonicPitchClass.print_options(flat_sharp="x"))
        # not input prints info
        old_stdout = sys.stdout
        for cls in [EnharmonicPitch, EnharmonicPitchClass]:
            sys.stdout = out = io.StringIO()
            self.assertFalse(out.getvalue())
            cls.print_options()
            self.assertTrue(out.getvalue())
        sys.stdout = old_stdout

        p = EnharmonicPitch("C#4")
        pc = EnharmonicPitchClass("C#")
        # check default values
        self.assertEqual(EnharmonicPitch._print_as_int, False)
        self.assertEqual(EnharmonicPitch._print_flat_sharp, 'sharp')
        self.assertEqual(EnharmonicPitchClass._print_as_int, False)
        self.assertEqual(EnharmonicPitchClass._print_flat_sharp, 'sharp')
        self.assertEqual(p.name(), "C#4")
        self.assertEqual(pc.name(), "C#")
        # change for both
        Enharmonic.print_options(as_int=True, flat_sharp='flat')
        self.assertEqual(EnharmonicPitch._print_as_int, True)
        self.assertEqual(EnharmonicPitch._print_flat_sharp, 'flat')
        self.assertEqual(EnharmonicPitchClass._print_as_int, True)
        self.assertEqual(EnharmonicPitchClass._print_flat_sharp, 'flat')
        self.assertEqual(p.name(), "61")
        self.assertEqual(pc.name(), "1")
        # change for Pitch
        EnharmonicPitch.print_options(as_int=False)
        self.assertEqual(EnharmonicPitch._print_as_int, False)
        self.assertEqual(EnharmonicPitch._print_flat_sharp, 'flat')
        self.assertEqual(EnharmonicPitchClass._print_as_int, True)
        self.assertEqual(EnharmonicPitchClass._print_flat_sharp, 'flat')
        self.assertEqual(p.name(), "Db4")
        self.assertEqual(pc.name(), "1")
        # change for PitchClass
        EnharmonicPitchClass.print_options(as_int=False)
        self.assertEqual(EnharmonicPitch._print_as_int, False)
        self.assertEqual(EnharmonicPitch._print_flat_sharp, 'flat')
        self.assertEqual(EnharmonicPitchClass._print_as_int, False)
        self.assertEqual(EnharmonicPitchClass._print_flat_sharp, 'flat')
        self.assertEqual(p.name(), "Db4")
        self.assertEqual(pc.name(), "Db")

    # some other tests

    def test_init_2(self):
        EnharmonicPitch("C5")
        EnharmonicPitch(72)
        for p in ["C5", "B#4", "A###4", "Dbb5"]:
            self.assertEqual(EnharmonicPitch(p), EnharmonicPitch(72))
        for p in ["C5-", "B#b", "c5"]:
            self.assertRaises(ValueError, lambda: EnharmonicPitch(p))
        for midi_name_sharp, midi_name_flat, midi_number in zip(
                ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
                 "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5", ],
                ["C4", "Db4", "D4", "Eb4", "E4", "F4", "Gb4", "G4", "Ab4", "A4", "Bb4", "B4",
                 "C5", "Db5", "D5", "Eb5", "E5", "F5", "Gb5", "G5", "Ab5", "A5", "Bb5", "B5", ],
                range(60, 85)
        ):
            from_flat = EnharmonicPitch(midi_name_flat)
            from_sharp = EnharmonicPitch(midi_name_sharp)
            from_number = EnharmonicPitch(midi_number)
            self.assertEqual(from_flat, from_number)
            self.assertEqual(from_sharp, from_number)
            self.assertEqual(midi_number, int(from_number))
            self.assertEqual(from_flat.to_class().value, midi_number % 12)
            self.assertEqual(from_sharp.to_class().value, midi_number % 12)

    def test_freq(self):
        self.assertEqual(EnharmonicPitch("A4").freq(), 440)
        self.assertEqual(EnharmonicPitch("A5").freq(), 880)

    def test_arithmetics(self):
        c4 = EnharmonicPitch("C4")
        d4 = EnharmonicPitch("D4")
        g4 = EnharmonicPitch("G4")
        icg = c4 - g4
        idc = d4 - c4
        self.assertEqual(icg, EnharmonicInterval(-7))
        self.assertEqual(idc, EnharmonicInterval(2))

        pc_c4 = c4.to_class()
        pc_d4 = d4.to_class()
        pc_g4 = g4.to_class()
        pci_cg = pc_c4 - pc_g4
        pci_dc = pc_d4 - pc_c4

        self.assertEqual(icg.to_class(), EnharmonicIntervalClass(icg.value))

        self.assertEqual(pci_cg, EnharmonicIntervalClass(5))
        self.assertEqual(pci_cg, EnharmonicIntervalClass(-7))
        self.assertEqual(pci_cg.value, 5)

        self.assertEqual(pci_dc, EnharmonicIntervalClass(2))
        self.assertEqual(pci_dc, EnharmonicIntervalClass(-10))
        self.assertEqual(int(pci_dc), 2)
