from unittest import TestCase
import numpy as np
from pitchtypes import LogFreq, LogFreqPitch, LogFreqInterval, LogFreqPitchClass, LogFreqIntervalClass, EnharmonicPitch


class TestLogFreq(TestCase):

    def test_against_MIDI(self):
        self.assertAlmostEqual(EnharmonicPitch("A4").convert_to(LogFreqPitch).freq(), 440)

    def test_to_class(self):
        # pitch classes are mapped to frequencies between 1 and 2 Hz
        # this corresponds to 0 to log(2) in log representation
        for f in np.random.uniform(1, 100, 100):
            # make sure pitch is set up correctly
            p = LogFreq.Pitch(str(f) + "Hz")
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
            i = LogFreq.Interval(str(r))
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
        p = LogFreq.Pitch("123.456Hz")
        pc = LogFreq.PitchClass("1.111Hz")
        i = LogFreq.Interval("2.345")
        ic = LogFreq.IntervalClass("1.234")
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

    def test_init(self):
        self.assertRaises(ValueError, lambda: LogFreqPitch("not good"))
        self.assertRaises(ValueError, lambda: LogFreqPitchClass("not good"))
        for freq in np.random.uniform(10, 1000, 100):
            self.assertEqual(LogFreqPitch(str(freq) + "Hz"), LogFreqPitch(freq, is_freq=True))
            self.assertEqual(LogFreqPitch(str(freq) + "Hz"), LogFreqPitch(np.log(freq), is_freq=False))
            self.assertEqual(LogFreqPitchClass(str(freq) + "Hz"), LogFreqPitchClass(freq, is_freq=True))
            self.assertEqual(LogFreqPitchClass(str(freq) + "Hz"), LogFreqPitchClass(np.log(freq), is_freq=False))
        self.assertRaises(ValueError, lambda: LogFreqInterval("not good"))
        self.assertRaises(ValueError, lambda: LogFreqIntervalClass("not good"))
        for ratio in np.random.uniform(1e-5, 100, 100):
            self.assertEqual(LogFreqInterval(str(ratio)), LogFreqInterval(ratio, is_ratio=True))
            self.assertEqual(LogFreqInterval(str(ratio)), LogFreqInterval(np.log(ratio), is_ratio=False))
            self.assertEqual(LogFreqIntervalClass(str(ratio)), LogFreqIntervalClass(ratio, is_ratio=True))
            self.assertEqual(LogFreqIntervalClass(str(ratio)), LogFreqIntervalClass(np.log(ratio), is_ratio=False))

    def test_arithmetics(self):
        for freq1, freq2 in np.random.uniform(10, 1000, (10, 2)):
            ratio1, ratio2 = np.random.uniform(0.1, 2, 2)
            # non-class types
            self.assertAlmostEqual((LogFreqInterval(str(ratio1)) + LogFreqInterval(str(ratio2))).ratio(),
                                   ratio1 * ratio2)
            self.assertAlmostEqual((LogFreqInterval(str(ratio1)) - LogFreqInterval(str(ratio2))).ratio(),
                                   ratio1 / ratio2)
            self.assertAlmostEqual((LogFreqPitch(str(freq1) + "Hz") - LogFreqPitch(str(freq2) + "Hz")).ratio(),
                                   freq1 / freq2)
            self.assertAlmostEqual((LogFreqPitch(str(freq1) + "Hz") + LogFreqInterval(str(ratio1))).freq(),
                                   freq1 * ratio1)
            self.assertAlmostEqual((LogFreqPitch(str(freq1) + "Hz") - LogFreqInterval(str(ratio1))).freq(),
                                   freq1 / ratio1)

            # class types
            def log_mod(r):
                return np.exp(np.log(r) % np.log(2))

            self.assertAlmostEqual((LogFreqIntervalClass(str(ratio1)) + LogFreqIntervalClass(str(ratio2))).ratio(),
                                   log_mod(ratio1 * ratio2))
            self.assertAlmostEqual((LogFreqIntervalClass(str(ratio1)) - LogFreqIntervalClass(str(ratio2))).ratio(),
                                   log_mod(ratio1 / ratio2))
            self.assertAlmostEqual((LogFreqPitchClass(str(freq1) + "Hz") - LogFreqPitchClass(str(freq2) + "Hz")).ratio(),
                                   log_mod(freq1 / freq2))
            self.assertAlmostEqual((LogFreqPitchClass(str(freq1) + "Hz") + LogFreqIntervalClass(str(ratio1))).freq(),
                                   log_mod(freq1 * ratio1))
            self.assertAlmostEqual((LogFreqPitchClass(str(freq1) + "Hz") - LogFreqIntervalClass(str(ratio1))).freq(),
                                   log_mod(freq1 / ratio1))

    # def test_convert_from_midi_pitch(self):
    #     self.fail()
    #
    # def test_to_class(self):
    #     self.fail()
    #
    # def test_freq(self):
    #     self.fail()
