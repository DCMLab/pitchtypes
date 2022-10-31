#  Copyright (c) 2022 Christoph Finkensiep

import abc
import numbers
import numpy as np

from pitchtypes.basetypes import Pitch, Interval, Diatonic, Chromatic
from pitchtypes.spelled import Spelled, SpelledInterval, SpelledIntervalClass, SpelledPitch, SpelledPitchClass

# TODO: indexing into arrays
# TODO: element-wise comparison
# TODO: to/from list
# TODO: docs

class SpelledArray(abc.ABC):
    """
    A common base class for vectorized spelled pitch and interval types.
    Uses the same interface as the Spelled types.
    """

    # some common methods:
    
    def __repr__(self):
        # For vectorized types, name() returns an array of names,
        # so we convert it to a string here:
        with np.printoptions(formatter={'all': lambda x: str(x)}):
            return str(self.name())

    # spelled interface

    @abc.abstractmethod
    def name(self):
        raise NotImplementedError

    @abc.abstractmethod
    def fifths(self):
        """
        Return the position of the interval on the line of fifths.
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def octaves(self):
        """
        For intervals, return the number of octaves the interval spans.
        Negative intervals start with -1, decreasing.
        For pitches, return the absolute octave of the pitch.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def internal_octaves(self):
        """
        Return the internal octave representation of a pitch,
        which is dependent on the fifths.

        Only use this if you know what you are doing.
        """
        raise NotImplementedError

    def degree(self):
        """
        Return the "relative scale degree" (0-6) to which the interval points
        (unison=0, 2nd=1, octave=0, 2nd down=6, etc.).
        For pitches, return the integer that corresponds to the letter (C=0, D=1, ...).
        """
        return (self.fifths() * 4) % 7

    @abc.abstractmethod
    def generic(self):
        """
        Return the generic interval, i.e. the number of diatonic steps modulo octave.
        Unlike degree(), the result respects the sign of the interval
        (unison=0, 2nd up=1, 2nd down=-1).
        For pitches, use degree().
        """
        raise NotImplementedError

    @abc.abstractmethod
    def diatonic_steps(self):
        """
        Return the diatonic steps of the interval (unison=0, 2nd=1, ..., octave=7, ...).
        Respects both direction and octaves.
        For pitches, use degree()
        """
        raise NotImplementedError

    @abc.abstractmethod
    def alteration(self):
        """
        Return the number of semitones by which the interval is altered from its the perfect or major variant.
        Positive alteration always indicates augmentation,
        negative alteration indicates diminution (minor or smaller) of the interval.
        For pitches, return the accidentals (positive=sharps, negative=flats, 0=natural).
        """
        raise NotImplementedError


