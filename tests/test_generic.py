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
                        p = GenericPitchClass(61)
                    else:
                        p = GenericPitch(61)
                else:
                    if is_class:
                        p = GenericIntervalClass(61)
                    else:
                        p = GenericInterval(61)
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
                        self.assertEqual("A", str(pc))
                        self.assertEqual(1, int(pc))
                    else:
                        self.assertEqual(1, int(pc))
                # check str is correct
                if p.is_pitch:
                    if p.is_class:
                        self.assertEqual(str(p), "A")
                        self.assertEqual(p.name(), "A")
                        self.assertRaises(ValueError, lambda: p.name(flat_sharp='invalid'))
                    else:
                        self.assertEqual(str(p), "A7")
                        self.assertEqual(p.name(), "A7")
                        self.assertRaises(ValueError, lambda: p.name(flat_sharp='invalid'))
                else:
                    if p.is_class:
                        self.assertEqual(str(p), "5")
                        self.assertEqual(p.name(), "5")
                    else:
                        self.assertEqual(str(p), "61")
                        self.assertEqual(p.name(), "61")
        # raise for non-integer number input
        self.assertRaises(ValueError, lambda: Generic(1.1, True, True))

    def test_name(self):
        e = Generic(1, is_pitch=True, is_class=True)
        self.assertRaises(NotImplementedError, lambda: e.name())

    def test_octave_and_freq(self):
        for i in range(-3, 10):
            pitch = GenericPitch(f"C{i}")
            self.assertEqual(pitch.octaves(), i)
            interval = pitch - GenericPitch("C4")
            self.assertEqual(interval.octaves(), i - 4)

    def test_convert_to_logfreq(self):
        self.assertRaises(NotImplementedError, lambda: Generic("C", True, True).convert_to_logfreq())
        for x in [GenericPitch("C4"), GenericPitchClass("C"), GenericInterval(1), GenericIntervalClass(1)]:
            x.convert_to_logfreq()
            if not x.is_class:
                self.assertAlmostEqual(float(x.to_class().convert_to_logfreq()),
                                       float(x.convert_to_logfreq().to_class()))

    def test_print_options(self):
        # bad input raises
        self.assertRaises(ValueError, lambda: GenericPitch.print_options(flat_sharp="x"))
        self.assertRaises(ValueError, lambda: GenericPitchClass.print_options(flat_sharp="x"))
        # not input prints info
        old_stdout = sys.stdout
        for cls in [GenericPitch, GenericPitchClass]:
            sys.stdout = out = io.StringIO()
            self.assertFalse(out.getvalue())
            cls.print_options()
            self.assertTrue(out.getvalue())
        sys.stdout = old_stdout

        p = GenericPitch("C4")
        pc = GenericPitchClass("C")
        # check default values
        self.assertEqual(GenericPitch._print_as_int, False)
        self.assertEqual(GenericPitchClass._print_as_int, False)
        self.assertEqual(p.name(), "C4")
        self.assertEqual(pc.name(), "C")
        # change for both
        self.assertEqual(GenericPitch._print_as_int, True)
        self.assertEqual(GenericPitchClass._print_as_int, True)
        self.assertEqual(p.name(), "61")
        self.assertEqual(pc.name(), "1")
        # change for Pitch
        GenericPitch.print_options(as_int=False)
        self.assertEqual(GenericPitch._print_as_int, False)
        self.assertEqual(GenericPitchClass._print_as_int, True)
        self.assertEqual(p.name(), "C4")
        self.assertEqual(pc.name(), "C")
        # change for PitchClass
        GenericPitchClass.print_options(as_int=False)
        self.assertEqual(GenericPitch._print_as_int, False)
        self.assertEqual(GenericPitchClass._print_as_int, False)
        self.assertEqual(p.name(), "C4")
        self.assertEqual(pc.name(), "C")

    # some other tests

    def test_init_2(self):
        GenericPitch("C5")
        GenericPitch(72)
        for p in ["C5", "B#4", "A###4", "Dbb5"]:
            self.assertEqual(GenericPitch(p), GenericPitch(72))
        for p in ["C5-", "B#b", "c5"]:
            self.assertRaises(ValueError, lambda: GenericPitch(p))
        for midi_name_sharp, midi_name_flat, midi_number in zip(
                ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
                 "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5", ],
                ["C4", "Db4", "D4", "Eb4", "E4", "F4", "Gb4", "G4", "Ab4", "A4", "Bb4", "B4",
                 "C5", "Db5", "D5", "Eb5", "E5", "F5", "Gb5", "G5", "Ab5", "A5", "Bb5", "B5", ],
                range(60, 85)
        ):
            from_flat = GenericPitch(midi_name_flat)
            from_sharp = GenericPitch(midi_name_sharp)
            from_number = GenericPitch(midi_number)
            self.assertEqual(from_flat, from_number)
            self.assertEqual(from_sharp, from_number)
            self.assertEqual(midi_number, int(from_number))
            self.assertEqual(from_flat.to_class().value, midi_number % 7)
            self.assertEqual(from_sharp.to_class().value, midi_number % 7)

    def test_freq(self):
        self.assertEqual(GenericPitch("A4").freq(), 440)
        self.assertEqual(GenericPitch("A5").freq(), 880)

    def test_arithmetics(self):
        c4 = GenericPitch("C4")
        d4 = GenericPitch("D4")
        g4 = GenericPitch("G4")
        icg = c4 - g4
        idc = d4 - c4
        self.assertEqual(icg, GenericInterval(-7))
        self.assertEqual(idc, GenericInterval(2))

        pc_c4 = c4.to_class()
        pc_d4 = d4.to_class()
        pc_g4 = g4.to_class()
        pci_cg = pc_c4 - pc_g4
        pci_dc = pc_d4 - pc_c4

        self.assertEqual(icg.to_class(), GenericIntervalClass(icg.value))

        self.assertEqual(pci_cg, GenericIntervalClass(5))
        self.assertEqual(pci_cg, GenericIntervalClass(-7))
        self.assertEqual(pci_cg.value, 5)

        self.assertEqual(pci_dc, GenericIntervalClass(2))
        self.assertEqual(pci_dc, GenericIntervalClass(-10))
        self.assertEqual(int(pci_dc), 2)
