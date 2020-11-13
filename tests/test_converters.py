#  Copyright (c) 2020 Robert Lieck
from unittest import TestCase
from pitchtypes import AbstractBase, Converters


class TestConverters(TestCase):

    def test_converters(self):
        # define three types A, B, and C
        class TypeA(AbstractBase):
            pass

        class TypeB(AbstractBase):
            pass

        class TypeC(AbstractBase):
            pass

        # register without adding implicit converters (e=explicit, x=does not exist)
        # converter matrix then is:
        #  |A B C|
        # A|  E X|
        # B|    E|
        # C|     |

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

        # register other direction WITH adding implicit converters (e=explicit, i=implicit x=does not exist)
        # converter matrix then is:
        #  |A B C|
        # A|  e  |
        # B|E   e|
        # C|I E  |

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

        # overwrite implicit converter with explicit one
        # - raise ValueError if not explicitly requested
        # - since the existing converter is implicit, requesting explicit converter to be overwritten does not help
        # converter matrix then is:
        #  |A B C|
        # A|  e  |
        # B|e   e|
        # C|E e  |
        self.assertRaises(ValueError,
                          lambda: Converters.register_converter(from_type=TypeC,
                                                                to_type=TypeA,
                                                                conv_func=lambda pitch_c: TypeA(pitch_c.value,
                                                                                                pitch_c.is_pitch,
                                                                                                pitch_c.is_class),
                                                                overwrite_explicit_converters=True))
        Converters.register_converter(from_type=TypeC,
                                      to_type=TypeA,
                                      conv_func=lambda pitch_c: TypeA(pitch_c.value,
                                                                      pitch_c.is_pitch,
                                                                      pitch_c.is_class),
                                      overwrite_implicit_converters=True)

        # overwrite explicit converter just created
        # - raise ValueError if not explicitly requested
        # - since the existing converter is explicit, requesting implicit converter to be overwritten does not help
        self.assertRaises(ValueError,
                          lambda: Converters.register_converter(from_type=TypeC,
                                                                to_type=TypeA,
                                                                conv_func=lambda pitch_c: TypeA(pitch_c.value,
                                                                                                pitch_c.is_pitch,
                                                                                                pitch_c.is_class),
                                                                overwrite_implicit_converters=True))
        Converters.register_converter(from_type=TypeC,
                                      to_type=TypeA,
                                      conv_func=lambda pitch_c: TypeA(pitch_c.value,
                                                                      pitch_c.is_pitch,
                                                                      pitch_c.is_class),
                                      overwrite_explicit_converters=True)

        # add converter to yet another type to check extending implicit converters
        # - add TypeD --> TypeC
        # - TypeD --> TypeA is implicitly created by extending TypeC --> TypeA
        # converter matrix then is:
        #  |A B C D|
        # A|  e    |
        # B|e   e  |
        # C|e e    |
        # D|I I E  |
        class TypeD(AbstractBase):
            pass

        Converters.register_converter(from_type=TypeD,
                                      to_type=TypeC,
                                      conv_func=lambda pitch_d: TypeC(pitch_d.value,
                                                                      pitch_d.is_pitch,
                                                                      pitch_d.is_class),
                                      create_implicit_converters=True)
        self.assertEqual(TypeD("bar", True, False).convert_to(TypeC), TypeC("bar", True, False))
        self.assertEqual(TypeD("bar", True, False).convert_to(TypeA), TypeA("bar", True, False))
        self.assertEqual(TypeD("bar", True, False).convert_to(TypeB), TypeB("bar", True, False))

        # add converter TypeA --> TypeD and TypeD --> TypeA
        # - overwrite existing implicit converters (because one was implicitly created above)
        # - create implicit converters for second one
        # this includes self-conversion TypeA --> TypeA and TypeD --> TypeD, which should be ignored
        # converter matrix then is:
        #  |A B C D|
        # A|  e    |
        # B|e   e  |
        # C|e e    |
        # D|i i e  |
        self.assertRaises(NotImplementedError, lambda: Converters.get_converter(TypeA, TypeA))
        Converters.register_converter(from_type=TypeA,
                                      to_type=TypeD,
                                      conv_func=lambda pitch_a: TypeD(pitch_a.value,
                                                                      pitch_a.is_pitch,
                                                                      pitch_a.is_class))
        Converters.register_converter(from_type=TypeD,
                                      to_type=TypeA,
                                      conv_func=lambda pitch_d: TypeA(pitch_d.value,
                                                                      pitch_d.is_pitch,
                                                                      pitch_d.is_class),
                                      create_implicit_converters=True,
                                      overwrite_implicit_converters=True)
        # still not implemented
        self.assertRaises(NotImplementedError, lambda: Converters.get_converter(TypeA, TypeA))
        self.assertRaises(NotImplementedError, lambda: Converters.get_converter(TypeD, TypeD))

    def test_self_conversion(self):
        class NewType(AbstractBase):
            pass

        # self conversion should just give back the original object
        n = NewType("x", is_pitch=True, is_class=True)
        self.assertEqual(n, n.convert_to(NewType))
        # it's actually the SAME object
        self.assertTrue(n is n.convert_to(NewType))

        # attempting to register a self-converter should raise a TypeError
        self.assertRaises(TypeError, lambda: Converters.register_converter(NewType, NewType, conv_func=lambda: None))

    def test_non_existing_converter(self):
        class NewType(AbstractBase):
            pass

        class OtherType(AbstractBase):
            pass

        n = NewType("x", is_pitch=True, is_class=True)

        # requesting a converter or attempting conversion should raise NotImplementedError
        self.assertRaises(NotImplementedError, lambda: Converters.get_converter(NewType, OtherType))
        self.assertRaises(NotImplementedError, lambda: n.convert_to(OtherType))