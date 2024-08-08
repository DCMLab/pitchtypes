#  Copyright (c) 2022 Robert Lieck, Christoph Finkensiep

import numbers
import abc
import functools
from typing import Tuple, Union

import numpy as np

from pitchtypes.basetypes import AbstractBase, Pitch, Interval, Diatonic, Chromatic
from pitchtypes import utils


@functools.total_ordering
class Generic(AbstractBase):
    """
    A common base class for Generic pitch and interval types.
    See below for a set of common operations.
    """

    _pitch_regex = utils.PITCH_REGEX
    _interval_regex = utils.INTERVAL_REGEX

    @staticmethod
    def parse_pitch(s):
        """
        Parse a string as a Generic pitch or Generic pitch class. Returns a tuple (octave, fifths), where octave
        indicates the octave the pitch lies in (None for Generic pitch classes) and fifths indicates the steps taken
        along the line of fifths.

        :param s: string to parse
        :return: (octave, fifths)

        :meta private:
        """
        if not isinstance(s, str):
            raise TypeError(f"expected string as input, got {s}")
        # convert unicode flats and sharps (♭ -> b and ♯ -> #)
        s = s.replace("♭", "b")
        s = s.replace("♯", "#")
        # match with regex
        pitch_match = Generic._pitch_regex.match(s)
        if pitch_match is None:
            raise ValueError(
                f"could not match '{s}' with regex: '{Generic._pitch_regex.pattern}'"
            )
        octave = pitch_match["octave"]
        # initialise fifth steps from diatonic pitch class
        fifth_steps = Generic.fifths_from_diatonic_pitch_class(pitch_match["class"])
        # add modifiers
        if "#" in pitch_match["modifiers"]:
            fifth_steps += 7 * len(pitch_match["modifiers"])
        else:
            fifth_steps -= 7 * len(pitch_match["modifiers"])
        # add octave
        if octave == "":
            return None, fifth_steps
        else:
            return int(octave), fifth_steps

    @staticmethod
    def parse_interval(s):
        """
        Parse a string as a Generic interval or Generic interval class. Returns a tuple (sign, octave, fifths), where
        sign is +1 or -1 and indicates the sign given in the string (no sign means positive), octave indicates the
        number of full octave steps (in positive or negative direction; None for Generic interval classes), and fifths
        indicates the steps taken along the line of fifths (i.e. not actual fifth steps that would add to the octaves).

        :param s: string to parse
        :return: (sign, octave, fifths)

        :meta private:
        """
        if not isinstance(s, str):
            raise TypeError("expecte string as input, got {s}")
        interval_match = Generic._interval_regex.match(s)
        if interval_match is None:
            raise ValueError(
                f"could not match '{s}' with regex: '{Generic._interval_regex.pattern}'"
            )
        # get quality and generic interval (first corresponding group that is not None)
        for i in range(3):
            g = interval_match[f"generic{i}"]
            q = interval_match[f"quality{i}"]
            if g is not None and q is not None:
                generic = int(g)
                quality = q
                break
        else:
            raise RuntimeError(
                f"Could not match generic interval and quality, this is a bug in the regex ("
                f"{[interval_match[f'generic{i}'] for i in range(3)]}, "
                f"{[interval_match[f'quality{i}'] for i in range(3)]}"
                f")"
            )
        # initialise value with generic interval classes
        fifth_steps = Generic.fifths_from_generic_interval_class(generic)
        # add modifiers
        if quality in ["P", "M"]:
            pass
        elif quality == "m":
            fifth_steps -= 7
        elif "a" in quality:
            fifth_steps += 7 * len(quality)
        elif "d" in quality:
            if generic in [4, 1, 5]:
                fifth_steps -= 7 * len(quality)
            else:
                fifth_steps -= 7 * (len(quality) + 1)
        else:
            raise RuntimeError(
                f"Initialization from string failed: "
                f"Unexpected interval quality '{quality}'. This is a bug and "
                f"means that either the used regex is bad or the handling code."
            )
        # get octave
        if interval_match["octave"][1:] == "":
            octave = None
        else:
            octave = int(interval_match["octave"][1:])
        # get sign and bring adapt fifth steps
        if interval_match["sign"] == "-":
            sign = -1
        else:
            sign = 1
        return sign, octave, fifth_steps

    @staticmethod
    def pitch_class_from_fifths(fifth_steps: int) -> str:
        """
        Return the pitch class given the number of steps along the line of fifths

        :param fifth_steps: number of steps along the line of fifths
        :return: generic pitch class (e.g. C, B, F, A etc.)

        :meta private:
        """
        base_pitch = ["F", "C", "G", "D", "A", "E", "B"][(fifth_steps + 1) % 7]
        return base_pitch

    @staticmethod
    def generic_interval_class_from_fifths(fifth_steps: int) -> int:
        """
        Return the generic interval class corresponding to the given number of fifths. This corresponds to the number of
        diatonic steps plus one. The generic interval also corresponds to the scale degree when interpreted as the tone
        reached when starting from the tonic.

        :param fifth_steps: number of fifth steps
        :return: scale degree (integer in 1,...,7)

        :meta private:
        """
        return utils.diatonic_steps_from_fifths(fifth_steps) % 7 + 1

    @staticmethod
    def interval_class_from_fifths(fifths: int, inverse: bool = False):
        """
        Return the interval class corresponding to the given number of steps along the line of fifths. This function
        combines Generic.interval_quality_from_fifths and Generic.generic_interval_class_from_fifths. Specifying
        inverse=True (default is False) returns the inverse interval class (m2 for M7, aa4 for dd5 etc.).

        :param fifths: number of fifth steps
        :param inverse: whether to return the inverse interval class
        :return: interval class (p1, M3, aa6 etc.)

        :meta private:
        """
        if inverse:
            fifths = -fifths
        return f"{Generic.generic_interval_class_from_fifths(fifths)}"

    def __init__(self, value, is_pitch, is_class, **kwargs):
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)
        if not is_class:
            self.value.flags.writeable = False

    def __repr__(self):
        return self.name()

    def name(self):
        """
        The name of the pitch or interval in string notation

        :return: the object's notation name (string)
        """
        raise NotImplementedError

    def compare(self, other):
        """
        Comparison between two Generic types.

        Returns 0 if the objects are equal,
        1 if the first object (``self``) is greater,
        and -1 if the second object (``other``) is greater.

        The respective ordering differs between types.
        Non-class pitches and intervals use diatonic ordering,
        interval/pitch classes use line-of-fifths ordering.

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

    # Generic interface:

    def fifths(self):
        """
        Return the position of the interval on the line of fifths.

        :return: fifth position (integer)
        """
        raise NotImplementedError

    def steps(self):
        """
        Return the diatonic steps of the object.
        For intervals: unison=0, 2nd=1, ..., 7th=6
        For pitches: C=0, D=1, ..., B=6.

        :return: number of diatonic steps (integer)
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
        Return the internal octave representation of a pitch,
        which is dependent on the fifths.

        Only use this if you know what you are doing.

        :return: internal/dependent octave (integer)
        """
        raise NotImplementedError

    def degree(self) -> int:
        """
        Return the "scale degree" or "generic interval" (1-7).
        For pitches, return the integer that corresponds to the letter (C=1, D=2, ...).

        :return: degree (integer)
        """
        return self.steps() + 1

    def alteration(self):
        """
        Return the number of semitones by which the interval is altered from its the perfect or major variant.
        Positive alteration always indicates augmentation,
        negative alteration indicates diminution (minor or smaller) of the interval.
        For pitches, return the accidentals (positive=sharps, negative=flats, 0=natural).

        :return: alteration (integer)
        """
        raise NotImplementedError

    def onehot(self):
        """
        Return a one-hot encoded tensor representing the object.
        Specialized versions of this method take ranges for their respective dimensions.

        :return: one-hot encoding of the object (numpy array)
        """
        raise NotImplementedError


class AbstractGenericInterval(abc.ABC):
    """
    The interface for Generic interval types.
    """

    pass


class AbstractGenericPitch(abc.ABC):
    """
    The interface for Generic pitch types.
    """

    @abc.abstractmethod
    def letter(self):
        """
        Returns the letter associated with the pitch (without accidentals).

        :return: letter (single-character string)
        """
        raise NotImplementedError


@Generic.link_pitch_type()
class GenericPitch(Generic, AbstractGenericPitch, Pitch):
    """
    Represents a Generic pitch.
    """

    def __init__(self, value: Union[str, Tuple[int, int]]):
        """
        Takes a string consisting of the form
        ``<letter><accidentals?><octave>``, e.g. ``"C#4"``, ``"E5"``, or ``"Db-2"``.
        Accidentals may be written as ASCII symbols (#/b)
        or with unicode symbols (♯/♭), but not mixed within the same note.

        :param value: a string or internal numeric representation of the pitch (<internal_octave>, [0-6])
        """
        if isinstance(value, str):
            octaves, fifths = self.parse_pitch(value)
            steps = utils.diatonic_steps_from_fifths(fifths)
        else:
            octaves, steps = value
        steps %= 7
        value = np.array([octaves, steps])
        assert isinstance(steps, numbers.Integral)
        assert isinstance(octaves, numbers.Integral)
        super().__init__(value=value, is_pitch=True, is_class=False)

    @staticmethod
    def from_fifths_and_octaves(fifths, octaves):
        """
        Create a pitch by directly providing fifths and octaves.

        Each pitch is represented relative to C0
        by moving the specified number of fifths and octaves upwards
        (or downwards for negative values).

        :param fifths: the fifth (= pitch class) of the pitch (integer)
        :param octaves: the internal/dependent octave of the pitch (integer)
        :return: the resulting pitch (GenericPitch)
        """
        return GenericPitch((octaves, utils.diatonic_steps_from_fifths(fifths)))

    @staticmethod
    def from_independent(steps: int, octaves: int):
        """
        Create a pitch from fifths (pitch class) and independent/external octaves (octave number).

        :param steps: the steps (= generic pitch class 0-6) of the pitch (integer)
        :param octaves: the external/independent octave of the pitch (integer)
        :return: the resulting pitch (GenericPitch)
        """
        return GenericPitch(octaves, steps)

    @staticmethod
    def from_onehot(onehot, octave_low):
        """
        Create a Generic pitch from a one-hot matrix.

        Requires the lower bounds of the fifth and octave range used by the one-hot matrix.

        :param onehot: a one-hot matrix representing the pitch (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot matrix
        :param octave_low: the lowest octave expressible in the one-hot matrix
        :return: the resulting pitch (GenericPitch)
        """
        if onehot.sum() != 1:
            raise ValueError(f"{onehot} is not a one-hot vector.")
        fs, os = np.where(onehot == 1)
        return GenericPitch.from_independent(fs[0], os[0] + octave_low)

    # Pitch interface

    def interval_from(self, other):
        if type(other) is GenericPitch:
            octaves1, steps1 = self.value
            octaves2, steps2 = other.value
            return GenericInterval((octaves1 - octaves2, steps1 - steps2))
        else:
            raise TypeError(
                f"Cannot take interval between GenericPitch and {type(other)}."
            )

    def to_class(self):
        return self.PitchClass(self.steps())

    def pc(self):
        return self.to_class()

    def embed(self):
        return self

    # Generic interface

    def name(self):
        return f"{self.pitch_class_from_fifths(self.fifths())}{self.octaves()}"

    def compare(self, other):
        """
        Comparison between two Generic pitches according to diatonic ordering.

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

    def steps(self) -> int:
        return self.value[1]

    def octaves(self) -> int:
        return self.value[0] + 1

    def internal_octaves(self) -> int:
        return self.value[0]

    def alteration(self):
        return NotImplementedError

    def letter(self) -> str:
        return ["A", "B", "C", "D", "E", "F", "G"][self.steps()]

    def onehot(self, octave_range, dtype=int):
        """
        Returns a one-hot encoding of the pitch in fifths (first dimension) and external octaves (second dimension).
        The range of fifths and octaves is given by ``fifth_range`` and ``octave_range`` respectively,
        where each is a pair ``(lower, upper)``.

        :param fifth_range: the (inclusive) range of fifths (pair of integers)
        :param octave_range: the (inclusive) range of octaves (pair of integers)
        :param dtype: dtype of the resulting array
        :return: a one-hot matrix (numpy array)
        """
        slow, shigh = (0, 6)
        olow, ohigh = octave_range
        st = self.steps()
        o = self.octaves()
        if st < slow or st > shigh:
            raise ValueError(f"The pitch {self} is outside the range (0, 6).")
        if o < olow or o > ohigh:
            raise ValueError(
                f"The pitch {self} is outside the given octave range {octave_range}."
            )
        out = np.zeros((shigh - slow + 1, ohigh - olow + 1), dtype=dtype)
        out[st - slow, o - olow] = 1
        return out


@Generic.link_interval_type()
class GenericInterval(Generic, AbstractGenericInterval, Interval, Diatonic, Chromatic):
    """
    Represents a Generic interval.
    """

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
            sign, octaves, fifths = self.parse_interval(value)
            assert isinstance(sign, numbers.Integral)
            assert isinstance(octaves, numbers.Integral)
            assert isinstance(fifths, numbers.Integral)
            assert abs(sign) == 1
            assert octaves >= 0
            # correct octaves from fifth steps
            octaves -= utils.diatonic_steps_from_fifths(fifths) // 7
            value = np.array([octaves, fifths])
            # negate value for negative intervals
            if sign < 0:
                value *= -1
        else:
            octaves, fifths = value
            assert isinstance(octaves, numbers.Integral)
            assert isinstance(fifths, numbers.Integral)
            value = np.array([octaves, fifths])
        super().__init__(value=value, is_pitch=False, is_class=False)

    @staticmethod
    def from_fifths_and_octaves(fifths, octaves):
        """
        Create an interval by directly providing its internal fifths and octaves.

        :param fifths: the fifths (= interval class) of the interval (integer)
        :param octaves: the internal/dependent octaves of the interval (integer)
        :return: the resulting interval (GenericInterval)
        """
        return GenericInterval((octaves, fifths))

    @staticmethod
    def from_independent(fifths, octaves):
        """
        Create an interval from fifths (interval class) and independent/external octaves.

        :param fifths: the fifth (= interval class) of the interval (integer)
        :param octaves: the external/independent octaves the interval spans (integer)
        :return: the resulting interval (GenericInterval)
        """
        return GenericInterval.from_fifths_and_octaves(
            fifths, octaves - (fifths * 4) // 7
        )

    @staticmethod
    def from_onehot(onehot, fifth_low, octave_low):
        """
        Create a Generic interval from a one-hot matrix.

        Requires the lower bounds of the fifth and octave range used by the one-hot matrix.

        :param onehot: a one-hot matrix representing the interval (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot matrix
        :param octave_low: the lowest octave expressible in the one-hot matrix
        :return: the resulting interval (GenericInterval)
        """
        if onehot.sum() != 1:
            raise ValueError(f"{onehot} is not a one-hot vector.")
        fs, os = np.where(onehot == 1)
        return GenericInterval.from_independent(fs[0] + fifth_low, os[0] + octave_low)

    # interval interface

    @classmethod
    def unison(cls):
        """
        Create a perfect unison.

        :return: P1:0
        """
        return cls.from_fifths_and_octaves(0, 0)

    @classmethod
    def octave(cls):
        """
        Create a perfect octave.

        :return: P1:1
        """
        return cls.from_fifths_and_octaves(0, 1)

    @classmethod
    def chromatic_semitone(cls):
        """
        Create a chromatic semitone.

        :return: a1:0
        """
        return GenericInterval.from_fifths_and_octaves(7, -4)

    def direction(self):
        """
        Returns the direction of the interval (1 = up, 0 = neutral, -1 = down).
        Only perfect unisons are considered neutral.

        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        ds = self.diatonic_steps()
        if ds == 0:
            alt = (self.fifths() + 1) // 7
            if alt == 0:
                return 0
            elif alt < 0:
                return -1
            else:
                return 1
        elif ds < 0:
            return -1
        else:
            return 1

    def __abs__(self):
        if self.direction() < 0:
            return -self
        else:
            return self

    def to_class(self):
        return self.IntervalClass(self.value[1])

    def ic(self):
        return self.to_class()

    def embed(self):
        return self

    def is_step(self):
        return abs(self.diatonic_steps()) <= 1

    # Generic interface

    def name(self):
        octave = abs(self.octaves())
        if self.direction() == -1:
            # negative intervals are to be printed with "-" sign
            sign = "-"
            # in return we have to invert the interval class
            inverse = True
            # in the interval representation, the octave "0" is positive, while "-1" is the first negative octave;
            # an octave of "-1" in internal representation (i.e. the first negative octave) therefore corresponds to an
            # octave "0" with negative sign in printing; we thus need to subtract one from the absolute value for
            # printing; the unison (perfect, diminished or augmented) are an exception because they correspond to
            # zero diatonic steps (when ignoring the octave)
            if self.diatonic_steps() % 7 != 0:
                octave -= 1
        else:
            sign = ""
            inverse = False
        return (
            sign
            + self.interval_class_from_fifths(self.fifths(), inverse=inverse)
            + f":{octave}"
        )

    def compare(self, other):
        """
        Comparison between two Generic intervals according to diatonic ordering.

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
        return self.value[1]

    def octaves(self):
        return self.value[0] + (self.fifths() * 4) // 7

    def internal_octaves(self):
        return self.value[0]

    def generic(self):
        if self.direction() < 0:
            return -(-self).degree()
        else:
            return self.degree()

    def diatonic_steps(self):
        return (self.fifths() * 4) + (self.internal_octaves() * 7)

    def alteration(self):
        return (abs(self).fifths() + 1) // 7

    def onehot(self, fifth_range, octave_range, dtype=int):
        """
        Returns a one-hot encoding of the interval in fifths (first dimension) and independent octaves
        (second dimension). The range of fifths and octaves is given by ``fifth_range`` and ``octave_range``
        respectively, where each is a tuple ``(lower, upper)``.

        :param fifth_range: the (inclusive) range of fifths (pair of integers)
        :param octave_range: the (inclusive) range of octaves (pair of integers)
        :param dtype: dtype of the resulting array
        :return: a one-hot matrix (numpy array)
        """
        flow, fhigh = fifth_range
        olow, ohigh = octave_range
        f = self.fifths()
        o = self.octaves()
        if f < flow or f > fhigh:
            raise ValueError(
                f"The interval {self} is outside the given fifth range {fifth_range}."
            )
        if o < olow or o > ohigh:
            raise ValueError(
                f"The interval {self} is outside the given octave range {octave_range}."
            )
        out = np.zeros((fhigh - flow + 1, ohigh - olow + 1), dtype=dtype)
        out[f - flow, o - olow] = 1
        return out


@Generic.link_pitch_class_type()
class GenericPitchClass(Generic, AbstractGenericPitch, Pitch):
    """
    Represents a Generic pitch class, i.e. a pitch without octave information.
    """

    def __init__(self, value):
        """
        Takes a string consisting of the form
        ``<letter><accidentals?>``, e.g. ``"C#"``, ``"E"``, or ``"Dbb"``.
        Accidentals may be written as ASCII symbols (#/b)
        or with unicode symbols (♯/♭), but not mixed within the same note.

        :param value: a string or internal numeric representation of the pitch class
        """
        if isinstance(value, str):
            octaves, fifths = self.parse_pitch(value)
            assert octaves is None
        else:
            fifths = value
        assert isinstance(fifths, numbers.Integral)
        super().__init__(value=fifths, is_pitch=True, is_class=True)

    @staticmethod
    def from_fifths(fifths):
        """
        Create a pitch class by directly providing its position on the line of fifths (C=0, G=1, D=2, ...).

        :param fifths: the line-of-fifths position of the pitch class (integer)
        :return: the resulting pitch class (GenericPitchClass)
        """
        return GenericPitchClass(fifths)

    @staticmethod
    def from_onehot(onehot, fifth_low):
        """
        Create a Generic pitch class from a one-hot vector.

        Requires the lower bounds of the fifth range used by the one-hot vector.

        :param onehot: a one-hot vector representing the pitch (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot vector
        :return: the resulting pitch class (GenericPitchClass)
        """
        if onehot.sum() != 1:
            raise ValueError(f"{onehot} is not a one-hot vector.")
        (fs,) = np.where(onehot == 1)
        return GenericPitchClass.from_fifths(fs[0] + fifth_low)

    # pitch interface

    def interval_from(self, other):
        if type(other) is GenericPitchClass:
            return GenericIntervalClass.from_fifths(self.value - other.value)
        else:
            raise TypeError(
                f"Cannot take interval between GenericPitchClass and {type(other)}."
            )

    def pc(self):
        return self

    def embed(self):
        return GenericPitch.from_fifths_and_octaves(
            self.fifths(), -((self.fifths() * 4) // 7)
        )

    # Generic interface

    def name(self):
        return self.pitch_class_from_fifths(self.fifths())

    def compare(self, other):
        """
        Comparison between two Generic pitch classes according to line-of-fifth.

        Returns 0 if the pitch classes are equal,
        1 if the first pitch class (``self``) is greater ("sharper"),
        and -1 if the second pitch class (``other``) is greater ("sharper").

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: a pitch class to compare to (GenericPitchClass)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, GenericPitchClass):
            return np.sign(self.fifths() - other.fifths())
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def steps(self):
        return self.value

    def octaves(self):
        return 0

    def internal_octaves(self):
        return 0

    def alteration(self):
        return (self.fifths() + 1) // 7

    def letter(self):
        return chr(ord("A") + (self.degree() + 2) % 7)

    def onehot(self, fifth_range, dtype=int):
        """
        Returns a one-hot encoding of the pitch class in fifths.
        The range of fifths is given by ``fifth_range`` as a tuple ``(lower, upper)``.

        :param fifth_range: the (inclusive) range of fifths (pair of integers)
        :param dtype: dtype of the resulting array
        :return: a one-hot vector (numpy array)
        """
        low, high = fifth_range
        f = self.fifths()
        if f < low or f > high:
            raise ValueError(
                f"The pitch class {self} is outside the given fifths range {fifth_range}."
            )
        out = np.zeros(high - low + 1, dtype=dtype)
        out[f - low] = 1
        return out


@Generic.link_interval_class_type()
class GenericIntervalClass(
    Generic, AbstractGenericInterval, Interval, Diatonic, Chromatic
):
    """
    Represents a Generic interval class, i.e. an interval without octave information.
    """

    def __init__(self, value):
        """
        Takes a string consisting of the form
        ``-?<quality><generic-size>``,
        e.g. ``"M6"``, ``"-m3"``, or ``"aa2"``,
        which stand for a major sixth, a minor third down (= major sixth up), and a double-augmented second,
        respectively. Possible qualities are d (diminished), m (minor), M (major), P (perfect), and a (augmented),
        where d and a can be repeated.

        :param value: a string or internal numeric representation of the interval class
        """
        if isinstance(value, str):
            sign, octaves, fifths = self.parse_interval(value)
            assert isinstance(sign, numbers.Integral)
            assert abs(sign) == 1
            assert octaves is None
            assert isinstance(fifths, numbers.Integral)
            fifths *= sign
        else:
            fifths = value
        assert isinstance(fifths, numbers.Integral)
        super().__init__(value=fifths, is_pitch=False, is_class=True)

    @staticmethod
    def from_fifths(fifths):
        """
        Create an interval class by directly providing its internal fifths.

        :param fifths: the line-of-fifths position of the interval class (integer)
        :return: the resulting interval class (GenericIntervalClass)
        """
        return GenericIntervalClass(fifths)

    @staticmethod
    def from_onehot(onehot, low):
        """
        Create a Generic interval class from a one-hot vector.

        Requires the lower bounds of the fifth range used by the one-hot vector.

        :param onehot: a one-hot vector representing the interval (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot vector
        :return: the resulting interval class (GenericIntervalClass)
        """
        if onehot.sum() != 1:
            raise ValueError(f"{onehot} is not a one-hot vector.")
        (fs,) = np.where(onehot == 1)
        return GenericIntervalClass.from_fifths(fs[0] + low)

    # interval interface

    @classmethod
    def unison(cls):
        """
        Return a perfect unison.

        :return: P1
        """
        return cls.from_fifths(0)

    @classmethod
    def octave(cls):
        """
        Return a perfect unison, which is the same as an octave for interval classes.

        :return: P1
        """
        return cls.from_fifths(0)

    @classmethod
    def chromatic_semitone(cls):
        """
        Return a chromatic semitone

        :return: a1
        """
        return GenericIntervalClass.from_fifths(7)

    def direction(self):
        """
        Returns the direction of smallest realization of the interval class
        (1 = up, 0 = neutral, -1 = down).
        For example, the direction of ``M7`` (= ``m2``) is down.

        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        ds = self.degree()
        if ds == 0:
            alt = (self.fifths() + 1) // 7
            if alt == 0:
                return 0
            elif alt < 0:
                return -1
            else:
                return 1
        elif ds > 3:
            return -1
        else:
            return 1

    def __abs__(self):
        if self.direction() < 0:
            return -self
        else:
            return self

    def ic(self):
        return self

    def embed(self):
        return GenericInterval.from_fifths_and_octaves(
            self.fifths(), -((self.fifths() * 4) // 7)
        )

    def is_step(self):
        return self.degree() in [0, 1, 6]

    # Generic interface

    def name(self, inverse=False):
        if inverse:
            sign = "-"
        else:
            sign = ""
        return sign + self.interval_class_from_fifths(self.fifths(), inverse=inverse)

    def compare(self, other):
        """
        Comparison between two Generic interval classes according to line-of-fifth.

        Returns 0 if the interval classes are equal,
        1 if the first interval class (``self``) is greater ("sharper"),
        and -1 if the second interval class (``other``) is greater ("sharper").

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: an interval class to compare to (GenericIntervalClass)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, GenericIntervalClass):
            return np.sign(self.fifths() - other.fifths())
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def steps(self):
        return self.value

    def octaves(self):
        return 0

    def internal_octaves(self):
        return 0

    def generic(self):
        return self.degree()

    def diatonic_steps(self):
        return self.degree()

    def alteration(self):
        return (self.fifths() + 1) // 7

    def onehot(self, fifth_range, dtype=int):
        """
        Returns a one-hot encoding of the interval class in fifths.
        The range of fifths is given by ``fifth_range`` as a tuple ``(lower, upper)``.

        :param fifth_range: the (inclusive) range of fifths (pair of integers)
        :param dtype: dtype of the resulting array
        :return: a one-hot vector (numpy array)
        """
        low, high = fifth_range
        f = self.fifths()
        if f < low or f > high:
            raise ValueError(
                f"The pitch class {self} is outside the given fifths range {fifth_range}."
            )
        out = np.zeros(high - low + 1, dtype=dtype)
        out[f - low] = 1
        return out
