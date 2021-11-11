#  Copyright (c) 2021 Robert Lieck

import numbers

import numpy as np

from pitchtypes import AbstractBase


class LogFreq(AbstractBase):
    """
    Represents a pitches and intervals in continuous frequency space with the frequency value stored in log
    representation.
    """

    _print_precision = 2

    @classmethod
    def print_precision(cls, precision=None):
        if precision is not None:
            if not isinstance(precision, numbers.Integral):
                raise ValueError(f"precision has to be an integer, got {precision}")
            if cls == LogFreq:
                for sub_cls in [LogFreq.Pitch, LogFreq.Interval, LogFreq.PitchClass, LogFreq.IntervalClass]:
                    sub_cls.print_precision(precision)
            cls._print_precision = precision
        return cls._print_precision

    @classmethod
    def _convert_freq_str(cls, s):
        if s.endswith("Hz"):
            return float(s[:-2])
        else:
            raise ValueError(f"String values have to be floats followed by 'Hz', but got '{s}'")

    def __init__(self, value, is_pitch, is_class, is_log=True, **kwargs):
        """
        Initialise from frequency or log-frequency value.
        :param value: frequency or log-frequency (default) value
        :param is_log: whether value is frequency or log-frequency
        """
        if is_log:
            value = float(value)
        else:
            value = np.log(value)
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)

    def __float__(self):
        return float(self.value)


@LogFreq.link_pitch_type()
class LogFreqPitch(LogFreq):
    def __init__(self, value, is_freq=False, **kwargs):
        if isinstance(value, str):
            value = self._convert_freq_str(value)
            is_freq = True
        super().__init__(value, is_pitch=True, is_class=False, is_log=not is_freq, **kwargs)

    def __repr__(self):
        return f"{np.format_float_positional(self.freq(), fractional=True, precision=self._print_precision)}Hz"

    def to_class(self):
        return self.PitchClass(self.value, is_freq=False)

    def freq(self):
        return np.exp(self.value)


@LogFreq.link_interval_type()
class LogFreqInterval(LogFreq):
    def __init__(self, value, is_ratio=False, **kwargs):
        if isinstance(value, str):
            value = float(value)
            is_ratio = True
        super().__init__(value, is_pitch=False, is_class=False, is_log=not is_ratio, **kwargs)

    def __repr__(self):
        return f"{np.format_float_positional(self.ratio(), fractional=True, precision=self._print_precision)}"

    def to_class(self):
        return self.IntervalClass(self.value, is_ratio=False)

    def ratio(self):
        return np.exp(self.value)


@LogFreq.link_pitch_class_type()
class LogFreqPitchClass(LogFreq):
    def __init__(self, value, is_freq=False, **kwargs):
        if isinstance(value, str):
            value = self._convert_freq_str(value)
            is_freq = True
        if is_freq:
            value = np.log(value)
        else:
            value = float(value)
        value %= np.log(2)
        super().__init__(value, is_pitch=True, is_class=True, is_log=True, **kwargs)

    def __repr__(self):
        return f"{np.format_float_positional(self.freq(), fractional=True, precision=self._print_precision)}Hz"

    def freq(self):
        return np.exp(self.value)


@LogFreq.link_interval_class_type()
class LogFreqIntervalClass(LogFreq):
    def __init__(self, value, is_ratio=False, **kwargs):
        if isinstance(value, str):
            value = float(value)
            is_ratio = True
        if is_ratio:
            value = np.log(value)
        else:
            value = float(value)
        value %= np.log(2)
        super().__init__(value, is_pitch=False, is_class=True, is_log=True, **kwargs)

    def __repr__(self):
        return f"{np.format_float_positional(self.ratio(), fractional=True, precision=self._print_precision)}"

    def ratio(self):
        return np.exp(self.value)
