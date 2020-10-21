from unittest import TestCase
from pitchtypes import AbstractBase
import numpy as np
from itertools import product


class TestAbstractPitch(TestCase):
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
                    # conversion to interval should be possible
                    i = p_or_i.to_interval()
                    # and result in an interval
                    self.assertFalse(i.is_pitch)
                    self.assertTrue(i.is_interval)
                    # conversion to pitch should fail
                    self.assertRaises(TypeError, p_or_i.to_pitch)
                else:
                    # should be indicated correctly
                    self.assertFalse(p_or_i.is_pitch)
                    self.assertTrue(p_or_i.is_interval)
                    # conversion to pitch should be possible
                    p = p_or_i.to_pitch()
                    # and result in a pitch
                    self.assertTrue(p.is_pitch)
                    self.assertFalse(p.is_interval)
                    # conversion to interval should fail
                    self.assertRaises(TypeError, p_or_i.to_interval)

                # creating a pitch of same type but with different value
                p = p_or_i._create_pitch("x")
                # should have same class property
                self.assertEqual(p.is_class, p_or_i.is_class)
                # should be pitch of same type
                self.assertTrue(p_or_i._is_pitch_of_same_type(p))
                # should not be interval of same type
                self.assertFalse(p_or_i._is_interval_of_same_type(p))

                # creating an interval of same type but with different value
                i = p_or_i._create_interval("x")
                # should have same class property
                self.assertEqual(i.is_class, p_or_i.is_class)
                # should be interval of same type
                self.assertTrue(p_or_i._is_interval_of_same_type(i))
                # should not be pitch of same type
                self.assertFalse(p_or_i._is_pitch_of_same_type(i))

    def test_arithmetics(self):
        for v_1, v_2, v_3 in np.random.randint(-2, 3, (10, 3)):
            for is_pitch_1, is_pitch_2, is_class_1, is_class_2 in product(*([[True, False]] * 4)):
                pi_1 = AbstractBase(value=v_1, is_pitch=is_pitch_1, is_class=is_class_1)
                pi_2 = AbstractBase(value=v_2, is_pitch=is_pitch_2, is_class=is_class_2)
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
                            self.assertEqual((pi_1 - pi_2)._value, v_1 - v_2)
                            self.assertEqual((pi_2 - pi_1)._value, v_2 - v_1)
                        else:
                            self.assertEqual((pi_1 + pi_2)._value, v_1 + v_2)
                            self.assertRaises(TypeError, lambda: pi_2 + pi_1)
                            self.assertEqual((pi_1 - pi_2)._value, v_1 - v_2)
                            self.assertRaises(TypeError, lambda: pi_2 - pi_1)
                    else:
                        if is_pitch_2:
                            self.assertEqual((pi_2 + pi_1)._value, v_2 + v_1)
                            self.assertRaises(TypeError, lambda: pi_1 + pi_2)
                            self.assertEqual((pi_2 - pi_1)._value, v_2 - v_1)
                            self.assertRaises(TypeError, lambda: pi_1 - pi_2)
                        else:
                            self.assertEqual((pi_1 + pi_2)._value, v_1 + v_2)
                            self.assertEqual((pi_2 + pi_1)._value, v_2 + v_1)
                            self.assertEqual((pi_1 - pi_2)._value, v_1 - v_2)
                            self.assertEqual((pi_2 - pi_1)._value, v_2 - v_1)
                # multiplication and division is defined for intervals and interval classes
                if is_pitch_1:
                    self.assertRaises(TypeError, lambda: pi_1 * v_3)
                    self.assertRaises(TypeError, lambda: v_3 * pi_1)
                    if v_3 != 0:
                        self.assertRaises(TypeError, lambda: pi_1 / v_3)
                else:
                    self.assertEqual((pi_1 * v_3)._value, v_1 * v_3)
                    self.assertEqual((v_3 * pi_1)._value, v_1 * v_3)
                    if v_3 != 0:
                        self.assertEqual((pi_1 / v_3)._value, v_1 / v_3)
                if is_pitch_2:
                    self.assertRaises(TypeError, lambda: pi_2 * v_3)
                    self.assertRaises(TypeError, lambda: v_3 * pi_2)
                    if v_3 != 0:
                        self.assertRaises(TypeError, lambda: pi_2 / v_3)
                else:
                    self.assertEqual((pi_2 * v_3)._value, v_2 * v_3)
                    self.assertEqual((v_3 * pi_2)._value, v_2 * v_3)
                    if v_3 != 0:
                        self.assertEqual((pi_2 / v_3)._value, v_2 / v_3)
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
        for v_1, v_2, in np.random.randint(0, 2, (10, 2)):
            for is_pitch_1, is_pitch_2, is_class_1, is_class_2 in product(*([[True, False]] * 4)):
                pi_1 = AbstractBase(value=v_1, is_pitch=is_pitch_1, is_class=is_class_1)
                pi_2 = AbstractBase(value=v_2, is_pitch=is_pitch_2, is_class=is_class_2)
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

