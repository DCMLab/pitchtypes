from unittest import TestCase
from pitchtypes import Enharmonic


class TestEnharmonic(TestCase):

    def test_init(self):
        for is_pitch in [True, False, None]:
            for is_class in [True, False, None]:
                p = Enharmonic(61, is_pitch=is_pitch, is_class=is_class)
                # check for pitch versus interval
                if is_pitch is True or is_pitch is None:
                    self.assertTrue(p.is_pitch())
                elif is_pitch is False:
                    self.assertFalse(p.is_pitch())
                # check class is correctly set
                if is_class is True:
                    self.assertTrue(p.is_class())
                elif is_class is False or is_class is None:
                    self.assertFalse(p.is_class())
                    pc = p.to_class()
                    self.assertTrue(pc.is_class())
                    if pc.is_pitch():
                        self.assertEqual(str(pc), "C#")
                    else:
                        self.assertEqual(str(pc), "+1")
                # check str is correct
                if p.is_pitch():
                    if p.is_class():
                        self.assertEqual(str(p), "C#")
                        self.assertEqual(p.name(), "C#")
                        self.assertEqual(p.name(sharp_flat='sharp'), "C#")
                        self.assertEqual(p.name(sharp_flat='flat'), "Db")
                        self.assertRaises(ValueError, lambda: p.name(sharp_flat='invalid'))
                    else:
                        self.assertEqual(str(p), "C#4")
                        self.assertEqual(p.name(), "C#4")
                        self.assertEqual(p.name(sharp_flat='sharp'), "C#4")
                        self.assertEqual(p.name(sharp_flat='flat'), "Db4")
                        self.assertRaises(ValueError, lambda: p.name(sharp_flat='invalid'))
                else:
                    if p.is_class():
                        self.assertEqual(str(p), "+1")
                        self.assertEqual(p.name(), "+1")
                        self.assertRaises(ValueError, lambda: p.name(sharp_flat='sharp'))
                        self.assertRaises(ValueError, lambda: p.name(sharp_flat='flat'))
                    else:
                        self.assertEqual(str(p), "+61")
                        self.assertEqual(p.name(), "+61")
                        self.assertRaises(ValueError, lambda: p.name(sharp_flat='sharp'))
                        self.assertRaises(ValueError, lambda: p.name(sharp_flat='flat'))

    # some other tests

    def test_init_2(self):
        for p in ["C5", "B#4", "A###4", "Dbb5"]:
            self.assertEqual(Enharmonic(p), Enharmonic(72))
        for p in ["C5-", "B#b", "c5"]:
            self.assertRaises(ValueError, lambda: Enharmonic(p))
        for midi_name_sharp, midi_name_flat, midi_number in zip(
                ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
                 "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5", ],
                ["C4", "Db4", "D4", "Eb4", "E4", "F4", "Gb4", "G4", "Ab4", "A4", "Bb4", "B4",
                 "C5", "Db5", "D5", "Eb5", "E5", "F5", "Gb5", "G5", "Ab5", "A5", "Bb5", "B5", ],
                range(60, 85)
        ):
            from_flat = Enharmonic(midi_name_flat)
            from_sharp = Enharmonic(midi_name_sharp)
            from_number = Enharmonic(midi_number)
            self.assertEqual(from_flat, from_number)
            self.assertEqual(from_sharp, from_number)
            self.assertEqual(midi_number, int(from_number))
            self.assertEqual(from_flat.to_class()._value, midi_number % 12)
            self.assertEqual(from_sharp.to_class()._value, midi_number % 12)

    def test_freq(self):
        self.assertEqual(Enharmonic("A4").freq(), 440)
        self.assertEqual(Enharmonic("A5").freq(), 880)

    def test_arithmetics(self):
        c4 = Enharmonic("C4")
        d4 = Enharmonic("D4")
        g4 = Enharmonic("G4")
        icg = c4 - g4
        idc = d4 - c4
        self.assertEqual(icg, Enharmonic(-7, is_pitch=False))
        self.assertEqual(idc, Enharmonic(2, is_pitch=False))

        pc_c4 = c4.to_class()
        pc_d4 = d4.to_class()
        pc_g4 = g4.to_class()
        pci_cg = pc_c4 - pc_g4
        pci_dc = pc_d4 - pc_c4

        self.assertEqual(icg.to_class(), Enharmonic(icg._value, is_pitch=False, is_class=True))

        self.assertEqual(pci_cg, Enharmonic(5, is_pitch=False, is_class=True))
        self.assertEqual(pci_cg, Enharmonic(-7, is_pitch=False, is_class=True))
        self.assertEqual(pci_cg._value, 5)

        self.assertEqual(pci_dc, Enharmonic(2, is_pitch=False, is_class=True))
        self.assertEqual(pci_dc, Enharmonic(-10, is_pitch=False, is_class=True))
        self.assertEqual(int(pci_dc), 2)
