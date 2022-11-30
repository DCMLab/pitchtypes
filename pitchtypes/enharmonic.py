#  Copyright (c) 2021 Robert Lieck

import numbers

from pitchtypes.basetypes import AbstractBase
from pitchtypes.spelled import Spelled
from pitchtypes.logfreq import LogFreq


class Enharmonic(AbstractBase):

    # how should Pitch and PitchClass types be printed
    _print_as_int = False
    _print_flat_sharp = 'sharp'

    @classmethod
    def print_options(cls, as_int=None, flat_sharp=None):
        if cls == Enharmonic:
            Enharmonic.Pitch.print_options(as_int=as_int, flat_sharp=flat_sharp)
            Enharmonic.PitchClass.print_options(as_int=as_int, flat_sharp=flat_sharp)
        if as_int is not None:
            cls._print_as_int = as_int
        if flat_sharp is not None:
            if flat_sharp not in ['sharp', 'flat']:
                raise ValueError("'flat_sharp' has to be one of ['sharp', 'flat']")
            else:
                cls._print_flat_sharp = flat_sharp
        if as_int is None and flat_sharp is None:
            print(f"print options in {cls.__name__}:\n"
                  f"    as_int: {cls._print_as_int}\n"
                  f"    flat_sharp: {cls._print_flat_sharp}")

    @staticmethod
    def pitch_class_name_from_midi(midi_pitch, flat_sharp):
        """
        Return the pitch class name for the given pitch in MIDI integer.
        :param midi_pitch: MIDI pitch
        :param flat_sharp: whether to use flats or sharps for accidentals
        :return: pitch class
        """
        if flat_sharp == "sharp":
            base_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        elif flat_sharp == "flat":
            base_names = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
        else:
            raise ValueError("parameter 'flat_sharp' must be one of ['sharp', 'flat']")
        return base_names[midi_pitch % 12]

    def __init__(self, value, is_pitch, is_class, **kwargs):
        # pre-process value
        if isinstance(value, str):
            if is_pitch:
                if is_class:
                    value = Spelled.PitchClass(value=value).convert_to(EnharmonicPitchClass).value
                else:
                    value = Spelled.Pitch(value=value).convert_to(EnharmonicPitch).value
            else:
                if is_class:
                    value = Spelled.IntervalClass(value=value).convert_to(EnharmonicIntervalClass).value
                else:
                    value = Spelled.Interval(value=value).convert_to(EnharmonicInterval).value
        elif isinstance(value, numbers.Number):
            int_value = int(value)
            if int_value != value:
                raise ValueError(f"Expected integer pitch value but got {value}")
            value = int_value
            if is_class:
                value = value % 12
        # hand on initialisation to other base classes
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)

    def convert_to_logfreq(self):
        raise NotImplementedError

    def __int__(self):
        return self.value

    def __repr__(self):
        return self.name()

    def name(self, *args, **kwargs):
        raise NotImplementedError


@Enharmonic.link_pitch_type()
class EnharmonicPitch(Enharmonic):

    def to_class(self):
        return self.PitchClass(value=self.value % 12)

    def name(self, as_int=None, flat_sharp=None):
        if as_int is None:
            as_int = self._print_as_int
        if flat_sharp is None:
            flat_sharp = self._print_flat_sharp
        if as_int:
            return str(self.value)
        return self.pitch_class_name_from_midi(self.value, flat_sharp=flat_sharp) + str(self.octaves())

    def octaves(self):
        return self.value // 12 - 1

    def freq(self):
        return 2 ** ((self.value - 69) / 12) * 440

    def convert_to_logfreq(self):
        return LogFreq.Pitch(self.freq(), is_freq=True)

    @property
    def midi(self):
        return self.value


@Enharmonic.link_interval_type()
class EnharmonicInterval(Enharmonic):
    def to_class(self):
        return self.IntervalClass(value=self.value % 12)

    def name(self):
        sign = "-" if self.value < 0 else ""
        return sign + str(abs(self.value))

    def octaves(self):
        return self.value // 12

    def convert_to_logfreq(self):
        return LogFreq.Interval(2 ** (self.value / 12), is_ratio=True)


@Enharmonic.link_pitch_class_type()
class EnharmonicPitchClass(Enharmonic):

    def name(self, as_int=None, flat_sharp=None):
        if as_int is None:
            as_int = self._print_as_int
        if flat_sharp is None:
            flat_sharp = self._print_flat_sharp
        if as_int:
            return str(self.value)
        return self.pitch_class_name_from_midi(self.value, flat_sharp=flat_sharp)

    def convert_to_logfreq(self):
        return LogFreq.PitchClass(2 ** ((self.value - 69) / 12) * 440, is_freq=True)


@Enharmonic.link_interval_class_type()
class EnharmonicIntervalClass(Enharmonic):
    def name(self):
        sign = "-" if self.value < 0 else ""
        return sign + str(abs(self.value))

    def convert_to_logfreq(self):
        return LogFreq.IntervalClass(2 ** (self.value / 12), is_ratio=True)
