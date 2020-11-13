from unittest import TestCase
from pitchtypes import AbstractBase, Enharmonic, Converters


class TestConverters(TestCase):

    def test_implementing_new_type(self):

        # define new type with sub-types
        @AbstractBase.create_subtypes()
        class New(AbstractBase): pass

        # make sure the types are linking correctly
        self.assertRaises(AttributeError, lambda: New._base_type)
        self.assertEqual(New.Pitch._base_type, New)
        self.assertEqual(New.Interval._base_type, New)
        self.assertEqual(New.PitchClass._base_type, New)
        self.assertEqual(New.IntervalClass._base_type, New)

        # make sure they print correctly (implying the class name to be set correctly)
        self.assertEqual(str(New.Pitch("test")), "NewPitch(test)")
        self.assertEqual(str(New.Interval("test")), "NewInterval(test)")
        self.assertEqual(str(New.PitchClass("test")), "NewPitchClass(test)")
        self.assertEqual(str(New.IntervalClass("test")), "NewIntervalClass(test)")
