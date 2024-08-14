#  Copyright (c) 2021 Robert Lieck

import numbers

from pitchtypes.spelled import Spelled, SpelledPitch, SpelledInterval, SpelledPitchClass, SpelledIntervalClass
from pitchtypes.logfreq import LogFreq
import abc
import functools
from pitchtypes.errors import InvalidArgument, UnexpectedValue, PropertyUndefined
from pitchtypes.utils import diatonic_steps_from_fifths
from pitchtypes.basetypes import AbstractBase, Pitch, Interval, Chromatic


@functools.total_ordering
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
                raise InvalidArgument("'flat_sharp' has to be one of ['sharp', 'flat']")
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
            raise InvalidArgument("parameter 'flat_sharp' must be one of ['sharp', 'flat']")
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
                raise UnexpectedValue(f"Expected integer pitch value but got {value}")
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

    def __str__(self):
        return self.name()

    def name(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def convert_to_logfreq(self):
        raise NotImplementedError

    @abc.abstractmethod
    def octaves(self):
        pass

    @abc.abstractmethod
    def embed(self):
        pass

    @abc.abstractmethod
    def from_semitones(cls, semitones):
        pass

    def __int__(self):
        return self.value

    def compare(self, other):
        """
        Comparison between two enharmonic types.

        Returns 0 if the objects are equal,
        1 if the first object (``self``) is greater,
        and -1 if the second object (``other``) is greater.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: an object to compare to (same type as ``self``)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        raise NotImplementedError

    def __eq__(self, other):
        try:
            return self.compare(other) == 0
        except TypeError:
            return NotImplemented

    def __lt__(self, other):
        try:
            return self.compare(other) == -1
        except TypeError:
            return NotImplemented


class AbstractEnharmonicInterval(abc.ABC):

    @abc.abstractmethod
    def compare(self, other):
        pass

    @abc.abstractmethod
    def name(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def convert_to_logfreq(self):
        pass

    @abc.abstractmethod
    def octaves(self):
        pass

    def __int__(self):
        return self.value

    @abc.abstractmethod
    def embed(self):
        pass

    @abc.abstractmethod
    def from_semitones(cls, semitones):
        pass


class AbstractEnharmonicPitch(abc.ABC):

    @abc.abstractmethod
    def compare(self, other):
        pass

    @abc.abstractmethod
    def name(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def convert_to_logfreq(self):
        pass

    @abc.abstractmethod
    def octaves(self):
        pass

    @abc.abstractmethod
    def freq(self):
        pass

    @abc.abstractmethod
    def pc(self):
        pass

    def __int__(self):
        return self.value

    @abc.abstractmethod
    def midi(self):
        pass

    @abc.abstractmethod
    def from_semitones(cls, semitones):
        pass

    @abc.abstractmethod
    def embed(self):
        pass


@Enharmonic.link_pitch_type()
class EnharmonicPitch(Enharmonic, AbstractEnharmonicPitch, Pitch):

    def steps(self):
        raise PropertyUndefined(f"Property 'steps' is not defined for type {type(self)}.")

    def semitones(self):
        return self.value

    def __init__(self, value):
        """
        Takes a string consisting of the form
        ``<letter><accidentals?><octave>``, e.g. ``"C#4"``, ``"E5"``, or ``"Db-2"``.
        Accidentals may be written as ASCII symbols (#/b)
        or with unicode symbols (♯/♭), but not mixed within the same note.

        or the MIDI value (str or int) of the pitch.

        :param value: a string or internal numeric representation of the pitch
        """
        if isinstance(value, str):
            if value.isdigit():
                value = int(value)
            else:
                octaves, fifths = self.parse_pitch(value)
                assert isinstance(octaves, numbers.Integral)
                assert isinstance(fifths, numbers.Integral)
                octaves -= diatonic_steps_from_fifths(fifths) // 7
                value = fifths * 7 + 12 * (octaves + 1)
        elif isinstance(value, numbers.Integral):
            value = int(value)
        elif isinstance(value, SpelledPitch):
            value = (value.fifths() * 7) % 12 + 12 * (value.octaves() + 1)
        else:
            raise UnexpectedValue(f"Expected string or integer pitch value but got {value}")

        super().__init__(value=value, is_pitch=True, is_class=False)

    @staticmethod
    def from_semitones(semitones):
        """
        Create a pitch by directly providing its internal semitone value.

        Each pitch is represented relative to C0
        by moving the specified number of semitones upwards
        (or downwards for negative values).

        :param semitones: the number of semitones to move from C0
        :return: the resulting pitch (EnharmonicPitch)
        """
        return EnharmonicPitch(semitones)

    def embed(self):
        return self

    def interval_from(self, other):
        if type(other) is EnharmonicPitchClass:
            return EnharmonicIntervalClass.from_semitones((self.value - other.value) % 12)
        else:
            raise TypeError(f"Cannot take interval between EnharmonicPitch and {type(other)}.")

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

    def pc(self):
        return self.to_class()

    def compare(self, other):
        """
        Comparison between two enharmonic pitches according to enharmonic semitone ordering.

        Returns 0 if the objects are equal,
        1 if the first pitch (``self``) is higher,
        and -1 if the second pitch (``other``) is higher.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: a pitch to compare to (EnharmonicPitch)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, EnharmonicPitch):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")


@Enharmonic.link_interval_type()
class EnharmonicInterval(Enharmonic, AbstractEnharmonicInterval, Interval, Chromatic):

    def semitones(self):
        return self.value

    def steps(self):
        raise PropertyUndefined(f"Property 'steps' is not defined for type {type(self)}.")
        
    def __init__(self, value):
        """
        Takes a string consisting of the form
        ``-?<quality><generic-size>:<octaves>``,
        e.g. ``"M6:0"``, ``"-m3:0"``, or ``"aa2:1"``,
        which stand for a major sixth, a minor third down, and a double-augmented ninth, respectively.
        possible qualities are d (diminished), m (minor), M (major), P (perfect), and a (augmented),
        where d and a can be repeated.

        :param value: a string or internal numeric representation of the interval
        """
        if isinstance(value, str):
            if value.isdigit():
                value = int(value)
            else:
                sign, octaves, fifths = self.parse_interval(value)
                assert isinstance(sign, numbers.Integral)
                assert isinstance(octaves, numbers.Integral)
                assert isinstance(fifths, numbers.Integral)
                assert abs(sign) == 1
                assert octaves >= 0
                # correct octaves from fifth steps
                fifths_from_f = fifths + 1
                base_pitch = ((fifths % 7 - 1) * 7) % 12
                accidentals = fifths_from_f // 7
                12 * (octaves + 1) + base_pitch + accidentals
                # negate value for negative intervals
                if sign < 0:
                    value *= -1
        elif isinstance(value, numbers.Integral):
            value = int(value)
        elif isinstance(value, SpelledInterval):
            value = (value.fifths() * 7) % 12 + 12 * value.octaves()
        else:
            raise UnexpectedValue(f"Expected string or integer interval value but got {value}")
        super().__init__(value=value, is_pitch=False, is_class=False)

    @staticmethod
    def from_semitones(semitones):
        """
        Create an interval by directly providing its internal semitone value.

        :param semitones: the semitones (= interval class) of the interval (integer)
        :return: the resulting interval (EnharmonicInterval)
        """
        return EnharmonicInterval(semitones)

    @classmethod
    def unison(cls):
        """
        Create a perfect unison.

        :return: P1:0
        """
        return cls.from_semitones(0)

    @classmethod
    def octave(cls):
        """
        Create a perfect octave.

        :return: P1:1
        """
        return cls.from_semitones(12)

    def __abs__(self):
        if self.direction() < 0:
            return -self
        else:
            return self

    def direction(self):
        """
        Returns the direction of the interval (1 = up, 0 = neutral, -1 = down).
        Only perfect unisons are considered neutral.

        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if self.value == 0:
            return 0
        return self.value // abs(self.value)

    def ic(self):
        return self.to_class()

    def embed(self):
        return self

    @classmethod
    def chromatic_semitone(cls):
        """
        Create a chromatic semitone.

        :return: a1:0
        """
        return EnharmonicInterval.from_semitones(1)

    def to_class(self):
        return self.IntervalClass(value=self.value % 12)

    def name(self):
        sign = "-" if self.value < 0 else ""
        return sign + str(abs(self.value))

    def octaves(self):
        return self.value // 12

    def convert_to_logfreq(self):
        return LogFreq.Interval(2 ** (self.value / 12), is_ratio=True)

    def compare(self, other):
        """
        Comparison between two enharmonic intervals according to enharmonic semitone ordering.

        Returns 0 if the objects are equal,
        1 if the first interval (``self``) is greater,
        and -1 if the second interval (``other``) is greater.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: an interval to compare to (EnharmonicInterval)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, EnharmonicInterval):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")


