from unittest import TestCase
from pitchtypes import Pitch, Interval
from pitchtypes import EnharmonicPitch, EnharmonicPitchInterval
from pitchtypes import LogFreqPitch
from pitchtypes import prange
import numpy as np


class TestPitch(TestCase):

    def test_create_interval_class(self):

        # check operations/failure for both cases
        for with_interval in [True, False]:

            # create derived pitch class
            class NewPitch(Pitch):
                pass

            # create pitch objects
            p1 = NewPitch(np.random.randint(-10, 10))
            p2 = NewPitch(np.random.randint(-10, 10))

            if with_interval:
                # create interval class
                @NewPitch.associate_interval_type()
                class NewBaseInterval(Interval):
                    pass
                # assert second call raises an error
                try:
                    @NewPitch.associate_interval_type()
                    class NewBaseInterval(Interval):
                        pass
                except AttributeError:
                    pass
                else:
                    self.fail("Should have raise AttributeError")
                # assert overwriting can be forced
                @NewPitch.associate_interval_type(overwrite_interval_type=True)
                class NewBaseInterval(Interval):
                    pass

                # check class assignment
                self.assertEqual(NewPitch._associated_interval_type, NewBaseInterval)
                self.assertEqual(NewBaseInterval._associated_pitch_type, NewPitch)

                # create interval objects
                i1 = NewBaseInterval(np.random.randint(-10, 10))
                i2 = NewBaseInterval(np.random.randint(-10, 10))

                # interval class corresponds to interval class below
                NewBaseInterval = NewBaseInterval


                # transform a pitch to an interval and vice versa
                self.assertEqual(NewBaseInterval(p1._value), p1.to_interval())
                self.assertEqual(NewPitch(i1._value), i1.to_pitch())

                # check basic operations (all combinations of pitch/interval and +/-; multiplication for intervals)
                self.assertRaises(TypeError, lambda: p1 + p2)
                self.assertEqual(p1 - p2, NewBaseInterval(p1._value - p2._value))
                self.assertEqual(i1 + i2, NewBaseInterval(i1._value + i2._value))
                self.assertEqual(i1 - i2, NewBaseInterval(i1._value - i2._value))
                self.assertEqual(p1 + i1, NewPitch(p1._value + i1._value))
                self.assertEqual(p1 - i1, NewPitch(p1._value - i1._value))
                self.assertRaises(TypeError, lambda: i1 + p1)
                self.assertRaises(TypeError, lambda: i1 - p1)
                self.assertEqual(2 * i1, NewBaseInterval(2 * i1._value))
                self.assertEqual(i1 * 2, NewBaseInterval(2 * i1._value))
            else:
                self.assertRaises(AttributeError, lambda: p1 + p2)
                self.assertRaises(AttributeError, lambda: p1 - p2)
                self.assertRaises(AttributeError, lambda: p1.to_interval())


