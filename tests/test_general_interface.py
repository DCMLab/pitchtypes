#  Copyright (c) 2021 Robert Lieck

from unittest import TestCase
from unittest.mock import patch

from pitchtypes import Interval, Chromatic, Diatonic, Pitch

class TestGeneralInterface(TestCase):

    @patch.multiple(Interval, __abstractmethods__=set())
    def test_interval(self):
        self.assertRaises(NotImplementedError, lambda: Interval.unison())
        self.assertRaises(NotImplementedError, lambda: Interval.octave())
        self.assertRaises(NotImplementedError, lambda: Interval().direction())
        self.assertRaises(NotImplementedError, lambda: Interval().abs())
        self.assertRaises(NotImplementedError, lambda: abs(Interval()))
        self.assertRaises(NotImplementedError, lambda: Interval().ic())
        self.assertRaises(NotImplementedError, lambda: Interval().to_class())
        self.assertRaises(NotImplementedError, lambda: Interval().embed())

    @patch.multiple(Chromatic, __abstractmethods__=set())
    def test_chromatic(self):
        self.assertRaises(NotImplementedError, lambda: Chromatic.chromatic_semitone())

    @patch.multiple(Diatonic, __abstractmethods__=set())
    def test_diatonic(self):
        self.assertRaises(NotImplementedError, lambda: Diatonic().is_step())

    @patch.multiple(Pitch, __abstractmethods__=set())
    def test_pitch(self):
        self.assertRaises(NotImplementedError, lambda: Pitch().pc())
        self.assertRaises(NotImplementedError, lambda: Pitch().to_class())
        self.assertRaises(NotImplementedError, lambda: Pitch().embed())
