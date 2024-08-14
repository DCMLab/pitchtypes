import io
import sys
from unittest import TestCase

from pitchtypes import Generic, GenericPitch, GenericInterval, GenericPitchClass, GenericIntervalClass


class TestGeneric(TestCase):

    def test_types(self):
        # make sure the types are linking correctly
        self.assertEqual(Generic.Pitch, GenericPitch)
        self.assertEqual(Generic.Interval, GenericInterval)
        self.assertEqual(Generic.PitchClass, GenericPitchClass)
        self.assertEqual(Generic.IntervalClass, GenericIntervalClass)
        self.assertEqual(GenericPitch._base_type, Generic)
        self.assertEqual(GenericInterval._base_type, Generic)
        self.assertEqual(GenericPitchClass._base_type, Generic)
        self.assertEqual(GenericIntervalClass._base_type, Generic)

    def test_init(self):
        for is_pitch in [True, False]:
            for is_class in [True, False]:
                if is_pitch:
                    if is_class:
                        p = GenericPitchClass(39)
                    else:
                        p = GenericPitch(39)
                else:
                    if is_class:
                        p = GenericIntervalClass(39)
                    else:
                        p = GenericInterval(39)
                # check base type is set on object
                self.assertEqual(p._base_type, Generic)
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
                        self.assertEqual("G", str(pc))
                        self.assertEqual(4, int(pc))
                    else:
                        self.assertEqual(4, int(pc))
                # check str is correct
                if p.is_pitch:
                    if p.is_class:
                        self.assertEqual(str(p), "G")
                        self.assertEqual(p.name(), "G")
                    else:
                        self.assertEqual(str(p), "G4")
                        self.assertEqual(p.name(), "G4")
                else:
                    if p.is_class:
                        self.assertEqual(str(p), "4")
                        self.assertEqual(p.name(), "4")
                    else:
                        self.assertEqual(str(p), "39")
                        self.assertEqual(p.name(), "39")
        # raise for non-integer number input
        self.assertRaises(ValueError, lambda: Generic(1.1, True, True))

    def test_name(self):
        e = Generic(1, is_pitch=True, is_class=True)
        self.assertRaises(NotImplementedError, lambda: e.name())

    def test_octave_and_freq(self):
        for i in range(-3, 10):
            pitch = GenericPitch(f"G{i}")
            self.assertEqual(pitch.octaves(), i)
            interval = pitch - GenericPitch("C4")
            self.assertEqual(interval.octaves(), i - 4)

    def test_print_options(self):
        # not input prints info
        old_stdout = sys.stdout
        for cls in [GenericPitch, GenericPitchClass]:
            sys.stdout = out = io.StringIO()
            self.assertFalse(out.getvalue())
            cls.print_options()
            self.assertTrue(out.getvalue())
        sys.stdout = old_stdout

        p = GenericPitch("G4")
        pc = GenericPitchClass("G")
        # check default values
        self.assertEqual(GenericPitch._print_as_int, False)
        self.assertEqual(GenericPitchClass._print_as_int, False)
        self.assertEqual(p.name(), "G4")
        self.assertEqual(pc.name(), "G")
        # change for both
        Generic.print_options(as_int=True)
        self.assertEqual(GenericPitch._print_as_int, True)
        self.assertEqual(GenericPitchClass._print_as_int, True)
        self.assertEqual(p.name(), "39")
        self.assertEqual(pc.name(), "4")
        # change for Pitch
        GenericPitch.print_options(as_int=False)
        self.assertEqual(GenericPitch._print_as_int, False)
        self.assertEqual(GenericPitchClass._print_as_int, True)
        self.assertEqual(p.name(), "G4")
        self.assertEqual(pc.name(), "4")
        # change for PitchClass
        GenericPitchClass.print_options(as_int=False)
        self.assertEqual(GenericPitch._print_as_int, False)
        self.assertEqual(GenericPitchClass._print_as_int, False)
        self.assertEqual(p.name(), "G4")
        self.assertEqual(pc.name(), "G")

    # some other tests

    def test_init_2(self):
        GenericPitch("C5")
        GenericPitch(42)
        for p in ["C5", "C#5", "C###5", "Cbb5"]:
            self.assertEqual(GenericPitch(p), GenericPitch(42))
        for p in ["C5-", "C#b", "c5"]:
            self.assertRaises(ValueError, lambda: GenericPitch(p))
        for pitch_name, step_number in zip(
                ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5",],
                range(35, 49)
        ):
            from_pitch_name = GenericPitch(pitch_name)
            from_number = GenericPitch(step_number)
            self.assertEqual(from_pitch_name, from_number)
            self.assertEqual(step_number, int(from_number))
            self.assertEqual(from_pitch_name.to_class().value, step_number % 7)

    def test_arithmetics(self):
        c4 = GenericPitch("C4")
        d4 = GenericPitch("D4")
        g4 = GenericPitch("G4")
        icg = c4 - g4
        idc = d4 - c4
        self.assertEqual(icg, GenericInterval(-4))
        self.assertEqual(idc, GenericInterval(1))

        pc_c4 = c4.to_class()
        pc_d4 = d4.to_class()
        pc_g4 = g4.to_class()
        pci_cg = pc_c4 - pc_g4
        pci_dc = pc_d4 - pc_c4

        self.assertEqual(icg.to_class(), GenericIntervalClass(icg.value))

        self.assertEqual(pci_cg, GenericIntervalClass(3))
        self.assertEqual(pci_cg, GenericIntervalClass(-4))
        self.assertEqual(pci_cg.value, 3)

        self.assertEqual(pci_dc, GenericIntervalClass(1))
        self.assertEqual(pci_dc, GenericIntervalClass(-6))
        self.assertEqual(int(pci_dc), 1)