@Enharmonic.link_pitch_class_type()
class EnharmonicPitchClass(Enharmonic, AbstractEnharmonicPitch, Pitch):

    def steps(self):
        raise PropertyUndefined(f"Property 'steps' is not defined for type {type(self)}.")
      
    def midi(self):
        """
        Return the MIDI value of the pitch class, a value in the range [0, 11].
        """
        return self.value

    def semitones(self):
        """
        Equivalent to the MIDI value of the pitch class.
        """
        return self.value

    def __init__(self, value):
        """
        Takes a string consisting of the form
        ``<letter><accidentals?>``, e.g. ``"C#"``, ``"E"``, or ``"Dbb"``.
        Accidentals may be written as ASCII symbols (#/b)
        or with unicode symbols (♯/♭), but not mixed within the same note.

        :param value: a string or internal numeric representation of the pitch class
        """
        if isinstance(value, str):
            if value.isdigit():
                value = int(value)
            else:
                octaves, fifths = self.parse_pitch(value)
                assert isinstance(fifths, numbers.Integral)
                assert octaves is None
                value = (fifths * 7) % 12
        elif isinstance(value, numbers.Integral):
            value = int(value)
        elif isinstance(value, SpelledPitchClass) or isinstance(value, SpelledPitch):
            value = (value.fifths() * 7) % 12
        else:
            raise UnexpectedValue(f"Expected string or integer pitch class value but got {value}")
        super().__init__(value=value, is_pitch=True, is_class=True)

    def freq(self):
        return 2 ** ((self.value - 69) / 12) * 440

    def octaves(self):
        return None

    def from_semitones(cls, semitones):
        return cls(semitones)

    def pc(self):
        return self

    def interval_from(self, other):
        if type(other) is EnharmonicPitchClass:
            return EnharmonicIntervalClass.from_semitones((self.value - other.value) % 12)
        else:
            raise TypeError(f"Cannot take interval between EnharmonicPitchClass and {type(other)}.")

    def embed(self):
        return EnharmonicPitch.from_semitones(self.value)

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

    def compare(self, other):
        """
        Comparison between two enharmonic pitch classes according to enharmonic semitone ordering.

        Returns 0 if the objects are equal,
        1 if the first pitch class (``self``) is higher,
        and -1 if the second pitch class (``other``) is higher.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: a pitch class to compare to (EnharmonicPitchClass)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, EnharmonicPitchClass):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")


@Enharmonic.link_interval_class_type()
class EnharmonicIntervalClass(Enharmonic, AbstractEnharmonicInterval, Interval, Chromatic):

    def semitones(self):
        return self.value

    def steps(self):
        raise PropertyUndefined(f"Property 'steps' is not defined for type {type(self)}.")

    def __init__(self, value):
        """
        Takes a string consisting of the form
        ``-?<quality><generic-size>``,
        e.g. ``"M6"``, ``"-m3"``, or ``"aa2"``,
        which stand for a major sixth, a minor third down (= major sixth up), and a double-augmented second, respectively.
        possible qualities are d (diminished), m (minor), M (major), P (perfect), and a (augmented),
        where d and a can be repeated.

        :param value: a string or internal numeric representation of the interval class
        """
        if isinstance(value, str):
            if value.isdigit():
                value = int(value)
            else:
                sign, octaves, fifths = self.parse_interval(value)
                assert isinstance(sign, numbers.Integral)
                assert abs(sign) == 1
                assert octaves is None
                assert isinstance(fifths, numbers.Integral)
                value = ((fifths * 7) % 12) * sign
        elif isinstance(value, numbers.Integral):
            value = value
        elif isinstance(value, SpelledIntervalClass) or isinstance(value, SpelledInterval):
            value = (value.fifths() * 7) % 12
        else:
            raise UnexpectedValue(f"Expected string or integer interval class value but got {value}")
        super().__init__(value=value, is_pitch=False, is_class=True)

    @classmethod
    def octave(cls):
        """
        Return a perfect unison, which is the same as an octave for interval classes.

        :return: P1
        """
        return cls.from_semitones(0)

    @classmethod
    def octaves(self):
        return None

    @staticmethod
    def from_semitones(semitones):
        """
        Create an interval class by directly providing its internal semitones.

        :param semitones: the semitones (= interval class) of the interval (integer)
        :return: the resulting interval class (EnharmonicIntervalClass)
        """
        return EnharmonicIntervalClass(semitones)

    @classmethod
    def unison(cls):
        """
        Return a perfect unison.

        :return: P1
        """
        return cls.from_semitones(0)

    @classmethod
    def chromatic_semitone(cls):
        """
        Return a chromatic semitone

        :return: a1
        """
        return EnharmonicIntervalClass.from_semitones(0)

    def embed(self):
        return EnharmonicInterval.from_semitones(self.value)

    def ic(self):
        return self

    @classmethod
    def octave(cls):
        return 0

    def __abs__(self):
        if self.direction() < 0:
            return -self
        else:
            return self

    def direction(self):
        """
        Returns the direction of the interval (1 = up, 0 = neutral, -1 = down).
        Only perfect unisons are considered neutral.

        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if self.value == 0:
            return 0
        return self.value // abs(self.value)

    def name(self):
        sign = "-" if self.value < 0 else ""
        return sign + str(abs(self.value))

    def convert_to_logfreq(self):
        return LogFreq.IntervalClass(2 ** (self.value / 12), is_ratio=True)

    def compare(self, other):
        """
        Comparison between two enharmonic interval classes according to enharmonic semitone ordering.

        Returns 0 if the objects are equal,
        1 if the first interval class (``self``) is greater,
        and -1 if the second interval class (``other``) is greater.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: an interval class to compare to (EnharmonicIntervalClass)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, EnharmonicIntervalClass):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")
