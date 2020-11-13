from unittest import TestCase
import numpy as np
from pitchtypes import LogFreq, LogFreqPitch, EnharmonicPitch


class TestLogFreq(TestCase):

    def test_against_MIDI(self):
        self.assertAlmostEqual(EnharmonicPitch("A4").convert_to(LogFreqPitch).freq(), 440)

    def test_to_class(self):
        # pitch classes are mapped to frequencies between 1 and 2 Hz
        # this corresponds to 0 to log(2) in log representation
        for f in np.random.uniform(1, 100, 100):
            # make sure pitch is set up correctly
            p = LogFreq.Pitch(f)
            self.assertEqual(np.log(f), float(p))
            # get the pitch class
            pc = p.to_class()
            self.assertEqual(LogFreq.PitchClass, type(pc))
            # check interval in log space
            self.assertTrue(0 <= float(pc) < np.log(2))
            # check interval in frequency space (cut of the 'Hz' in the printed representation)
            # due to round-off in printing 2 may be exactly matched (e.g. by 1.999999 rounded in print)
            self.assertTrue(1 <= float(str(pc)[:-2]) <= 2)
            # check exact value
            self.assertEqual(np.log(f) % np.log(2), float(pc))

        # interval classes are mapped to frequency ratios between 1 and 2
        # this corresponds to 0 to log(2) in log representation
        for r in np.random.uniform(1, 100, 100):
            # make sure pitch is set up correctly
            i = LogFreq.Interval(r)
            self.assertEqual(np.log(r), float(i))
            # get the pitch class
            ic = i.to_class()
            self.assertEqual(LogFreq.IntervalClass, type(ic))
            # check interval in log space
            self.assertTrue(0 <= float(ic) < np.log(2))
            # check interval in frequency space (cut of the 'Hz' in the printed representation)
            # due to round-off in printing 2 may be exactly matched (e.g. by 1.999999 rounded in print)
            self.assertTrue(1 <= float(str(ic)) <= 2)
            # check exact value
            self.assertEqual(np.log(r) % np.log(2), float(ic))

    def test_print_precision(self):
        p = LogFreq.Pitch(123.456)
        pc = LogFreq.PitchClass(1.111)
        i = LogFreq.Interval(2.345)
        ic = LogFreq.IntervalClass(1.234)
        # bad input raises ValueError
        self.assertRaises(ValueError, lambda: LogFreq.print_precision("x"))
        # default is 2
        self.assertEqual("123.46Hz", str(p))
        self.assertEqual("1.11Hz", str(pc))
        self.assertEqual("2.35", str(i))
        self.assertEqual("1.23", str(ic))
        # change separately for the single sub-types
        LogFreq.Pitch.print_precision(3)
        self.assertEqual(3, LogFreq.Pitch.print_precision())
        self.assertEqual("123.456Hz", str(p))
        self.assertEqual("1.11Hz", str(pc))
        self.assertEqual("2.35", str(i))
        self.assertEqual("1.23", str(ic))
        LogFreq.PitchClass.print_precision(3)
        self.assertEqual(3, LogFreq.PitchClass.print_precision())
        self.assertEqual("123.456Hz", str(p))
        self.assertEqual("1.111Hz", str(pc))
        self.assertEqual("2.35", str(i))
        self.assertEqual("1.23", str(ic))
        LogFreq.Interval.print_precision(3)
        self.assertEqual(3, LogFreq.Interval.print_precision())
        self.assertEqual("123.456Hz", str(p))
        self.assertEqual("1.111Hz", str(pc))
        self.assertEqual("2.345", str(i))
        self.assertEqual("1.23", str(ic))
        LogFreq.IntervalClass.print_precision(3)
        self.assertEqual(3, LogFreq.IntervalClass.print_precision())
        self.assertEqual("123.456Hz", str(p))
        self.assertEqual("1.111Hz", str(pc))
        self.assertEqual("2.345", str(i))
        self.assertEqual("1.234", str(ic))
        # change for all simultaneouly
        self.assertEqual(2, LogFreq.print_precision())
        LogFreq.print_precision(1)
        self.assertEqual(1, LogFreq.print_precision())
        self.assertEqual(1, LogFreq.Pitch.print_precision())
        self.assertEqual(1, LogFreq.PitchClass.print_precision())
        self.assertEqual(1, LogFreq.Interval.print_precision())
        self.assertEqual(1, LogFreq.IntervalClass.print_precision())
        self.assertEqual("123.5Hz", str(p))
        self.assertEqual("1.1Hz", str(pc))
        self.assertEqual("2.3", str(i))
        self.assertEqual("1.2", str(ic))
        # reset
        LogFreq.print_precision(2)


    # def test_convert_from_midi_pitch(self):
    #     self.fail()
    #
    # def test_to_class(self):
    #     self.fail()
    #
    # def test_freq(self):
    #     self.fail()
