from unittest import TestCase
from pitchtypes import AbstractBase, Enharmonic, Converters


class TestConverters(TestCase):

    def test_converters(self):
        # define three types A, B, and C
        class TypeA(AbstractBase): pass

        class TypeB(AbstractBase): pass

        class TypeC(AbstractBase): pass

        # register converter A --> B
        Converters.register_converter(from_type=TypeA,
                                        to_type=TypeB,
                                        conv_func=lambda pitch_a: TypeB(pitch_a.value,
                                                                        pitch_a.is_pitch,
                                                                        pitch_a.is_class))
        # check conversion works
        self.assertEqual(TypeA("foo", True, False).convert_to(TypeB), TypeB("foo", True, False))

        # register converter B --> C
        Converters.register_converter(from_type=TypeB,
                                        to_type=TypeC,
                                        conv_func=lambda pitch_b: TypeC(pitch_b.value,
                                                                        pitch_b.is_pitch,
                                                                        pitch_b.is_class))
        # check conversion works
        self.assertEqual(TypeB("bar", True, False).convert_to(TypeC), TypeC("bar", True, False))

        # check that conversion A --> C DOES NOT work!
        self.assertRaises(NotImplementedError, lambda: TypeA("baz", True, False).convert_to(TypeC))


        # register conversion C --> B
        Converters.register_converter(from_type=TypeC,
                                        to_type=TypeB,
                                        conv_func=lambda pitch_c: TypeB(pitch_c.value,
                                                                        pitch_c.is_pitch,
                                                                        pitch_c.is_class))
        # check that conversion C --> B works
        self.assertEqual(TypeC("foo", True, False).convert_to(TypeB), TypeB("foo", True, False))

        # register conversion B --> A
        # CREATE implicit converter C --> A
        Converters.register_converter(from_type=TypeB,
                                        to_type=TypeA,
                                        conv_func=lambda pitch_b: TypeA(pitch_b.value,
                                                                        pitch_b.is_pitch,
                                                                        pitch_b.is_class),
                                        create_implicit_converters=True)  # CREATE HERE
        # check that conversion B --> A works
        self.assertEqual(TypeB("bar", True, False).convert_to(TypeA), TypeA("bar", True, False))

        # check that conversion C --> A also works (implicitly created)
        self.assertEqual(TypeC("baz", True, False).convert_to(TypeA), TypeA("baz", True, False))

    def test_implementing_new_type(self):

        # define new type with sub-types
        @AbstractBase.create_subtypes()
        class New(AbstractBase): pass

        # make sure the types are linking correctly
        self.assertEqual(New._base_type, None)
        self.assertEqual(New.Pitch._base_type, New)
        self.assertEqual(New.Interval._base_type, New)
        self.assertEqual(New.PitchClass._base_type, New)
        self.assertEqual(New.IntervalClass._base_type, New)

        # make sure they print correctly (implying the class name to be set correctly)
        self.assertEqual(str(New.Pitch("test")), "NewPitch(test)")
        self.assertEqual(str(New.Interval("test")), "NewInterval(test)")
        self.assertEqual(str(New.PitchClass("test")), "NewPitchClass(test)")
        self.assertEqual(str(New.IntervalClass("test")), "NewIntervalClass(test)")
