#  Copyright (c) 2022 Christoph Finkensiep

import abc
import numbers
import numpy as np
import copy

from pitchtypes.basetypes import Pitch, Interval, Diatonic, Chromatic
from pitchtypes.spelled import Spelled, SpelledInterval, SpelledIntervalClass, SpelledPitch, SpelledPitchClass

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
        return f"{self._print_name}({np.array2string(self.name(), separator=', ')})"

    def __str__(self):
        # with np.printoptions(formatter={'all': lambda x: str(x)}):
        #     return f"{self._print_name}{self.name()}"
        return np.array2string(self.name(), formatter={'all': lambda x: str(x)})

    # mandatory array methods

    @abc.abstractmethod
    def __copy__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __deepcopy__(self, memo):
        raise NotImplementedError

    def copy(self):
        """
        Returns a shallow copy of the array.
        This also creates copies of the underlying numpy arrays.
        """
        return copy.copy(self)

    def deepcopy(self):
        """
        Returns a deep copy of the array.
        """
        return copy.deepcopy(self)

    @abc.abstractmethod
    def __getitem__(self, index):
        """
        Returns an item or a subarray of the spelled array.
        Supports advanced indexing as on numpy arrays.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, index, item):
        """
        Sets the given indices to the given item(s).
        Supports advanced indexing as on numpy arrays.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __contains__(self, item):
        """
        Returns true if the array contains the given interval/pitch.
        """
        raise NotImplementedError
    
    # spelled interface

    @abc.abstractmethod
    def name(self):
        """
        Returns the names of the objects in the array
        as an array of strings of the same shape.
        """
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
    """

    _print_name = "asi"
    
    def __init__(self, fifths, octaves):
        """        
        Takes two numpy arrays,
        one for fifths and one for internal/dependent octaves,
        both as integers.
        """
        if fifths.shape != octaves.shape:
            raise ValueError(f"Cannot create SpelledIntervalArray from arrays of different sizes ({fifths.shape} and {octaves.shape}).")
        self._fifths = fifths
        self._octaves = octaves

    @staticmethod
    def from_independent(fifths, octaves):
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

    # collection interface

    def __copy__(self):
        return SpelledIntervalArray(copy.copy(self.fifths()), copy.copy(self.internal_octaves()))

    def __deepcopy__(self, memo):
        return SpelledIntervalArray(copy.deepcopy(self.fifths(), memo), copy.deepcopy(self.internal_octaves(), memo))
    
    def __getitem__(self, index):
        f = self._fifths[index]
        o = self._octaves[index]
        if isinstance(f, numbers.Integral):
            return SpelledInterval.from_fifths_and_octaves(f, o)
        else:
            return SpelledIntervalArray(f, o)

    def __setitem__(self, index, item):
        if isinstance(item, SpelledInterval) or isinstance(item, SpelledIntervalArray):
            self._fifths[index] = item.fifths()
            self._octaves[index] = item.internal_octaves()
        else:
            raise TypeError(f"Cannot set elements of SpelledIntervalArray to {type(item)}.")

    def __contains__(self, item):
        if isinstance(item, SpelledInterval):
            return ((self.fifths() == item.fifths()) &
                    (self.internal_octaves() == item.internal_octaves())).any()
        else:
            return False
    
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

    @classmethod
    def chromatic_semitone(cls, shape):
        """
        Returns an array of the given size filled with chromatic semitones (a1:0).
        """
        return SpelledIntervalArray(np.full(shape, 7, dtype=np.int_), np.full(shape, -4, dtype=np.int_))

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
    """

    _print_name = "asic"
    
    def __init__(self, fifths):
        """
        Takes a numpy array of fifths as integers.
        """
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

    # collection interface

    def __copy__(self):
        return SpelledIntervalClassArray(copy.copy(self.fifths()))

    def __deepcopy__(self, memo):
        return SpelledIntervalClassArray(copy.deepcopy(self.fifths(), memo))
    
    def __getitem__(self, index):
        f = self._fifths[index]
        if isinstance(f, numbers.Integral):
            return SpelledIntervalClass.from_fifths(f)
        else:
            return SpelledIntervalClassArray(f)

    def __setitem__(self, index, item):
        if isinstance(item, SpelledIntervalClass) or isinstance(item, SpelledIntervalClassArray):
            self._fifths[index] = item.fifths()
        else:
            raise TypeError(f"Cannot set elements of SpelledIntervalClassArray to {type(item)}.")

    def __contains__(self, item):
        if isinstance(item, SpelledIntervalClass):
            return item.fifths() in self.fifths()
        else:
            return False
        
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

    @classmethod
    def chromatic_semitone(cls, shape):
        return cls(np.full(shape, 7, dtype=np.int_))

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
        return SpelledIntervalArray.from_independent(self.fifths(), np.zeros_like(self.fifths()))

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
    """

    _print_name = "asp"

    # constructors
    
    def __init__(self, fifths, octaves):
        """
        Takes two numpy arrays,
        one for fifths and one for (internal/dependent) octaves,
        both as integers.
        """
        # assert fifths.dtype == np.int_
        # assert octaves.dtype == np.int_
        if fifths.shape != octaves.shape:
            raise ValueError(f"Cannot create SpelledPitchArray from arrays of different sizes ({fifths.shape} and {octaves.shape}).")
        self._fifths = fifths
        self._octaves = octaves

    @staticmethod
    def from_independent(fifths, octaves):
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
        return SpelledPitchArray.from_independent(fifths, octaves)

    # collection interface

    def __copy__(self):
        return SpelledPitchArray(copy.copy(self.fifths()), copy.copy(self.internal_octaves()))

    def __deepcopy__(self, memo):
        return SpelledPitchArray(copy.deepcopy(self.fifths(), memo), copy.deepcopy(self.internal_octaves(), memo))
    
    def __getitem__(self, index):
        f = self._fifths[index]
        o = self._octaves[index]
        if isinstance(f, numbers.Integral):
            return SpelledPitch.from_fifths_and_octaves(f, o)
        else:
            return SpelledPitchArray(f, o)

    def __setitem__(self, index, item):
        if isinstance(item, SpelledPitch) or isinstance(item, SpelledPitchArray):
            self._fifths[index] = item.fifths()
            self._octaves[index] = item.internal_octaves()
        else:
            raise TypeError(f"Cannot set elements of SpelledPitchArray to {type(item)}.")

    def __contains__(self, item):
        if isinstance(item, SpelledPitch):
            return ((self.fifths() == item.fifths()) &
                    (self.internal_octaves() == item.internal_octaves())).any()
        else:
            return False
    
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
    """

    _print_name = "aspc"

    def __init__(self, fifths):
        """
        Takes a numpy array of fifths as integers.
        """
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

    # collection interface

    def __copy__(self):
        return SpelledPitchClassArray(copy.copy(self.fifths()))

    def __deepcopy__(self, memo):
        return SpelledPitchClassArray(copy.deepcopy(self.fifths(), memo))

    def __getitem__(self, index):
        f = self._fifths[index]
        if isinstance(f, numbers.Integral):
            return SpelledPitchClass.from_fifths(f)
        else:
            return SpelledPitchClassArray(f)

    def __setitem__(self, index, item):
        if isinstance(item, SpelledPitchClass) or isinstance(item, SpelledPitchClassArray):
            self._fifths[index] = item.fifths()
        else:
            raise TypeError(f"Cannot set elements of SpelledPitchClassArray to {type(item)}.")

    def __contains__(self, item):
        if isinstance(item, SpelledPitchClass):
            return item.fifths() in self.fifths()
        else:
            return False
    
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
        return SpelledPitchArray.from_independent(self.fifths(), np.zeros_like(self.fifths()))

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

def asi(things, things2=None):
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

def asp(things, things2=None):
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
