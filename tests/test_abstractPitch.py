from unittest import TestCase
from pitchtypes import AbstractBase
import numpy as np
from itertools import product


class TestAbstractPitch(TestCase):

    def test_implementing_subtypes(self):

        @AbstractBase.link_pitch_type()
        class AbstractPitch(AbstractBase): pass

        @AbstractBase.link_interval_type()
        class AbstractInterval(AbstractBase): pass

        @AbstractBase.link_pitch_class_type()
        class AbstractPitchClass(AbstractBase): pass

        @AbstractBase.link_interval_class_type()
        class AbstractIntervalClass(AbstractBase): pass

        # make sure the linking worked
        self.assertEqual(AbstractBase._base_type, None)
        self.assertEqual(AbstractBase.Pitch, AbstractPitch)
        self.assertEqual(AbstractBase.Interval, AbstractInterval)
        self.assertEqual(AbstractBase.PitchClass, AbstractPitchClass)
        self.assertEqual(AbstractBase.IntervalClass, AbstractIntervalClass)
        self.assertEqual(AbstractPitch._base_type, AbstractBase)
        self.assertEqual(AbstractInterval._base_type, AbstractBase)
        self.assertEqual(AbstractPitchClass._base_type, AbstractBase)
        self.assertEqual(AbstractIntervalClass._base_type, AbstractBase)

        # some basic arithmetics
        p = AbstractPitch("pitch")
        i = AbstractInterval("interval")
        pc = AbstractPitchClass("pitch class")
        ic = AbstractIntervalClass("interval class")
        self.assertEqual(p + i, AbstractPitch("pitchinterval"))
        self.assertEqual(pc + ic, AbstractPitchClass("pitch classinterval class"))
        self.assertRaises(TypeError, lambda: i + p)
        self.assertRaises(TypeError, lambda: i + ic)


    def test_AbstractPitch(self):
        for is_pitch in [True, False]:
            for is_class in [True, False]:
                # create a pitch or interval (class)
                p_or_i = AbstractBase(value="p", is_pitch=is_pitch, is_class=is_class)
                # class type
                if is_class:
                    # if it's a class type
                    # is_class should be true
                    self.assertTrue(p_or_i.is_class)
                    # conversion to class type should fail
                    self.assertRaises(TypeError, p_or_i.to_class)
                else:
                    # if it's NOT a class type
                    # is_class should be true
                    self.assertFalse(p_or_i.is_class)
                    # conversion to class type should be possible
                    c = p_or_i.to_class()
                    # and produce a class type
                    self.assertTrue(c.is_class)
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

        # create default types to make AbstractBase usable
        @AbstractBase.link_pitch_type()
        class AbstractPitch(AbstractBase):
            pass

        @AbstractBase.link_interval_type()
        class AbstractInterval(AbstractBase):
            pass

        @AbstractBase.link_pitch_class_type()
        class AbstractPitchClass(AbstractBase):
            pass

        @AbstractBase.link_interval_class_type()
        class AbstractIntervalClass(AbstractBase):
            pass

        for v_1, v_2, v_3 in np.random.randint(-2, 3, (10, 3)):
            for is_pitch_1, is_pitch_2, is_class_1, is_class_2 in product(*([[True, False]] * 4)):
                pi_1 = AbstractBase(value=v_1, is_pitch=is_pitch_1, is_class=is_class_1)._create_derived_type()
                pi_2 = AbstractBase(value=v_2, is_pitch=is_pitch_2, is_class=is_class_2)._create_derived_type()
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
                # inequality can only be check for matching non-class types
                if is_class_1 != is_class_2:
                    self.assertRaises(TypeError, lambda: pi_1 < pi_2)
                    self.assertRaises(TypeError, lambda: pi_2 < pi_1)
                else:
                    if is_pitch_1:
                        if is_pitch_2:
                            if is_class_1 and is_class_2:
                                self.assertRaises(TypeError, lambda: pi_1 < pi_2)
                                self.assertRaises(TypeError, lambda: pi_2 < pi_1)
                            else:
                                self.assertEqual(pi_1 < pi_2, v_1 < v_2)
                                self.assertEqual(pi_2 < pi_1, v_2 < v_1)
                        else:
                            self.assertRaises(TypeError, lambda: pi_1 < pi_2)
                            self.assertRaises(TypeError, lambda: pi_2 < pi_1)
                    else:
                        if is_pitch_2:
                            self.assertRaises(TypeError, lambda: pi_1 < pi_2)
                            self.assertRaises(TypeError, lambda: pi_2 < pi_1)
                        else:
                            if is_class_1 and is_class_2:
                                self.assertRaises(TypeError, lambda: pi_1 < pi_2)
                                self.assertRaises(TypeError, lambda: pi_2 < pi_1)
                            else:
                                self.assertEqual(pi_1 < pi_2, v_1 < v_2)
                                self.assertEqual(pi_2 < pi_1, v_2 < v_1)

    def test_hashing(self):

        # create default types to make AbstractBase usable
        @AbstractBase.link_pitch_type()
        class AbstractPitch(AbstractBase):
            pass

        @AbstractBase.link_interval_type()
        class AbstractInterval(AbstractBase):
            pass

        @AbstractBase.link_pitch_class_type()
        class AbstractPitchClass(AbstractBase):
            pass

        @AbstractBase.link_interval_class_type()
        class AbstractIntervalClass(AbstractBase):
            pass

        for v_1, v_2, in np.random.randint(0, 2, (10, 2)):
            for is_pitch_1, is_pitch_2, is_class_1, is_class_2 in product(*([[True, False]] * 4)):
                pi_1 = AbstractBase(value=v_1, is_pitch=is_pitch_1, is_class=is_class_1)._create_derived_type()
                pi_2 = AbstractBase(value=v_2, is_pitch=is_pitch_2, is_class=is_class_2)._create_derived_type()
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

