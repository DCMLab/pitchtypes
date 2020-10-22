from unittest import TestCase

class TestExamples(TestCase):

    def test_readme_1(self):
        from pitchtypes import SpelledPitchClass
        p1 = SpelledPitchClass("C#")
        p2 = SpelledPitchClass("Gb")
        i = p1 - p2
        print(type(i))
        print(i)

    def test_readme_2(self):
        from pitchtypes import SpelledPitch, EnharmonicPitch
        spelled = SpelledPitch("C#4")
        enharmonic = spelled.convert_to(EnharmonicPitch)
        print(type(enharmonic))
        print(enharmonic.midi)
        print(enharmonic.name('sharp'))
        print(enharmonic.name('flat'))

    def test_readme_3(self):
        from pitchtypes import EnharmonicPitch, LogFreqPitch
        enharmonic = EnharmonicPitch("A4")
        logfreq = enharmonic.convert_to(LogFreqPitch)
        print(logfreq)