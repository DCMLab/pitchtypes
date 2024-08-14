import numpy as np
from pitchtypes.basetypes import AbstractBase, Pitch, Interval, Diatonic
from pitchtypes.utils import diatonic_steps_from_fifths
from pitchtypes.spelled import Spelled, SpelledPitch, SpelledInterval, SpelledPitchClass, SpelledIntervalClass
from pitchtypes.errors import UnexpectedValue, PropertyUndefined
import functools
import abc
import numbers


@functools.total_ordering
class Generic(AbstractBase):
    """
    A common base class for generic pitch and interval types.
    See below for a set of common operations.
    """

    # how should Pitch and PitchClass types be printed
    _print_as_int = False

    @classmethod
    def print_options(cls, as_int=None):
        if cls == Generic:
            Generic.Pitch.print_options(as_int=as_int)
            Generic.PitchClass.print_options(as_int=as_int)
        if as_int is not None:
            cls._print_as_int = as_int
        if as_int is None:
            print(f"print options in {cls.__name__}:\n"
                  f"    as_int: {cls._print_as_int}")

    @staticmethod
    def pitch_class_from_diatonic_steps(diatonic_steps):
        """
        Return the pitch class given the number of steps

        :param diatonic_steps: number of diatonic steps
        :return: pitch class (C, D, E, F, G, A, B)
        """
        base_pitch = ["C", "D", "E", "F", "G", "A", "B"][diatonic_steps % 7]
        return base_pitch

    @staticmethod
    def generic_interval_class_from_fifths(fifth_steps):
        """
        Return the generic interval class corresponding to the given number of fifths. This corresponds to the number of
        diatonic steps plus one. The generic interval also corresponds to the scale degree when interpreted as the tone
        reached when starting from the tonic.

        :param fifth_steps: number of fifth steps
        :return: scale degree (integer in 1,...,7)

        :meta private:
        """
        return diatonic_steps_from_fifths(fifth_steps) % 7 + 1

    @staticmethod
    def _degree_from_diatonic_steps_(diatonic_steps):
        """
        Return the scale degree of a pitch/interval based on its diatonic steps.
        Helper function for degree()

        :meta private:
        """
        return diatonic_steps % 7 + 1

    def __init__(self, value, is_pitch, is_class, **kwargs):
        # pre-process value
        if isinstance(value, str):
            if is_pitch:
                if is_class:
                    value = Spelled.PitchClass(value=value).convert_to(GenericPitchClass).value
                else:
                    value = Spelled.Pitch(value=value).convert_to(GenericPitch).value
            else:
                if is_class:
                    value = Spelled.IntervalClass(value=value).convert_to(GenericIntervalClass).value
                else:
                    value = Spelled.Interval(value=value).convert_to(GenericInterval).value
        elif isinstance(value, numbers.Number):
            int_value = int(value)
            if int_value != value:
                raise UnexpectedValue(f"Expected integer pitch value but got {value}")
            value = int_value
            if is_class:
                value = value % 7
        # hand on initialisation to other base classes
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)

    def __repr__(self):
        return self.name()

    def __str__(self):
        return self.name()

    def name(self):
        """
        The name of the pitch or interval in string notation

        :return: the object's notation name (string)
        """
        raise NotImplementedError

    def compare(self, other):
        """
        Comparison between two generic types.

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

    @abc.abstractmethod
    def steps(self):
        """
        Return the position of the interval in diatonic steps.

        :return: fifth position (integer)
        """
        raise NotImplementedError

    def octaves(self):
        """
        For intervals, return the number of octaves the interval spans.
        Negative intervals start with -1, decreasing.
        For pitches, return the absolute octave of the pitch.

        :return: external/independent octave (integer)
        """
        raise NotImplementedError

    def internal_octaves(self):
        """
        Return the internal octave representation of a pitch

        Only use this if you know what you are doing.

        :return: internal/dependent octave (integer)
        """
        raise NotImplementedError

    def degree(self):
        """
        Return the "relative scale degree" (0-6) to which the interval points
        (unison=0, 2nd=1, octave=0, 2nd down=6, etc.).
        For pitches, return the integer that corresponds to the letter (C=0, D=1, ...).

        :return: degree (integer)
        """
        return self._degree_from_fifths_(self.steps)

    def onehot(self):
        """
        Return a one-hot encoded tensor representing the object.
        Specialized versions of this method take ranges for their respective dimensions.

        :return: one-hot encoding of the object (numpy array)
        """
        raise NotImplementedError

    @staticmethod
    def pitch_class_name_from_steps(step_pitch):
        """
        Return the pitch class name for the given pitch in steps, alias for pitch_class_from_diatonic_steps

        :param step_pitch: step pitch
        :return: pitch class
        """

        return Generic.pitch_class_from_diatonic_steps(step_pitch)


class AbstractGenericInterval(abc.ABC):
    @abc.abstractmethod
    def compare(self, other):
        pass

    @abc.abstractmethod
    def name(self, *args, **kwargs):
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
    def from_steps(cls, steps):
        pass


class AbstractGenericPitch(abc.ABC):
    @abc.abstractmethod
    def compare(self, other):
        pass

    @abc.abstractmethod
    def name(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def octaves(self):
        pass

    @abc.abstractmethod
    def pc(self):
        pass

    def __int__(self):
        return self.value

    @abc.abstractmethod
    def from_steps(cls, steps):
        pass

    @abc.abstractmethod
    def embed(self):
        pass


@Generic.link_pitch_type()
class GenericPitch(Generic, AbstractGenericPitch, Pitch):
    def compare(self, other):
        """
        Comparison between two generic pitches according to diatonic ordering.

        Returns 0 if the objects are equal,
        1 if the first pitch (``self``) is higher,
        and -1 if the second pitch (``other``) is higher.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: a pitch to compare to (GenericPitch)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, GenericPitch):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def semitones(self):
        raise PropertyUndefined(f"Property 'semitones' is not defined for type {type(self)}")

    def midi(self):
        raise PropertyUndefined(f"Property 'semitones' is not defined for type {type(self)}")

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
                value = (fifths * 4) % 7 + 7 * (octaves + 1)
        elif isinstance(value, numbers.Integral):
            value = int(value)
        elif isinstance(value, SpelledPitch):
            value = (value.fifths() * 4) % 7 + 7 * (value.octaves() + 1)
        else:
            raise UnexpectedValue(f"Expected string or integer pitch value but got {value}")

        super().__init__(value=value, is_pitch=True, is_class=False)

    @staticmethod
    def from_steps(steps):
        """
        Create a pitch by directly providing its internal step value.

        Each pitch is represented relative to C0
        by moving the specified number of steps upwards
        (or downwards for negative values).

        :param steps: the number of steps to move from C0
        :return: the resulting pitch (GenericPitch)
        """
        return GenericPitch(steps)

    def embed(self):
        return self

    def interval_from(self, other):
        if type(other) is GenericPitchClass:
            return GenericIntervalClass.from_steps((self.value - other.value) % 7)
        else:
            raise TypeError(f"Cannot take interval between GenericPitch and {type(other)}.")

    def to_class(self):
        return self.PitchClass(value=self.value % 7)

    def name(self, as_int=None):
        if as_int is None:
            as_int = self._print_as_int
        if as_int:
            return str(self.value)
        return self.pitch_class_name_from_steps(self.value) + str(self.octaves())

    def octaves(self):
        return self.value // 7 - 1

    @property
    def steps(self):
        return self.value

    def pc(self):
        return self.to_class()