class SpelledIntervalArray(SpelledArray, Interval, Diatonic, Chromatic):
    """
    Represents an array of spelled intervals.

    The constructor takes two arrays,
    one for fifths and one for internal/dependent octaves.
    """
    def __init__(self, fifths, octaves):
        self._fifths = fifths
        self._octaves = octaves

    @staticmethod
    def from_fifths_and_independent_octaves(fifths, octaves):
        """
        Create an interval array from fifths (pitch class) and independent/external octaves.
        """
        return SpelledIntervalArray(fifths, octaves - (fifths * 4) // 7)

    @staticmethod
    def from_strings(strings):
        """
        Create an interval array from an array of strings (using spelled interval notation).
        """
        def parse_interval(string):
            sign, octave, fifth = Spelled.parse_interval(string)
            if octave is None:
                raise ValueError(f"Missing octave specifier in interval '{string}'.")
            return sign, octave, fifth
        sign, octaves, fifths = np.vectorize(parse_interval, otypes=[np.int_, np.int_, np.int_])(strings)
        return SpelledIntervalArray(fifths * sign, (octaves - (fifths * 4) // 7) * sign)

    # interval interface

    @classmethod
    def unison(cls, shape):
        """
        Return an array of the given shape filled with perfect unisons (P1:0).
        """
        return cls(np.full(shape, 0, dtype=np.int_),np.full(shape, 0, dtype=np.int_))

    @classmethod
    def octave(cls, shape):
        """
        Return an array of the given shape filled with perfect octaves (P1:1).
        """
        return cls(np.full(shape, 0, dtype=np.int_),np.full(shape, 1, dtype=np.int_))

    def __eq__(self, other):
        if type(other) == SpelledInterval or type(other) == SpelledIntervalArray:
            return (self.fifths() == other.fifths()).all() and \
                (self.internal_octaves() == other.internal_octaves()).all()
        else:
            return False

    def __add__(self, other):
        if type(other) == SpelledInterval or type(other) == SpelledIntervalArray:
            return SpelledIntervalArray(self.fifths() + other.fifths(),
                                        self.internal_octaves() + other.internal_octaves())
        else:
            return NotImplemented

    def __sub__(self, other):
        if type(other) == SpelledInterval or type(other) == SpelledIntervalArray:
            return SpelledIntervalArray(self.fifths() - other.fifths(),
                                        self.internal_octaves() - other.internal_octaves())
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, numbers.Integral) or\
           (hasattr(other, 'dtype') and issubclass(other.dtype.type, numbers.Integral)):
            return SpelledIntervalArray(self.fifths() * other, self.internal_octaves() * other)
        else:
            return NotImplemented
    
    def __neg__(self):
        return SpelledIntervalArray(-self.fifths(), -self.internal_octaves())

    def __abs__(self):
        downs = self.direction() < 0
        abs_fifths = self.fifths().copy()
        abs_octs = self.internal_octaves().copy()
        # manually invert the intervals that point downwards
        abs_fifths[downs] = -abs_fifths[downs]
        abs_octs[downs] = -abs_octs[downs]
        return SpelledIntervalArray(abs_fifths, abs_octs)

    
    def direction(self):
        """
        Return the direction of the interval (1=up / 0=neutral / -1=down).
        All unisons are considered neutral (including augmented and diminished unisons).
        """
        return np.sign(self.diatonic_steps())

    def ic(self):
        return SpelledIntervalClassArray(self.fifths())

    def embed(self):
        return self
    
    @classmethod
    def chromatic_semitone(cls, shape):
        """
        Returns an array of the given size filled with chromatic semitones (a1:0).
        """
        return SpelledIntervalArray(np.full(shape, 7, dtype=np.int_), np.full(shape, -4, dtype=np.int_))

    def is_step(self):
        return abs(self.diatonic_steps()) <= 1

    # spelled interface

    def name(self):
        def interval_name(fifths, octaves, direction):
            if direction == -1:
                return "-" + Spelled.interval_class_from_fifths(-fifths) + ":" + str(octaves)
            else:
                return Spelled.interval_class_from_fifths(fifths) + ":" + str(octaves)
        return np.vectorize(interval_name, otypes=[np.str_])(self.fifths(), abs(self).octaves(), self.direction())

    def fifths(self):
        return self._fifths

    def octaves(self):
        return self.internal_octaves() + (self.fifths() * 4) // 7

    def internal_octaves(self):
        return self._octaves

    def generic(self):
        downs = self.direction() < 0
        degrees = self.degree()
        degrees[downs] = -((-degrees[downs]) % 7)
        return degrees

    def diatonic_steps(self):
        return (self.fifths() * 4) + (self.internal_octaves() * 7)

    def alteration(self):
        return (abs(self).fifths() + 1) // 7

class SpelledIntervalClassArray(SpelledArray, Interval, Diatonic, Chromatic):
    """
    Represents a spelled interval class, i.e. an interval without octave information.

    The constructor takes a string consisting of the form
    -?<quality><generic-size>,
    e.g. "M6", "-m3", or "aa2",
    which stand for a major sixth, a minor third down (= major sixth up), and a double-augmented second, respectively.
    possible qualities are d (diminished), m (minor), M (major), P (perfect), and a (augmented),
    where d and a can be repeated.
    """
    def __init__(self, fifths):
        self._fifths = fifths

    @staticmethod
    def from_strings(strings):
        """
        Create an interval-class array from an array of strings.
        """
        def parse_ic(string):
            sign, octave, fifth = Spelled.parse_interval(string)
            if octave is not None:
                raise ValueError(f"Interval classes cannot have octave specifiers ({string}).")
            return sign, fifth
        sign, fifths = np.vectorize(parse_ic, otypes=[np.int_, np.int_])(strings)
        return SpelledIntervalClassArray(fifths * sign)

    def name(self):
        def intervalclass_name(fifths):
            return Spelled.interval_class_from_fifths(fifths)
        return np.vectorize(intervalclass_name, otypes=[np.str_])(self.fifths())

    # interval interface

    @classmethod
    def unison(cls, shape):
        """
        Return an array of the given shape filled with perfect unisons (P1).
        """
        return cls(np.full(shape, 0, dtype=np.int_))

    @classmethod
    def octave(cls, shape):
        """
        Same as unison() since octaves are equivalent to unisons in interval class space.
        """
        return cls.unison(shape)

    def __eq__(self, other):
        if type(other) == SpelledIntervalClass or type(other) == SpelledIntervalClassArray:
            return (self.fifths() == other.fifths()).all()
        else:
            return False

    def __add__(self, other):
        if type(other) == SpelledIntervalClass or type(other) == SpelledIntervalClassArray:
            return SpelledIntervalClassArray(self.fifths() + other.fifths())
        else:
            return NotImplemented

    def __sub__(self, other):
        if type(other) == SpelledIntervalClass or type(other) == SpelledIntervalClassArray:
            return SpelledIntervalClassArray(self.fifths() - other.fifths())
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, numbers.Integral) or\
           (hasattr(other, 'dtype') and issubclass(other.dtype.type, numbers.Integral)):
            return SpelledIntervalClassArray(self.fifths() * other)
        return NotImplemented
    
    def __neg__(self):
        return SpelledIntervalClassArray(-self.fifths())

    def __abs__(self):
        downs = self.direction() < 0
        abs_fifths = self.fifths().copy()
        # manually invert the intervals that point downwards
        abs_fifths[downs] = -abs_fifths[downs]
        return SpelledIntervalClassArray(abs_fifths)
    
    def direction(self):
        ds = self.diatonic_steps()
        out = np.ones_like(ds, dtype=np.int_)
        out[ds == 0] = 0
        out[ds > 3] = -1
        return out

    def ic(self):
        return self

    def embed(self):
        return SpelledIntervalArray.from_fifths_and_independent_octaves(self.fifths(), np.zeros_like(self.fifths()))

    @classmethod
    def chromatic_semitone(cls, shape):
        return cls(np.full(shape, 7, dtype=np.int_))

    def is_step(self):
        return np.isin(self.degree(), [0,1,6])

    # spelled interface

    def fifths(self):
        return self._fifths

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

class SpelledPitchArray(SpelledArray, Pitch):
    """
    Represents a vector spelled pitch.

    The constructor takes two numpy arrays,
    one for fifths and one for (internal/dependent) octaves,
    both as integers.
    """

    # constructors
    
    def __init__(self, fifths, octaves):
        # assert fifths.dtype == np.int_
        # assert octaves.dtype == np.int_
        self._fifths = fifths
        self._octaves = octaves

    @staticmethod
    def from_fifths_and_independent_octaves(fifths, octaves):
        """
        Create a pitch array from fifths and indenpendent octaves.
        The fifths indicate the names of the pitches
        while the octaves indicate their octave numbers.
        """
        return SpelledPitchArray(fifths, octaves - (fifths * 4) // 7)

    @staticmethod
    def from_strings(strings):
        """
        Create a pitch array from an array of strings.
        """
        # assert isinstance(strings.dtype, np.str_)
        def parse_pitch(string):
            octave, fifth = Spelled.parse_pitch(string)
            if octave is None:
                raise ValueError(f"Missing octave specifier in pitch '{string}'.")
            return octave, fifth
        octaves, fifths = np.vectorize(parse_pitch, otypes=[np.int_, np.int_])(strings)
        return SpelledPitchArray.from_fifths_and_independent_octaves(fifths, octaves)

    # Pitch interface

    def __eq__(self, other):
        if type(other) == SpelledPitch or type(other) == SpelledPitchArray:
            return (self.fifths() == other.fifths()).all() and \
                (self.internal_octaves() == other.internal_octaves()).all()
        else:
            return False

    def __add__(self, other):
        if type(other) == SpelledInterval or type(other) == SpelledIntervalArray:
            return SpelledPitchArray(self.fifths() + other.fifths(),
                                     self.internal_octaves() + other.internal_octaves())
        return NotImplemented

    def interval_from(self, other):
        if type(other) == SpelledPitch or type(other) == SpelledPitchArray:
            return SpelledIntervalArray(self.fifths() - other.fifths(),
                                     self.internal_octaves() - other.internal_octaves())
        else:
            raise TypeError(f"Cannot take interval between SpelledPitchArray and {type(other)}.")

    def pc(self):
        return SpelledPitchClassArray(self.fifths())

    def embed(self):
        return self

    # Spelled interface

    def name(self):
        def pitch_name(fifths, octave):
            return f"{Spelled.pitch_class_from_fifths(fifths)}{octave}"
        return np.vectorize(pitch_name, otypes=[np.str_])(self.fifths(), self.octaves())

    def fifths(self):
        return self._fifths

    def octaves(self):
        return self.internal_octaves() + (self.fifths() * 4) // 7

    def internal_octaves(self):
        return self._octaves

    def generic(self):
        # return self.degree()
        raise NotImplementedError

    def diatonic_steps(self):
        # return self.degree()
        raise NotImplementedError

    def alteration(self):
        return (self.fifths() + 1) // 7

    def letter(self):
        return ((self.degree() + 2) % 7 + ord('A')).astype(np.uint8).view('c').astype(np.str_)

class SpelledPitchClassArray(SpelledArray, Pitch):
    """
    Represents a spelled pitch class, i.e. a pitch without octave information.

    The constructure takes an array of fifths.
    """
    def __init__(self, fifths):
        self._fifths = fifths

    @staticmethod
    def from_strings(strings):
        """
        Create a pitch-class array from an array of strings.
        """
        def parse_pc(string):
            octave, fifth = Spelled.parse_pitch(string)
            if octave is not None:
                raise ValueError(f"Pitch classes cannot have octave specifiers ({string}).")
            return fifth
        fifths = np.vectorize(parse_pc, otypes=[np.int_])(strings)
        return SpelledPitchClassArray(fifths)

    def name(self):
        def pitchclass_name(fifths):
            return Spelled.pitch_class_from_fifths(fifths)
        return np.vectorize(pitchclass_name, otypes=[np.str_])(self.fifths())

    # pitch interface

    def __eq__(self, other):
        if type(other) == SpelledPitchClass or type(other) == SpelledPitchClassArray:
            return (self.fifths() == other.fifths()).all()
        else:
            return False

    def __add__(self, other):
        if type(other) == SpelledIntervalClass or type(other) == SpelledIntervalClassArray:
            return SpelledPitchClassArray(self.fifths() + other.fifths())
        else:
            return NotImplemented

    def interval_from(self, other):
        if type(other) == SpelledPitchClass or type(other) == SpelledPitchClassArray:
            return SpelledIntervalClassArray(self.fifths() - other.fifths())
        else:
            raise TypeError(f"Cannot take interval between SpelledPitchClassArray and {type(other)}.")

    def pc(self):
        return self

    def embed(self):
        return SpelledPitchArray.from_fifths_and_independent_octaves(self.fifths(), np.zeros_like(self.fifths()))

    # spelled interface

    def fifths(self):
        return self._fifths

    def octaves(self):
        return 0

    def internal_octaves(self):
        return 0

    def generic(self):
        # return self.degree()
        raise NotImplementedError

    def diatonic_steps(self):
        # return self.degree()
        raise NotImplementedError

    def alteration(self):
        return (self.fifths() + 1) // 7

    def letter(self):
        return ((self.degree() + 2) % 7 + ord('A')).astype(np.uint8).view('c').astype(np.str_)

# shorthand constructors

def aspelled(things, things2=None):
    """
    A quick way to construct a spelled-interval array.
    Takes either an array-like of strings or two array-likes of integers
    (fifths and internal/dependent octaves).
    """
    input = np.array(things)
    if input.dtype.type is np.str_ or input.dtype.type is np.string_:
        return SpelledIntervalArray.from_strings(input)
    else:
        return SpelledIntervalArray(input, np.array(things2))

def asic(things):
    """
    A quick way to construct a spelled-interval-class array.
    Takes either an array-like of strings or an array-like of integers (fifths).
    """
    input = np.array(things)
    if input.dtype.type is np.str_ or input.dtype.type is np.string_:
        return SpelledIntervalClassArray.from_strings(input)
    else:
        return SpelledIntervalClassArray(input)

def aspelledp(things, things2=None):
    """
    A quick way to construct a spelled-pitch array.
    Takes either an array-like of strings or two array-likes of integers
    (fifths and internal/dependent octaves).
    """
    input = np.array(things)
    if input.dtype.type is np.str_ or input.dtype.type is np.string_:
        return SpelledPitchArray.from_strings(input)
    else:
        return SpelledPitchArray(input, np.array(things2))

def aspc(things):
    """
    A quick way to construct a spelled-pitch-class array.
    Takes either an array-like of strings or an array-like of integers (fifths).
    """
    input = np.array(things)
    if input.dtype.type is np.str_ or input.dtype.type is np.string_:
        return SpelledPitchClassArray.from_strings(input)
    else:
        return SpelledPitchClassArray(input)