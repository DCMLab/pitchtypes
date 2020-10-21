from unittest import TestCase
from pitchtypes import LogFreqPitch, EnharmonicPitch


class TestLogFreq(TestCase):

    def test_against_MIDI(self):
        self.assertAlmostEqual(EnharmonicPitch("A4").convert_to(LogFreqPitch).freq(), 440)

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
