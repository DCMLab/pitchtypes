from unittest import TestCase
from itertools import product

import numpy as np
from pitchtypes import AbstractBase, UnexpectedValue


class TestAbstractPitch(TestCase):

    def create_derived(self, value, is_pitch, is_class):
        if is_pitch:
            if is_class:
                return AbstractBase.PitchClass(value=value)
            else:
                return AbstractBase.Pitch(value=value)
        else:
            if is_class:
                return AbstractBase.IntervalClass(value=value)
            else:
                return AbstractBase.Interval(value=value)

    def test_implementing_subtypes(self):
        # create a new base type
        class NewType(AbstractBase):
            pass

        # create new sub-types with non-standard names; assert normal linking fails but can be forced
        class WrongNewTypePitch(NewType):
            pass
        self.assertRaises(UnexpectedValue, lambda: NewType.link_pitch_type()(WrongNewTypePitch))
        NewType.link_pitch_type(skip_name_check=True)(WrongNewTypePitch)

        class WrongNewTypeInterval(NewType):
            pass
        self.assertRaises(UnexpectedValue, lambda: NewType.link_interval_type()(WrongNewTypeInterval))
        NewType.link_interval_type(skip_name_check=True)(WrongNewTypeInterval)

        class WrongNewTypePitchClass(NewType):
            pass
        self.assertRaises(UnexpectedValue, lambda: NewType.link_pitch_class_type()(WrongNewTypePitchClass))
        NewType.link_pitch_class_type(skip_name_check=True)(WrongNewTypePitchClass)

        class WrongNewTypeIntervalClass(NewType):
            pass
        self.assertRaises(UnexpectedValue, lambda: NewType.link_interval_class_type()(WrongNewTypeIntervalClass))
        NewType.link_interval_class_type(skip_name_check=True)(WrongNewTypeIntervalClass)

        # make sure the linking worked
        self.assertRaises(AttributeError, lambda: NewType._base_type)
        self.assertEqual(NewType.Pitch, WrongNewTypePitch)
        self.assertEqual(NewType.Interval, WrongNewTypeInterval)
        self.assertEqual(NewType.PitchClass, WrongNewTypePitchClass)
        self.assertEqual(NewType.IntervalClass, WrongNewTypeIntervalClass)
        self.assertEqual(WrongNewTypePitch._base_type, NewType)
        self.assertEqual(WrongNewTypeInterval._base_type, NewType)
        self.assertEqual(WrongNewTypePitchClass._base_type, NewType)
        self.assertEqual(WrongNewTypeIntervalClass._base_type, NewType)

        # create type with standard name
        @NewType.link_pitch_type()
        class NewTypePitch(NewType):
            pass

        @NewType.link_interval_type()
        class NewTypeInterval(NewType):
            pass

        @NewType.link_pitch_class_type()
        class NewTypePitchClass(NewType):
            pass

        @NewType.link_interval_class_type()
        class NewTypeIntervalClass(NewType):
            pass

        # make sure the linking worked
        self.assertRaises(AttributeError, lambda: NewType._base_type)
        self.assertEqual(NewType.Pitch, NewTypePitch)
        self.assertEqual(NewType.Interval, NewTypeInterval)
        self.assertEqual(NewType.PitchClass, NewTypePitchClass)
        self.assertEqual(NewType.IntervalClass, NewTypeIntervalClass)
        self.assertEqual(NewTypePitch._base_type, NewType)
        self.assertEqual(NewTypeInterval._base_type, NewType)
        self.assertEqual(NewTypePitchClass._base_type, NewType)
        self.assertEqual(NewTypeIntervalClass._base_type, NewType)

        # some basic arithmetics
        p = NewTypePitch("pitch")
        i = NewTypeInterval("interval")
        pc = NewTypePitchClass("pitch class")
        ic = NewTypeIntervalClass("interval class")
        self.assertEqual(p + i, NewTypePitch("pitchinterval"))
        self.assertEqual(pc + ic, NewTypePitchClass("pitch classinterval class"))
        self.assertRaises(TypeError, lambda: i + p)
        self.assertRaises(TypeError, lambda: i + ic)

        # to class
        self.assertEqual(NewTypePitchClass("pitch"), p.to_class())
        self.assertEqual(NewTypeIntervalClass("interval"), i.to_class())
        self.assertRaises(AttributeError, lambda: pc.to_class())
        self.assertRaises(AttributeError, lambda: ic.to_class())

    def test_frozen_and_hash(self):
        # construct pitch with non-frozen array as value
        arr = np.array([1, 2, 3])
        p = AbstractBase(value=arr, is_pitch=True, is_class=True)
        # try to set value (should raise AttributeError)
        def f():
            p.value = "x"
        self.assertRaises(AttributeError, f)
        # try to get hash (should raise AssertionError because value is non-frozen numpy array)
        self.assertRaises(AssertionError, lambda: hash(p))

        # construct pitch with frozen array as value
        frozen_arr = arr.copy()
        frozen_arr.flags.writeable = False
        p = AbstractBase(value=frozen_arr, is_pitch=True, is_class=True)
        # hashing should work now
        hash(p)

    def test_AbstractPitch(self):
        for is_pitch in [True, False]:
            for is_class in [True, False]:
                # create a pitch or interval (class)
                p_or_i = AbstractBase(value="p", is_pitch=is_pitch, is_class=is_class)
                # pitch vs interval
                if is_pitch:
                    # should be indicated correctly
                    self.assertTrue(p_or_i.is_pitch)
                    self.assertFalse(p_or_i.is_interval)
                else:
                    # should be indicated correctly
                    self.assertFalse(p_or_i.is_pitch)
                    self.assertTrue(p_or_i.is_interval)

    def test_arithmetics(self):

        # create abstract sub-types to allow for checks
        AbstractBase.create_subtypes()(AbstractBase)

        for v_1, v_2, v_3 in np.random.randint(-2, 3, (10, 3)):
            for is_pitch_1, is_pitch_2, is_class_1, is_class_2 in product(*([[True, False]] * 4)):
                pi_1 = self.create_derived(v_1, is_pitch_1, is_class_1)
                pi_2 = self.create_derived(v_2, is_pitch_2, is_class_2)
                # addition and subtraction are not defined for mixed class and non-class types
                if is_class_1 != is_class_2:
                    self.assertRaises(TypeError, lambda: pi_1 + pi_2)
                    self.assertRaises(TypeError, lambda: pi_2 + pi_1)
                    self.assertRaises(TypeError, lambda: pi_1 - pi_2)
                    self.assertRaises(TypeError, lambda: pi_2 - pi_1)
                else:
                    if is_pitch_1:
                        if is_pitch_2:
                            self.assertRaises(TypeError, lambda: pi_1 + pi_2)
                            self.assertRaises(TypeError, lambda: pi_2 + pi_1)
                            self.assertEqual((pi_1 - pi_2).value, v_1 - v_2)
                            self.assertEqual((pi_2 - pi_1).value, v_2 - v_1)
                        else:
                            self.assertEqual((pi_1 + pi_2).value, v_1 + v_2)
                            self.assertRaises(TypeError, lambda: pi_2 + pi_1)
                            self.assertEqual((pi_1 - pi_2).value, v_1 - v_2)
                            self.assertRaises(TypeError, lambda: pi_2 - pi_1)
                    else:
                        if is_pitch_2:
                            self.assertEqual((pi_2 + pi_1).value, v_2 + v_1)
                            self.assertRaises(TypeError, lambda: pi_1 + pi_2)
                            self.assertEqual((pi_2 - pi_1).value, v_2 - v_1)
                            self.assertRaises(TypeError, lambda: pi_1 - pi_2)
                        else:
                            self.assertEqual((pi_1 + pi_2).value, v_1 + v_2)
                            self.assertEqual((pi_2 + pi_1).value, v_2 + v_1)
                            self.assertEqual((pi_1 - pi_2).value, v_1 - v_2)
                            self.assertEqual((pi_2 - pi_1).value, v_2 - v_1)
                # multiplication and division is defined for intervals and interval classes
                if is_pitch_1:
                    self.assertRaises(TypeError, lambda: pi_1 * v_3)
                    self.assertRaises(TypeError, lambda: v_3 * pi_1)
                    if v_3 != 0:
                        self.assertRaises(TypeError, lambda: pi_1 / v_3)
                else:
                    self.assertEqual((pi_1 * v_3).value, v_1 * v_3)
                    self.assertEqual((v_3 * pi_1).value, v_1 * v_3)
                    if v_3 != 0:
                        self.assertEqual((pi_1 / v_3).value, v_1 / v_3)
                if is_pitch_2:
                    self.assertRaises(TypeError, lambda: pi_2 * v_3)
                    self.assertRaises(TypeError, lambda: v_3 * pi_2)
                    if v_3 != 0:
                        self.assertRaises(TypeError, lambda: pi_2 / v_3)
                else:
                    self.assertEqual((pi_2 * v_3).value, v_2 * v_3)
                    self.assertEqual((v_3 * pi_2).value, v_2 * v_3)
                    if v_3 != 0:
                        self.assertEqual((pi_2 / v_3).value, v_2 / v_3)
                # equality checks for matching types (class and pitch/interval) as well as value
                if is_class_1 != is_class_2:
                    self.assertFalse(pi_1 == pi_2)
                    self.assertFalse(pi_2 == pi_1)
                else:
                    if is_pitch_1:
                        if is_pitch_2:
                            self.assertEqual(pi_1 == pi_2, v_1 == v_2)
                            self.assertEqual(pi_2 == pi_1, v_2 == v_1)
                        else:
                            self.assertFalse(pi_1 == pi_2)
                            self.assertFalse(pi_2 == pi_1)
                    else:
                        if is_pitch_2:
                            self.assertFalse(pi_1 == pi_2)
                            self.assertFalse(pi_2 == pi_1)
                        else:
                            self.assertEqual(pi_1 == pi_2, v_1 == v_2)
                            self.assertEqual(pi_2 == pi_1, v_2 == v_1)

    def test_hashing(self):

        for v_1, v_2, in np.random.randint(0, 2, (10, 2)):
            for is_pitch_1, is_pitch_2, is_class_1, is_class_2 in product(*([[True, False]] * 4)):
                pi_1 = self.create_derived(value=v_1, is_pitch=is_pitch_1, is_class=is_class_1)
                pi_2 = self.create_derived(value=v_2, is_pitch=is_pitch_2, is_class=is_class_2)
                s = set()
                self.assertFalse(pi_1 in s)
                s.add(pi_1)
                self.assertTrue(pi_1 in s)
                if v_1 == v_2 and is_pitch_1 == is_pitch_2 and is_class_1 == is_class_2:
                    # if all constructor parameters are the same, the objects should be considered equal
                    self.assertEqual(pi_1, pi_2)
                    self.assertTrue(pi_2 in s)
                else:
                    self.assertNotEqual(pi_1, pi_2)
                    self.assertFalse(pi_2 in s)
                    s.add(pi_2)
                    self.assertTrue(pi_2 in s)

