#  Copyright (c) 2021 Robert Lieck

from unittest import TestCase
from unittest.mock import patch

from pitchtypes import AbstractInterval, Chromatic, Diatonic, AbstractPitch


class TestGeneralInterface(TestCase):

    @patch.multiple(AbstractInterval, __abstractmethods__=set())
    def test_interval(self):
        self.assertRaises(NotImplementedError, lambda: AbstractInterval.unison())
        self.assertRaises(NotImplementedError, lambda: AbstractInterval.octave())
        self.assertRaises(NotImplementedError, lambda: AbstractInterval().direction())
        self.assertRaises(NotImplementedError, lambda: AbstractInterval().abs())
        self.assertRaises(NotImplementedError, lambda: abs(AbstractInterval()))
        self.assertRaises(NotImplementedError, lambda: AbstractInterval().ic())
        self.assertRaises(NotImplementedError, lambda: AbstractInterval().to_class())
        self.assertRaises(NotImplementedError, lambda: AbstractInterval().embed())
        self.assertRaises(NotImplementedError, lambda: AbstractInterval() == AbstractInterval())
        self.assertRaises(NotImplementedError, lambda: AbstractInterval() + AbstractInterval())
        self.assertRaises(NotImplementedError, lambda: AbstractInterval() - AbstractInterval())
        self.assertRaises(NotImplementedError, lambda: AbstractInterval() * 1)
        self.assertRaises(NotImplementedError, lambda: 1 * AbstractInterval())
        self.assertRaises(NotImplementedError, lambda: -AbstractInterval())

    @patch.multiple(Chromatic, __abstractmethods__=set())
    def test_chromatic(self):
        self.assertRaises(NotImplementedError, lambda: Chromatic.chromatic_semitone())

    @patch.multiple(Diatonic, __abstractmethods__=set())
    def test_diatonic(self):
        self.assertRaises(NotImplementedError, lambda: Diatonic().is_step())

    @patch.multiple(AbstractPitch, __abstractmethods__=set())
    @patch.multiple(AbstractInterval, __abstractmethods__=set())
    def test_pitch(self):
        self.assertRaises(NotImplementedError, lambda: AbstractPitch().pc())
        self.assertRaises(NotImplementedError, lambda: AbstractPitch().to_class())
        self.assertRaises(NotImplementedError, lambda: AbstractPitch().embed())
        self.assertRaises(NotImplementedError, lambda: AbstractPitch() == AbstractPitch())
        self.assertRaises(NotImplementedError, lambda: AbstractPitch() + AbstractInterval())
        self.assertRaises(NotImplementedError, lambda: AbstractPitch() - AbstractInterval())
        self.assertRaises(TypeError, lambda: AbstractPitch() - AbstractPitch())
