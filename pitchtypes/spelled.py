#  Copyright (c) 2022 Robert Lieck, Christoph Finkensiep

import numbers
import abc
import functools
from abc import ABC

import numpy as np
from pitchtypes.utils import diatonic_steps_from_fifths
from pitchtypes.basetypes import AbstractBase, Pitch, Interval, Diatonic, Chromatic


@functools.total_ordering
class Spelled(AbstractBase):
    """
    A common base class for spelled pitch and interval types.
    See below for a set of common operations.
    """

    @staticmethod
    def pitch_class_from_fifths(fifth_steps):
        """
        Return the pitch class given the number of steps along the line of fifths

        :param fifth_steps: number of steps along the line of fifths
        :return: pitch class (e.g. C, Bb, F##, Abbb etc.)

        :meta private:
        """
        base_pitch = ["F", "C", "G", "D", "A", "E", "B"][(fifth_steps + 1) % 7]
        flat_sharp = (fifth_steps + 1) // 7
        return base_pitch + ('#' if flat_sharp > 0 else 'b') * abs(flat_sharp)

    @staticmethod
    def interval_quality_from_fifths(fifth_steps):
        """
        Return the interval quality (major, minor, perfect, augmented, diminished, doubly-augmented etc) given the
        number of steps along the line of fifths.

        :param fifth_steps: number of steps along the line of fifths
        :return: interval quality (M, m, p, a, d, aa, dd, aaa, ddd etc)

        :meta private:
        """
        if -5 <= fifth_steps <= 5:
            quality = ['m', 'm', 'm', 'm', 'P', 'P', 'P', 'M', 'M', 'M', 'M'][fifth_steps + 5]
        elif fifth_steps > 5:
            quality = 'a' * ((fifth_steps + 1) // 7)
        else:
            quality = 'd' * ((-fifth_steps + 1) // 7)
        return quality

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
    def interval_class_from_fifths(fifths, inverse=False):
        """
        Return the interval class corresponding to the given number of steps along the line of fifths. This function
        combines Spelled.interval_quality_from_fifths and Spelled.generic_interval_class_from_fifths. Specifying
        inverse=True (default is False) returns the inverse interval class (m2 for M7, aa4 for dd5 etc.).

        :param fifths: number of fifth steps
        :param inverse: whether to return the inverse interval class
        :return: interval class (p1, M3, aa6 etc.)

        :meta private:
        """
        if inverse:
            fifths = -fifths
        return f"{Spelled.interval_quality_from_fifths(fifths)}" \
               f"{Spelled.generic_interval_class_from_fifths(fifths)}"

    @staticmethod
    def _degree_from_fifths_(fifths):
        """
        Return the scale degree of a pitch/interval based on its fifths.
        Helper function for degree()

        :meta private:
        """
        return (fifths * 4) % 7

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
        Comparison between two spelled types.

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

    # Spelled interface:

    def fifths(self):
        """
        Return the position of the interval on the line of fifths.

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
        Return the internal octave representation of a pitch,
        which is dependent on the fifths.

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
        return self._degree_from_fifths_(self.fifths())

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


class AbstractSpelledInterval(abc.ABC):
    """
    The interface for spelled interval types.
    """

    @abc.abstractmethod
    def name(self):
        pass

    @abc.abstractmethod
    def compare(self, other):
        pass

    @abc.abstractmethod
    def fifths(self):
        pass

    @abc.abstractmethod
    def octaves(self):
        pass

    @abc.abstractmethod
    def internal_octaves(self):
        pass

    @abc.abstractmethod
    def alteration(self):
        pass

    @abc.abstractmethod
    def onehot(self, fifth_range, octave_range, dtype=int):
        pass

    @abc.abstractmethod
    def embed(self):
        pass

    @abc.abstractmethod
    def generic(self):
        """
        Return the generic interval, i.e. the number of diatonic steps modulo octave.
        Unlike degree(), the result respects the sign of the interval
        (unison=0, 2nd up=1, 2nd down=-1).

        :return: generic interval (integer)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def diatonic_steps(self):
        """
        Return the diatonic steps of the interval (unison=0, 2nd=1, ..., octave=7, ...).
        Respects both direction and octaves.

        :return: number of diatonic steps (integer)
        """
        raise NotImplementedError


class AbstractSpelledPitch(abc.ABC):
    """
    The interface for spelled pitch types.
    """

    @abc.abstractmethod
    def name(self):
        pass

    @abc.abstractmethod
    def compare(self, other):
        pass

    @abc.abstractmethod
    def fifths(self):
        pass

    @abc.abstractmethod
    def octaves(self):
        pass

    @abc.abstractmethod
    def internal_octaves(self):
        pass

    @abc.abstractmethod
    def alteration(self):
        pass

    @abc.abstractmethod
    def onehot(self, fifth_range, octave_range, dtype=int):
        pass

    @abc.abstractmethod
    def embed(self):
        pass

    @abc.abstractmethod
    def letter(self):
        """
        Returns the letter associated with the pitch (without accidentals).

        :return: letter (single-character string)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def midi(self):
        """
        Return the MIDI number of the pitch.

        :return: MIDI number (integer)
        """
        raise NotImplementedError


@Spelled.link_pitch_type()
class SpelledPitch(Spelled, AbstractSpelledPitch, Pitch):
    """
    Represents a spelled pitch.
    """

    def midi(self):
        """
        Return the MIDI value, in the interval [0,127].

        :return: MIDI value (integer)
        """
        return 12 * (self.octaves() + 1) + (self.fifths() * 7) % 12

    def __init__(self, value):
        """
        Takes a string consisting of the form
        ``<letter><accidentals?><octave>``, e.g. ``"C#4"``, ``"E5"``, or ``"Db-2"``.
        Accidentals may be written as ASCII symbols (#/b)
        or with unicode symbols (♯/♭), but not mixed within the same note.

        :param value: a string or internal numeric representation of the pitch
        """
        if isinstance(value, str):
            octaves, fifths = self.parse_pitch(value)
            assert isinstance(octaves, numbers.Integral)
            assert isinstance(fifths, numbers.Integral)
            # correct for octaves taken by fifth steps
            octaves -= diatonic_steps_from_fifths(fifths) // 7
            value = np.array([octaves, fifths])
        else:
            octaves, fifths = value
            assert isinstance(octaves, numbers.Integral)
            assert isinstance(fifths, numbers.Integral)
            value = np.array([octaves, fifths])
        assert isinstance(fifths, numbers.Integral)
        assert isinstance(octaves, numbers.Integral)
        super().__init__(value=value, is_pitch=True, is_class=False)

    @staticmethod
    def from_fifths_and_octaves(fifths, octaves):
        """
        Create a pitch by directly providing its internal fifths and octaves.

        Each pitch is represented relative to C0
        by moving the specified number of fifths and octaves upwards
        (or downwards for negative values).

        :param fifths: the fifth (= pitch class) of the pitch (integer)
        :param octaves: the internal/dependent octave of the pitch (integer)
        :return: the resulting pitch (SpelledPitch)
        """
        return SpelledPitch((octaves, fifths))

    @staticmethod
    def from_independent(fifths, octaves):
        """
        Create a pitch from fifths (pitch class) and independent/external octaves (octave number).

        :param fifths: the fifth (= pitch class) of the pitch (integer)
        :param octaves: the external/independent octave of the pitch (integer)
        :return: the resulting pitch (SpelledPitch)
        """
        return SpelledPitch.from_fifths_and_octaves(fifths, octaves - (fifths * 4) // 7)

    @staticmethod
    def from_onehot(onehot, fifth_low, octave_low):
        """
        Create a spelled pitch from a one-hot matrix.

        Requires the lower bounds of the fifth and octave range used by the one-hot matrix.

        :param onehot: a one-hot matrix representing the pitch (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot matrix
        :param octave_low: the lowest octave expressible in the one-hot matrix
        :return: the resulting pitch (SpelledPitch)
        """
        if onehot.sum() != 1:
            raise ValueError(f"{onehot} is not a one-hot vector.")
        fs, os = np.where(onehot == 1)
        return SpelledPitch.from_independent(fs[0] + fifth_low, os[0] + octave_low)

    # Pitch interface

    def interval_from(self, other):
        if isinstance(other, SpelledPitch):
            octaves1, fifths1 = self.value
            octaves2, fifths2 = other.value
            return SpelledInterval.from_fifths_and_octaves(fifths1 - fifths2, octaves1 - octaves2)
        else:
            raise TypeError(f"Cannot take interval between SpelledPitch and {type(other)}.")

    def to_class(self):
        return self.PitchClass(self.fifths())

    def pc(self):
        return self.to_class()

    def embed(self):
        return self

    # Spelled interface

    def name(self):
        return f"{self.pitch_class_from_fifths(self.fifths())}{self.octaves()}"

    def compare(self, other):
        """
        Comparison between two spelled pitches according to diatonic ordering.

        Returns 0 if the objects are equal,
        1 if the first pitch (``self``) is higher,
        and -1 if the second pitch (``other``) is higher.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: a pitch to compare to (SpelledPitch)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, SpelledPitch):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def fifths(self):
        return self.value[1]

    def octaves(self):
        return self.value[0] + diatonic_steps_from_fifths(self.fifths()) // 7

    def internal_octaves(self):
        return self.value[0]

    def alteration(self):
        return (self.fifths() + 1) // 7

    def letter(self):
        return chr(ord('A') + (self.degree() + 2) % 7)

    def onehot(self, fifth_range, octave_range, dtype=int):
        """
        Returns a one-hot encoding of the pitch in fifths (first dimension) and external octaves (second dimension).
        The range of fifths and octaves is given by ``fifth_range`` and ``octave_range`` respectively,
        where each is a pair ``(lower, upper)``.

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
            raise ValueError(f"The pitch {self} is outside the given fifth range {fifth_range}.")
        if o < olow or o > ohigh:
            raise ValueError(f"The pitch {self} is outside the given octave range {octave_range}.")
        out = np.zeros((fhigh - flow + 1, ohigh - olow + 1), dtype=dtype)
        out[f - flow, o - olow] = 1
        return out


@Spelled.link_interval_type()
class SpelledInterval(Spelled, AbstractSpelledInterval, Interval, Diatonic, Chromatic):
    """
    Represents a spelled interval.
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
            octaves -= diatonic_steps_from_fifths(fifths) // 7
            value = np.array([octaves, fifths])
            # negate value for negative intervals
            if sign < 0:
                value *= -1
        elif isinstance(value, int):
            octaves = 0
            fifths = value
            value = np.array([octaves, fifths])
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
        :return: the resulting interval (SpelledInterval)
        """
        return SpelledInterval((octaves, fifths))

    @staticmethod
    def from_independent(fifths, octaves):
        """
        Create an interval from fifths (interval class) and independent/external octaves.

        :param fifths: the fifth (= interval class) of the interval (integer)
        :param octaves: the external/independent octaves the interval spans (integer)
        :return: the resulting interval (SpelledInterval)
        """
        return SpelledInterval.from_fifths_and_octaves(fifths, octaves - (fifths * 4) // 7)

    @staticmethod
    def from_onehot(onehot, fifth_low, octave_low):
        """
        Create a spelled interval from a one-hot matrix.

        Requires the lower bounds of the fifth and octave range used by the one-hot matrix.

        :param onehot: a one-hot matrix representing the interval (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot matrix
        :param octave_low: the lowest octave expressible in the one-hot matrix
        :return: the resulting interval (SpelledInterval)
        """
        if onehot.sum() != 1:
            raise ValueError(f"{onehot} is not a one-hot vector.")
        fs, os = np.where(onehot == 1)
        return SpelledInterval.from_independent(fs[0] + fifth_low, os[0] + octave_low)

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
        return SpelledInterval.from_fifths_and_octaves(7, -4)

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

    # spelled interface

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
        return sign + self.interval_class_from_fifths(self.fifths(), inverse=inverse) + f":{octave}"

    def compare(self, other):
        """
        Comparison between two spelled intervals according to diatonic ordering.

        Returns 0 if the intervals are equal,
        1 if the first interval (``self``) is greater,
        and -1 if the second interval (``other``) is greater.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: an interval to compare to (SpelledInterval)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, SpelledInterval):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def fifths(self):
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
        Returns a one-hot encoding of the interval in fifths (first dimension) and independent octaves (second dimension).
        The range of fifths and octaves is given by ``fifth_range`` and ``octave_range`` respectively,
        where each is a tuple ``(lower, upper)``.

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
            raise ValueError(f"The interval {self} is outside the given fifth range {fifth_range}.")
        if o < olow or o > ohigh:
            raise ValueError(f"The interval {self} is outside the given octave range {octave_range}.")
        out = np.zeros((fhigh - flow + 1, ohigh - olow + 1), dtype=dtype)
        out[f - flow, o - olow] = 1
        return out


@Spelled.link_pitch_class_type()
class SpelledPitchClass(Spelled, AbstractSpelledPitch, Pitch):
    """
    Represents a spelled pitch class, i.e. a pitch without octave information.
    """

    def midi(self):
        """
        Return the MIDI number of the pitch class, in the interval [0,11].

        :return: MIDI number (integer)
        """
        return (self.fifths() * 7) % 12

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
        :return: the resulting pitch class (SpelledPitchClass)
        """
        return SpelledPitchClass(fifths)

    @staticmethod
    def from_onehot(onehot, fifth_low):
        """
        Create a spelled pitch class from a one-hot vector.

        Requires the lower bounds of the fifth range used by the one-hot vector.

        :param onehot: a one-hot vector representing the pitch (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot vector
        :return: the resulting pitch class (SpelledPitchClass)
        """
        if onehot.sum() != 1:
            raise ValueError(f"{onehot} is not a one-hot vector.")
        fs, = np.where(onehot == 1)
        return SpelledPitchClass.from_fifths(fs[0] + fifth_low)

    # pitch interface

    def interval_from(self, other):
        if type(other) is SpelledPitchClass:
            return SpelledIntervalClass.from_fifths(self.value - other.value)
        else:
            raise TypeError(f"Cannot take interval between SpelledPitchClass and {type(other)}.")

    def pc(self):
        return self

    def embed(self):
        return SpelledPitch.from_fifths_and_octaves(self.fifths(), -((self.fifths() * 4) // 7))

    # spelled interface

    def name(self):
        return self.pitch_class_from_fifths(self.fifths())

    def compare(self, other):
        """
        Comparison between two spelled pitch classes according to line-of-fifth.

        Returns 0 if the pitch classes are equal,
        1 if the first pitch class (``self``) is greater ("sharper"),
        and -1 if the second pitch class (``other``) is greater ("sharper").

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: a pitch class to compare to (SpelledPitchClass)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, SpelledPitchClass):
            return np.sign(self.fifths() - other.fifths())
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def fifths(self):
        return self.value

    def octaves(self):
        return 0

    def internal_octaves(self):
        return 0

    def alteration(self):
        return (self.fifths() + 1) // 7

    def letter(self):
        return chr(ord('A') + (self.degree() + 2) % 7)

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
            raise ValueError(f"The pitch class {self} is outside the given fifths range {fifth_range}.")
        out = np.zeros(high - low + 1, dtype=dtype)
        out[f - low] = 1
        return out


@Spelled.link_interval_class_type()
class SpelledIntervalClass(Spelled, AbstractSpelledInterval, Interval, Diatonic, Chromatic):
    """
    Represents a spelled interval class, i.e. an interval without octave information.
    """

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
        :return: the resulting interval class (SpelledIntervalClass)
        """
        return SpelledIntervalClass(fifths)

    @staticmethod
    def from_onehot(onehot, low):
        """
        Create a spelled interval class from a one-hot vector.

        Requires the lower bounds of the fifth range used by the one-hot vector.

        :param onehot: a one-hot vector representing the interval (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot vector
        :return: the resulting interval class (SpelledIntervalClass)
        """
        if onehot.sum() != 1:
            raise ValueError(f"{onehot} is not a one-hot vector.")
        fs, = np.where(onehot == 1)
        return SpelledIntervalClass.from_fifths(fs[0] + low)

    # interval interface

    @classmethod
    def unison(cls):
        """
        Return a perfect unison.

        :return: P1
        """
        return cls.from_fifths(0)

    @classmethod
    def octaves(cls):
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
        return SpelledIntervalClass.from_fifths(7)

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
        return SpelledInterval.from_fifths_and_octaves(self.fifths(), -((self.fifths() * 4) // 7))

    def is_step(self):
        return self.degree() in [0, 1, 6]

    # spelled interface

    def name(self, inverse=False):
        if inverse:
            sign = "-"
        else:
            sign = ""
        return sign + self.interval_class_from_fifths(self.fifths(), inverse=inverse)

    def compare(self, other):
        """
        Comparison between two spelled interval classes according to line-of-fifth.

        Returns 0 if the interval classes are equal,
        1 if the first interval class (``self``) is greater ("sharper"),
        and -1 if the second interval class (``other``) is greater ("sharper").

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).

        :param other: an interval class to compare to (SpelledIntervalClass)
        :return: ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, SpelledIntervalClass):
            return np.sign(self.fifths() - other.fifths())
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def fifths(self):
        return self.value

    def octave(self):
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
            raise ValueError(f"The pitch class {self} is outside the given fifths range {fifth_range}.")
        out = np.zeros(high - low + 1, dtype=dtype)
        out[f - low] = 1
        return out
