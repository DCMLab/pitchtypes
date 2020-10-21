from unittest import TestCase
from pitchtypes import AbstractBase, Enharmonic


class TestConverters(TestCase):

    def test_converters(self):
        # define three types A, B, and C
        class TypeA(AbstractBase): pass

        class TypeB(AbstractBase): pass

        class TypeC(AbstractBase): pass

        # register converter A --> B
        AbstractBase.register_converter(from_type=TypeA,
                                        to_type=TypeB,
                                        conv_func=lambda pitch_a: TypeB(pitch_a._value,
                                                                        pitch_a.is_pitch(),
                                                                        pitch_a.is_class()))
        # check conversion works (both via convert_to() and via initialisation)
        self.assertEqual(TypeA("foo", True, False).convert_to(TypeB), TypeB("foo", True, False))
        self.assertEqual(TypeB(TypeA("foo", True, False)), TypeB("foo", True, False))

        # register converter B --> C
        AbstractBase.register_converter(from_type=TypeB,
                                        to_type=TypeC,
                                        conv_func=lambda pitch_b: TypeC(pitch_b._value,
                                                                        pitch_b.is_pitch(),
                                                                        pitch_b.is_class()))
        # check conversion works (both via convert_to() and via initialisation)
        self.assertEqual(TypeB("bar", True, False).convert_to(TypeC), TypeC("bar", True, False))
        self.assertEqual(TypeC(TypeB("bar", True, False)), TypeC("bar", True, False))

        # check that conversion A --> C DOES NOT work!
        self.assertRaises(NotImplementedError, lambda: TypeA("baz", True, False).convert_to(TypeC))
        self.assertRaises(NotImplementedError, lambda: TypeC(TypeA("baz", True, False)))


        # register conversion C --> B
        AbstractBase.register_converter(from_type=TypeC,
                                        to_type=TypeB,
                                        conv_func=lambda pitch_c: TypeB(pitch_c._value,
                                                                        pitch_c.is_pitch(),
                                                                        pitch_c.is_class()))
        # check that conversion C --> B works
        self.assertEqual(TypeC("foo", True, False).convert_to(TypeB), TypeB("foo", True, False))
        self.assertEqual(TypeB(TypeC("foo", True, False)), TypeB("foo", True, False))

        # register conversion B --> A
        # CREATE implicit converter C --> A
        AbstractBase.register_converter(from_type=TypeB,
                                        to_type=TypeA,
                                        conv_func=lambda pitch_b: TypeA(pitch_b._value,
                                                                        pitch_b.is_pitch(),
                                                                        pitch_b.is_class()),
                                        create_implicit_converters=True)  # CREATE HERE
        # check that conversion B --> A works
        self.assertEqual(TypeB("bar", True, False).convert_to(TypeA), TypeA("bar", True, False))
        self.assertEqual(TypeA(TypeB("bar", True, False)), TypeA("bar", True, False))

        # check that conversion C --> A also works (implicitly created)
        self.assertEqual(TypeC("baz", True, False).convert_to(TypeA), TypeA("baz", True, False))
        self.assertEqual(TypeA(TypeC("baz", True, False)), TypeA("baz", True, False))