@Generic.link_interval_type()
class GenericInterval(Generic, AbstractGenericInterval, Interval, Diatonic):

    def compare(self, other):
        """
        Comparison between two generic intervals according to diatonic ordering.

        Returns 0 if the intervals are equal,
        1 if the first interval (``self``) is greater,
        and -1 if the second interval (``other``) is greater.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: an interval to compare to (GenericInterval)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, GenericInterval):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def steps(self):
        """
        Return the step value of the interval, a value in the range [-6, 6].
        """
        return self.value

    def semitones(self):
        raise PropertyUndefined(f"Property 'semitones' is not defined for type {type(self)}")

    def is_step(self):
        return True

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
                value = (fifths * 4) % 7 + 7 * octaves
                # negate value for negative intervals
                if sign < 0:
                    value *= -1
        elif isinstance(value, numbers.Integral):
            value = int(value)
        elif isinstance(value, SpelledInterval):
            value = (value.fifths() * 4) % 7 + 7 * value.octaves()
        else:
            raise UnexpectedValue(f"Expected string or integer interval value but got {value}")
        super().__init__(value=value, is_pitch=False, is_class=False)

    @staticmethod
    def from_steps(steps):
        """
        Create an interval by directly providing its internal step value.

        :param steps: the steps (= interval class) of the interval (integer)
        :return: the resulting interval (GenericInterval)
        """
        return GenericInterval(steps)

    @classmethod
    def unison(cls):
        """
        Create a perfect unison.

        :return: P1:0
        """
        return cls.from_steps(0)

    @classmethod
    def octave(cls):
        """
        Create a perfect octave.

        :return: P1:1
        """
        return cls.from_steps(7)

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
    def diatonic_step(cls):
        """
        Create a chromatic semitone.

        :return: a1:0
        """
        return GenericInterval.from_steps(1)

    def to_class(self):
        return self.IntervalClass(value=self.value % 7)

    def name(self):
        sign = "-" if self.value < 0 else ""
        return sign + str(abs(self.value))

    def octaves(self):
        return self.value // 7


@Generic.link_pitch_class_type()
class GenericPitchClass(Generic, AbstractGenericPitch, Pitch):

    def compare(self, other):
        """
        Comparison between two spelled pitch classes according to diatonic steps.

        Returns 0 if the pitch classes are equal,
        1 if the first pitch class (``self``) is greater ("sharper"),
        and -1 if the second pitch class (``other``) is greater ("sharper").

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: a pitch class to compare to (GenericPitchClass)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, GenericPitchClass):
            return np.sign(self.steps() - other.steps())
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def semitones(self):
        raise PropertyUndefined(f"Property 'semitones' is not defined for type {self.__class__.__name__}")

    def midi(self):
        raise PropertyUndefined(f"Property 'semitones' is not defined for type {self.__class__.__name__}")

    def steps(self):
        """
        Return the step value of the pitch class, a value in the range [0, 6].
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
                value = (fifths * 4) % 7
        elif isinstance(value, numbers.Integral):
            value = int(value)
        elif isinstance(value, SpelledPitchClass) or isinstance(value, SpelledPitch):
            value = (value.fifths() * 4) % 7
        else:
            raise UnexpectedValue(f"Expected string or integer pitch class value but got {value}")
        super().__init__(value=value, is_pitch=True, is_class=True)

    def octaves(self):
        return None

    def from_steps(cls, steps):
        return cls(steps)

    def pc(self):
        return self

    def interval_from(self, other):
        if type(other) is GenericPitchClass:
            return GenericIntervalClass.from_steps((self.value - other.value) % 7)
        else:
            raise TypeError(f"Cannot take interval between EnharmonicPitchClass and {type(other)}.")

    def embed(self):
        return GenericPitch.from_steps(self.value)

    def name(self, as_int=None):
        if as_int is None:
            as_int = self._print_as_int
        if as_int:
            return str(self.value)
        return self.pitch_class_name_from_steps(self.value)


@Generic.link_interval_class_type()
class GenericIntervalClass(Generic, AbstractGenericInterval, Interval, Diatonic):

    def compare(self, other):
        """
        Comparison between two spelled interval classes according to diatonic steps.

        Returns 0 if the interval classes are equal,
        1 if the first interval class (``self``) is greater ("sharper"),
        and -1 if the second interval class (``other``) is greater ("sharper").

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: an interval class to compare to (GenericIntervalClass)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, GenericIntervalClass):
            return np.sign(self.steps() - other.steps())
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def steps(self):
        """
        Return the step value of the interval class, a value in the range [-6, 6].
        """
        return self.value

    def semitones(self):
        raise PropertyUndefined(f"Property 'semitones' is not defined for type {type(self)}")

    def is_step(self):
        return True

    def from_steps(cls, steps):
        return cls(steps)

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
                value = ((fifths * 4) % 7) * sign
        elif isinstance(value, numbers.Integral):
            value = value
        elif isinstance(value, SpelledIntervalClass) or isinstance(value, SpelledInterval):
            value = (value.fifths() * 4) % 7
        else:
            raise UnexpectedValue(f"Expected string or integer interval class value but got {value}")
        super().__init__(value=value, is_pitch=False, is_class=True)

    @classmethod
    def octave(cls):
        """
        Return a perfect unison, which is the same as an octave for interval classes.

        :return: P1
        """
        return cls.from_steps(0)

    @classmethod
    def octaves(self):
        return None

    @staticmethod
    def from_steps(steps):
        """
        Create an interval class by directly providing its internal steps.

        :param steps: the steps (= interval class) of the interval (integer)
        :return: the resulting interval class (GenericIntervalClass)
        """
        return GenericIntervalClass(steps)

    @classmethod
    def unison(cls):
        """
        Return a perfect unison.

        :return: P1
        """
        return cls.from_steps(0)

    @classmethod
    def diatonic_step(cls):
        """
        Return a diatonic step.

        :return: a1
        """
        return GenericIntervalClass.from_steps(0)

    def embed(self):
        return GenericInterval.from_steps(self.value)

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