class TestEnharmonicPitch(TestCase):

    def test_init(self):
        for p in ["C5", "B#4", "A###4", "Dbb5"]:
            self.assertEqual(EnharmonicPitch(p), EnharmonicPitch(72))
        for p in ["C5-", "B#b", "c5"]:
            self.assertRaises(ValueError, lambda: EnharmonicPitch(p))
        for midi_name_sharp, midi_name_flat, midi_number in zip(
                ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
                 "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",],
                ["C4", "Db4", "D4", "Eb4", "E4", "F4", "Gb4", "G4", "Ab4", "A4", "Bb4", "B4",
                 "C5", "Db5", "D5", "Eb5", "E5", "F5", "Gb5", "G5", "Ab5", "A5", "Bb5", "B5",],
                range(60, 85)
        ):
            from_flat = EnharmonicPitch(midi_name_flat)
            from_sharp = EnharmonicPitch(midi_name_sharp)
            from_number = EnharmonicPitch(midi_number)
            self.assertEqual(from_flat, from_number)
            self.assertEqual(from_sharp, from_number)
            self.assertEqual(midi_number, int(from_number))
            self.assertEqual(from_flat.to_pitch_class()._value, midi_number % 12)
            self.assertEqual(from_sharp.to_pitch_class()._value, midi_number % 12)

    def test_freq(self):
        self.assertEqual(EnharmonicPitch("A4").freq(), 440)
        self.assertEqual(EnharmonicPitch("A5").freq(), 880)

    def test_arithmetics(self):
        c4 = EnharmonicPitch("C4")
        d4 = EnharmonicPitch("D4")
        g4 = EnharmonicPitch("G4")
        icg = c4 - g4
        idc = d4 - c4
        self.assertEqual(icg, EnharmonicPitchInterval(-7))
        self.assertEqual(idc, EnharmonicPitchInterval(2))

        pc_c4 = c4.to_pitch_class()
        pc_d4 = d4.to_pitch_class()
        pc_g4 = g4.to_pitch_class()
        pci_cg = pc_c4 - pc_g4
        pci_dc = pc_d4 - pc_c4

        self.assertEqual(icg.to_interval_class(), EnharmonicPitchInterval(icg._value, is_interval_class=True))

        self.assertEqual(pci_cg, EnharmonicPitchInterval(5, is_interval_class=True))
        self.assertEqual(pci_cg, EnharmonicPitchInterval(-7, is_interval_class=True))
        self.assertEqual(pci_cg._value, 5)

        self.assertEqual(pci_dc, EnharmonicPitchInterval(2, is_interval_class=True))
        self.assertEqual(pci_dc, EnharmonicPitchInterval(-10, is_interval_class=True))
        self.assertEqual(int(pci_dc), 2)

        self.assertEqual(pc_c4.pitch_class_phase(), 0)
        self.assertEqual(pc_g4.pitch_class_phase(), 7 / 12)
        self.assertEqual(pc_d4.pitch_class_phase(), 2 / 12)

        self.assertEqual(pci_cg.phase_diff(), 5 / 12)
        self.assertEqual(pci_dc.phase_diff(), 2 / 12)

    def test_range(self):
        p1 = EnharmonicPitch("C4")
        p2 = EnharmonicPitch("C5")
        i1 = EnharmonicPitch("C#4") - EnharmonicPitch("C4")
        i2 = EnharmonicPitch("D4") - EnharmonicPitch("C4")

        self.assertEqual([int(p) for p in prange(p1, p2, i1)], list(range(60, 72)))
        self.assertEqual([int(p) for p in prange(p1, p2, i2)], list(range(60, 72, 2)))
        self.assertEqual([int(p) for p in prange(p1, p2, i1, endpoint=True)], list(range(60, 73)))
        self.assertEqual([int(p) for p in prange(p1, p2, i2, endpoint=True)], list(range(60, 73, 2)))


class TestLogFreqPitch(TestCase):

    def test_against_MIDI(self):
        c4 = EnharmonicPitch("C4")
        d4 = EnharmonicPitch("D4")
        lc4 = c4.convert_to(LogFreqPitch)
        ld4 = d4.convert_to(LogFreqPitch)
        pci = d4.to_pitch_class() - c4.to_pitch_class()
        pci_ = pci
        lpci = ld4.to_pitch_class() - lc4.to_pitch_class()
        lpci_ = lpci
        for _ in range(12):
            # cannot use simple equality check because special case -0.5 and 0.5 have to evaluate to equal, too
            # same point on unit circle (e.g. 0.2 == -0.8)
            self.assertAlmostEqual(pci_.phase_diff() % 1, lpci_.phase_diff() % 1)
            # same magnitude (e.g. 0.2 == -0.2)
            self.assertAlmostEqual(abs(pci_.phase_diff()), abs(lpci_.phase_diff()))
            pci_ = pci_ + pci
            lpci_ = lpci_ + lpci


