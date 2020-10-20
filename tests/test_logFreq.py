from unittest import TestCase
from pitchtypes import LogFreq, Enharmonic


class TestLogFreq(TestCase):

    def test_against_MIDI(self):
        self.assertAlmostEqual(LogFreq(Enharmonic("A4")).freq(), 440)

    # def test_print_precision(self):
    #     self.fail()
    #
    # def test_convert_from_midi_pitch(self):
    #     self.fail()
    #
    # def test_to_class(self):
    #     self.fail()
    #
    # def test_freq(self):
    #     self.fail()