class TestConverters(TestCase):

    def test_converters(self):
        # define classes A and B with a converter A-->B
        class PitchA(Pitch):
            """Use integer representation: 5 --> 5"""
            # def __init__(self, value, *args, **kwargs):
            #     super().__init__(int(value), *args, **kwargs)
        @PitchA.associate_interval_type()
        class PitchAInterval(Interval):
            pass

        class PitchB(Pitch):
            """Use string representation: 5 --> '5'"""
            @staticmethod
            def convert_to_PitchA(pitch_b):
                return PitchA(int(pitch_b._value))
            # def __init__(self, value, *args, **kwargs):
            #     super().__init__(str(value), *args, **kwargs)
            def __sub__(self, other):
                self._assert_has_associated_interval_type()
                try:
                    self._assert_is_pitch(other)
                    return self._associated_interval_type(int(self._value) - int(other._value))
                except TypeError:
                    self._assert_is_interval(other)
                    return self.__class__(int(self._value) - int(other._value))
            def to_interval(self):
                return self._associated_interval_type(int(self._value))
        Pitch.register_converter(PitchB, PitchA, PitchB.convert_to_PitchA)
        @PitchB.associate_interval_type()
        class PitchBInterval(Interval):
            pass

        # instantiate objects and check (in)equality and conversion)
        a = PitchA(5)
        ai = a.to_interval()
        b = PitchB("5")
        bi = b.to_interval()
        self.assertNotEqual(a, b)
        self.assertNotEqual(ai, bi)
        self.assertEqual(a, b.convert_to(PitchA))
        self.assertEqual(ai, bi.convert_to(PitchAInterval))
        self.assertEqual(a, PitchA(b))
        self.assertEqual(ai, PitchAInterval(bi))

        # define another class C with converter C-->A
        class PitchC(Pitch):
            """Use list representation: 5 --> [0, 0, 0, 0, 0]"""
            @staticmethod
            def convert_to_PitchB(pitch_c):
                return PitchB(str(len(pitch_c._value)))
            def __init__(self, value, *args, **kwargs):
                if isinstance(value, int):
                    value = [0] * value
                super().__init__(value, *args, **kwargs)
            def __sub__(self, other):
                self._assert_has_associated_interval_type()
                try:
                    self._assert_is_pitch(other)
                    return self._associated_interval_type(len(self._value) - len(other._value))
                except TypeError:
                    self._assert_is_interval(other)
                    return self.__class__([0] * (len(self._value) - len(other._value)))
            def to_interval(self):
                return self._associated_interval_type(len(self._value))
        @PitchC.associate_interval_type()
        class PitchCInterval(Interval):
            pass

        # instantiate object and check (in)equality
        c = PitchC([0, 0, 0, 0, 0])
        ci = c.to_interval()
        self.assertNotEqual(b, c)
        self.assertNotEqual(bi, ci)
        self.assertNotEqual(c, a)
        self.assertNotEqual(ci, ai)

        # register without and with extending implicit converters and check conversion
        for extend_implicit_converters in [False, True]:
            # we avoid an error on the second registration we use give an explicit value to
            # overwrite_explicit_converters (could also be True, just not None)
            Pitch.register_converter(PitchC, PitchB, PitchC.convert_to_PitchB,
                                     create_implicit_converters=extend_implicit_converters,
                                     overwrite_explicit_converters=False)
            self.assertEqual(b, c.convert_to(PitchB))
            self.assertEqual(bi, ci.convert_to(PitchBInterval))
            self.assertEqual(b, PitchB(c))
            self.assertEqual(bi, PitchBInterval(ci))
            if not extend_implicit_converters:
                # should NOT be created implicitly
                self.assertRaises(NotImplementedError, lambda: c.convert_to(PitchA))
                self.assertRaises(NotImplementedError, lambda: ci.convert_to(PitchAInterval))
                self.assertRaises(NotImplementedError, lambda: PitchA(c))
                self.assertRaises(NotImplementedError, lambda: PitchAInterval(ci))
            else:
                # SHOULD be created implicitly
                self.assertEqual(c.convert_to(PitchA), a)
                self.assertEqual(ci.convert_to(PitchAInterval), ai)
                self.assertEqual(PitchA(c), a)
                self.assertEqual(PitchAInterval(ci), ai)

        # define a direct converter C-->A which returns a version scaled by 10
        # (to detect whether the old or now converter was used)
        def direct_but_wrong_converter_from_C_to_A(c):
            return PitchA(10 * len(c._value))
        # check again that the implicit converter exists
        self.assertEqual(c.convert_to(PitchA), a)
        self.assertEqual(ci.convert_to(PitchAInterval), ai)
        self.assertEqual(PitchA(c), a)
        self.assertEqual(PitchAInterval(ci), ai)
        # register the converter, which should replace the existing implicit converter
        Pitch.register_converter(PitchC, PitchA, direct_but_wrong_converter_from_C_to_A)

        # check
        # via convert_to
        self.assertEqual(type(a), type(c.convert_to(PitchA)))
        self.assertEqual(type(ai), type(ci.convert_to(PitchAInterval)))
        self.assertNotEqual(a, c.convert_to(PitchA))
        self.assertNotEqual(ai, ci.convert_to(PitchAInterval))
        self.assertEqual(PitchA(50), c.convert_to(PitchA))
        self.assertEqual(PitchAInterval(50), ci.convert_to(PitchAInterval))
        # via __init__
        self.assertEqual(type(a), type(PitchA(c)))
        self.assertEqual(type(ai), type(PitchAInterval(ci)))
        self.assertNotEqual(a, PitchA(c))
        self.assertNotEqual(ai, PitchAInterval(ci))
        self.assertEqual(PitchA(50), PitchA(c))
        self.assertEqual(PitchAInterval(50), PitchAInterval(ci))

        # trying to re-register should raise a ValueError because a direct converter now exists
        self.assertRaises(ValueError,
                          lambda: Pitch.register_converter(PitchC, PitchA, direct_but_wrong_converter_from_C_to_A))
        # but overwriting can be forced
        Pitch.register_converter(PitchC, PitchA, direct_but_wrong_converter_from_C_to_A,
                                 overwrite_explicit_converters=True)
