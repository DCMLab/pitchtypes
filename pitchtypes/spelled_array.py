#  Copyright (c) 2022 Christoph Finkensiep

import abc
import numbers
import numpy as np
import copy

from pitchtypes.basetypes import Pitch, Interval, Diatonic, Chromatic
from pitchtypes.spelled import Spelled, SpelledInterval, SpelledIntervalClass, SpelledPitch, SpelledPitchClass

class SpelledArray(abc.ABC):
    """
    A common base class for vectorized spelled pitch and interval types.
    Uses the same interface as the Spelled types.
    """

    # constructors

    @abc.abstractstaticmethod
    def from_onehot():
        raise NotImplementedError

    # printing

    _print_name = "SpelledArray"
    
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

        :return: a copy of the array
        """
        return copy.copy(self)

    def deepcopy(self):
        """
        Returns a deep copy of the array.

        :return: a deepcopy of the array
        """
        return copy.deepcopy(self)

    @abc.abstractmethod
    def __getitem__(self, index):
        """
        Returns an item or a subarray of the spelled array.
        Supports advanced indexing as on numpy arrays.

        :param index: a numpy-compatible index into the array
        :return: a new array or a scalar value (depending on the index)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, index, item):
        """
        Sets the given indices to the given item(s).
        Supports advanced indexing as on numpy arrays.

        :param index: a numpy-compatible index into the array
        :param item: an array or a scalar to assign to the indicated sub-array
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __contains__(self, item):
        """
        Returns true if the array contains the given interval/pitch.

        :param item: the potential item to test
        :return: ``True`` if the array contains ``item``, otherwise ``False``
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self):
        """
        Returns the length of the array (first dimension, as in numpy).

        :return: the length of the array (1st dimension, integer)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self):
        raise NotImplementedError

    def array_equal(self, other):
        """
        Returns True if self and other are the equal,
        False otherwise.

        :param other: another spelled array of the same type
        :return: ``True`` if the two arrays are equal, ``False`` otherwise
        """
        try:
            return (self.compare(other) == 0).all()
        except TypeError:
            return False

    # element-wise comparison
    
    @abc.abstractmethod
    def compare(self, other):
        """
        Element-wise comparison between two spelled arrays.

        Returns 0 where the elements are equal,
        1 where the first element is greater,
        and -1 where the second element is greater.

        The respective ordering differs between types.
        Non-class pitches and intervals use diatonic ordering,
        interval/pitch classes use line-of-fifths ordering.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).
        To test the overall equality of two spelled arrays,
        use :py:meth:`array_equal <SpelledArray.array_equal>`

        :param other: another spelled array or scalar
        :return: an array of ``-1`` / ``0`` / ``1`` (integer)
        """
        raise NotImplementedError
    
    def __lt__(self, other):
        """
        Element-wise ``<`` between two spelled arrays.

        :param other: the spelled array or scalar to compare to
        :return: a boolean array that indicates where this array is ``< other``
        """
        try:
            return self.compare(other) == -1
        except TypeError:
           return NotImplemented

    def __le__(self, other):
        """
        Element-wise ``<=`` between two spelled arrays.

        :param other: the spelled array or scalar to compare to
        :return: a boolean array that indicates where this array is ``<= other``
        """
        try:
            return self.compare(other) != 1
        except TypeError:
           return NotImplemented

    def __gt__(self, other):
        """
        Element-wise ``>`` between two spelled arrays.

        :param other: the spelled array or scalar to compare to
        :return: a boolean array that indicates where this array is ``> other``
        """
        try:
            return self.compare(other) == 1
        except TypeError:
           return NotImplemented

    def __ge__(self, other):
        """
        Element-wise ``>=`` between two spelled arrays.

        :param other: the spelled array or scalar to compare to
        :return: a boolean array that indicates where this array is ``>= other``
        """
        try:
            return self.compare(other) != -1
        except TypeError:
           return NotImplemented

    def __eq__(self, other):
        """
        Element-wise ``<=`` between two spelled arrays.

        :param other: the spelled array or scalar to compare to
        :return: a boolean array that indicates where this array is ``== other``
        """
        try:
            return self.compare(other) == 0
        except TypeError:
           return NotImplemented

    def __ne__(self, other):
        """
        Element-wise ``<=`` between two spelled arrays.

        :param other: the spelled array or scalar to compare to
        :return: a boolean array that indicates where this array is ``!= other``
        """
        try:
            return self.compare(other) != 0
        except TypeError:
           return NotImplemented

    # spelled interface

    @abc.abstractmethod
    def name(self):
        """
        Returns the names of the objects in the array
        as an array of strings of the same shape.

        :return: an array of notation strings
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fifths(self):
        """
        Return the position of the interval on the line of fifths.

        :return: an array of fifths (integers)
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def octaves(self):
        """
        For intervals, return the number of octaves the interval spans.
        Negative intervals start with -1, decreasing.
        For pitches, return the absolute octave of the pitch.

        :return: an array of external/independent octaves (integers)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def internal_octaves(self):
        """
        Return the internal octave representation of a pitch,
        which is dependent on the fifths.

        Only use this if you know what you are doing.

        :return: an array of internal/dependent octaves (integers)
        """
        raise NotImplementedError

    def degree(self):
        """
        Return the "relative scale degree" (0-6) to which the interval points
        (unison=0, 2nd=1, octave=0, 2nd down=6, etc.).
        For pitches, return the integer that corresponds to the letter (C=0, D=1, ...).

        :return: an array of degrees (integers)
        """
        return (self.fifths() * 4) % 7

    @abc.abstractmethod
    def alteration(self):
        """
        Return the number of semitones by which the interval is altered
        from its the perfect or major variant.
        Positive alteration always indicates augmentation,
        negative alteration indicates diminution (minor or smaller) of the interval's magnitude.
        For interval classes, alteration refers to the upward version of the interval
        (e.g. for ``m7``/``-M2`` it is -1).
        For pitches, return the accidentals (positive=sharps, negative=flats, 0=natural).

        :return: an array of alterations (integers)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def onehot(self):
        """
        Return a one-hot encoded tensor representing the elements of the array.
        Specialized versions of this method take ranges for their respective dimensions.

        :return: a one-hot tensor for the array
        """
        raise NotImplementedError

class AbstractSpelledArrayInterval(abc.ABC):
    """
    The interface for spelled interval array types.
    """
    @abc.abstractmethod
    def generic(self):
        """
        Return the generic interval, i.e. the number of diatonic steps modulo octave.
        Unlike degree(), the result respects the sign of the interval
        (unison=0, 2nd up=1, 2nd down=-1).

        :return: an array of generic intervals (integers)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def diatonic_steps(self):
        """
        Return the diatonic steps of the interval (unison=0, 2nd=1, ..., octave=7, ...).
        Respects both direction and octaves.

        :return: an array of diatonic steps (integers)
        """
        raise NotImplementedError

class AbstractSpelledArrayPitch(abc.ABC):
    """
    The interface for spelled pitch array types.
    """
    @abc.abstractmethod
    def letter(self):        
        """
        Returns the letter associated with the pitch (without accidentals).

        :return: an array of pitch letters (single-character strings)
        """
        raise NotImplementedError
        

class SpelledIntervalArray(SpelledArray, AbstractSpelledArrayInterval, Interval, Diatonic, Chromatic):
    """
    Represents an array of spelled intervals.
    """

    _print_name = "asi"
    
    def __init__(self, fifths, octaves):
        """        
        Takes two numpy arrays,
        one for fifths and one for internal/dependent octaves,
        both as integers.

        :param fifths: the internal fifths of each interval (numpy array of integers)
        :param octaves: the internal octaves of each interval (numpy array of integers)
        """
        if fifths.shape != octaves.shape:
            raise ValueError(f"Cannot create SpelledIntervalArray from arrays of different sizes ({fifths.shape} and {octaves.shape}).")
        self._fifths = fifths
        self._octaves = octaves

    @staticmethod
    def from_independent(fifths, octaves):
        """
        Create an interval array from fifths (interval class) and independent/external octaves.

        :param fifths:  the internal fifths of each interval (numpy array of integers)
        :param octaves: the external/independent octaves of each interval (numpy array of integers)
        :return: the corresponding interval array
        """
        return SpelledIntervalArray(fifths, octaves - (fifths * 4) // 7)

    @staticmethod
    def from_strings(strings):
        """
        Create an interval array from an array of strings (using spelled interval notation).

        :param strings: an array-like of interval notation strings
        :return: the corresponding interval array
        """
        def parse_interval(string):
            sign, octave, fifth = Spelled.parse_interval(string)
            if octave is None:
                raise ValueError(f"Missing octave specifier in interval '{string}'.")
            return sign, octave, fifth
        sign, octaves, fifths = np.vectorize(parse_interval, otypes=[np.int_, np.int_, np.int_])(strings)
        return SpelledIntervalArray(fifths * sign, (octaves - (fifths * 4) // 7) * sign)

    @staticmethod
    def from_array(intervals):
        """
        Create an interval array from an array of intervals.

        :param intervals: an array-like of ``SpelledInterval``
        :return: the corresponding interval array
        """
        def from_interval(interval):
            return interval.fifths(), interval.internal_octaves()
        fifths, octaves = np.vectorize(from_interval, otypes=[np.int_, np.int_])(intervals)
        return SpelledIntervalArray(fifths, octaves)

    @staticmethod
    def from_onehot(onehot, fifth_low, octave_low):
        """
        Create a spelled interval array from a one-hot tensor.
        ``fifth_low`` denotes the lower bound of the fifth range used in the vector,
        ``octave_low`` the lower bound of the octave range.
        The shape of the resulting array will be equivalent to the first n-2 dimensions of the input tensor.

        :param onehot: a one-hot tensor representing the intervals (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot tensor (integer)
        :param octave_low: the lowest octave expressible in the one-hot tensor (integer)
        :return: the corresponding interval array
        """
        if (onehot.sum((-2,-1)) != 1).any():
            raise ValueError(f"{onehot} is not a one-hot tensor.")
        
        ones = np.where(onehot==1)
        indices = ones[:-2] # first n-2 dimensions are indices
        fifths_values = ones[-2] + fifth_low
        octs_values = ones[-1] + octave_low

        new_shape = onehot.shape[:-2]
        new_fifths = np.zeros(new_shape, dtype=int)
        new_fifths[indices] = fifths_values
        new_octaves = np.zeros(new_shape, dtype=int)
        new_octaves[indices] = octs_values
        return SpelledIntervalArray.from_independent(new_fifths, new_octaves)

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
            return ((self.fifths() == item.fifths()) & \
                    (self.internal_octaves() == item.internal_octaves())).any()
        else:
            return False

    def __len__(self):
        return len(self.fifths())

    class SpelledIntervalArrayIter:
        def __init__(self, array):
            self._fifths_iter = array.fifths().__iter__()
            self._octaves_iter = array.internal_octaves().__iter__()

        def __next__(self):
            f = self._fifths_iter.__next__()
            o = self._octaves_iter.__next__()
            if isinstance(f, numbers.Integral):
                return SpelledInterval.from_fifths_and_octaves(f, o)
            else:
                return SpelledIntervalArray(f, o)
        
    def __iter__(self):
        return self.SpelledIntervalArrayIter(self)
        
    # interval interface

    @classmethod
    def unison(cls, shape):
        """
        Create an array of the given shape filled with perfect unisons (P1:0).

        :param shape: the shape of the resulting array (tuple of integers)
        :return: a ``SpelledIntervalArray`` of shape ``shape`` filled with P1:0
        """
        return cls(np.full(shape, 0, dtype=np.int_),np.full(shape, 0, dtype=np.int_))

    @classmethod
    def octave(cls, shape):
        """
        Return an array of the given shape filled with perfect octaves (P1:1).

        :param shape: the shape of the resulting array (tuple of integers)
        :return: a ``SpelledIntervalArray`` of shape ``shape`` filled with P1:0
        """
        return cls(np.full(shape, 0, dtype=np.int_),np.full(shape, 1, dtype=np.int_))

    @classmethod
    def chromatic_semitone(cls, shape):
        """
        Returns an array of the given shape filled with chromatic semitones (a1:0).

        :param shape: the shape of the resulting array (tuple of integers)
        :return: a ``SpelledIntervalArray`` of shape ``shape`` filled with a1:0
        """
        return SpelledIntervalArray(np.full(shape, 7, dtype=np.int_), np.full(shape, -4, dtype=np.int_))

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
        Returns the direction of the interval (1=up / 0=neutral / -1=down).
        The perfect unisons (``P1:0``) is considered neutral.
        
        :return: an array of ``-1`` / ``0`` / ``1`` (integer)
        """
        dia = np.sign(self.diatonic_steps())
        mask = dia == 0
        dia[mask] = np.sign((self.fifths()[mask] + 1) // 7)
        return dia

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

    def compare(self, other):
        """
        Element-wise comparison between two spelled arrays.

        Returns 0 where the elements are equal,
        1 where the first element is greater,
        and -1 where the second element is greater.

        Spelled intervals use diatonic ordering,
        for example ``P4:0 < a4:0 < aaaa4:0 < d5:0 < P5:0``.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).
        To test the overall equality of two spelled arrays,
        use :py:meth:`array_equal <SpelledIntervalArray.array_equal>`

        :param other: another ``SpelledIntervalArray`` or ``SpelledInterval``
        :return: an array of ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, SpelledInterval) or isinstance(other, SpelledIntervalArray):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot elements of {type(self)} to {type(other)}.")

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

    def onehot(self, fifth_range, octave_range, dtype=int):
        """
        Returns a one-hot encoding of the intervals in fifths and independent octaves as the innermost dimensions.
        The range of fifths and octaves is given by ``fifth_range`` and ``octave_range`` respectively,
        where each is a tuple ``(lower, upper)``.
        The outer shape of the output tensor is identical to the shape of the original array,
        so the resulting shape is ``original_shape + (n_fifths, n_octaves)``.

        :param fifth_range: the (inclusive) range of fifths (pair of integers)
        :param octave_range: the (inclusive) range of octaves (pair of integers)
        :param dtype: dtype of the resulting array (default: ``int``)
        :return: a one-hot tensor (numpy array)
        """
        flow, fhigh = fifth_range
        olow, ohigh = octave_range
        f = self.fifths()
        o = self.octaves()
        if (f < flow).any() or (f > fhigh).any():
            raise ValueError(f"The interval {self} is outside the given fifth range {fifth_range}.")
        if (o < olow).any() or (o > ohigh).any():
            raise ValueError(f"The interval {self} is outside the given octave range {octave_range}.")
        # translate fifths and octaves to 0-based indices (from [low,high] to [0,high-low])
        f = f - flow
        o = o - olow

        # compute one-hot indices
        inner_shape = f.shape
        # a tuple of indices:
        # the first dimensions encode the position in the original array,
        # the last two dimensions encode the fifth and octave position.
        indices = tuple(np.indices(inner_shape)) + (f, o)

        # initialize one-hot tensor with 0s
        out = np.zeros(inner_shape + (fhigh-flow+1, ohigh-olow+1), dtype=dtype)
        # set all elements picked by the indices to 1
        out[indices] = 1
        return out

class SpelledIntervalClassArray(SpelledArray, AbstractSpelledArrayInterval, Interval, Diatonic, Chromatic):
    """
    Represents an array of spelled interval classes, i.e. intervals without octave information.
    """

    _print_name = "asic"
    
    def __init__(self, fifths):
        """
        Takes a numpy array of fifths as integers.

        :param fifths: the internal fifths of each interval class (numpy array of integers)
        """
        self._fifths = fifths

    @staticmethod
    def from_strings(strings):
        """
        Create an interval-class array from an array of strings.

        :param strings: an array-like of interval-class notation strings
        :return: the corresponding interval-class array
        """
        def parse_ic(string):
            sign, octave, fifth = Spelled.parse_interval(string)
            if octave is not None:
                raise ValueError(f"Interval classes cannot have octave specifiers ({string}).")
            return sign, fifth
        sign, fifths = np.vectorize(parse_ic, otypes=[np.int_, np.int_])(strings)
        return SpelledIntervalClassArray(fifths * sign)

    @staticmethod
    def from_array(intervals):
        """
        Create an interval class array from an array of interval classes.

        :param intervals: an array-like of ``SpelledIntervalClass``
        :return: the corresponding interval-class array
        """
        fifths = np.vectorize(lambda i: i.fifths(), otypes=[np.int_])(intervals)
        return SpelledIntervalClassArray(fifths)

    @staticmethod
    def from_onehot(onehot, fifth_low):
        """
        Create a spelled interval-class array from a one-hot tensor.
        ``fifth_low`` denotes the lower bound of the fifth range used in the vector.
        The shape of the resulting array will be equivalent to the first n-1 dimensions of the input tensor.

        :param onehot: a one-hot tensor representing the interval classes (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot tensor (integer)
        :return: the corresponding interval-class array
        """
        if (onehot.sum(-1) != 1).any():
            raise ValueError(f"{onehot} is not a one-hot tensor.")
        
        ones = np.where(onehot==1)
        indices = ones[:-1] # first n-1 dimensions are indices
        fifths_values = ones[-1] + fifth_low

        new_shape = onehot.shape[:-1]
        new_fifths = np.zeros(new_shape, dtype=int)
        new_fifths[indices] = fifths_values
        return SpelledIntervalClassArray(new_fifths)

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

    def __len__(self):
        return len(self.fifths())
        
    class SpelledIntervalClassArrayIter:
        def __init__(self, array):
            self._fifths_iter = array.fifths().__iter__()
            
        def __next__(self):
            f = self._fifths_iter.__next__()
            if isinstance(f, numbers.Integral):
                return SpelledIntervalClass.from_fifths(f)
            else:
                return SpelledIntervalClassArray(f)
        
    def __iter__(self):
        return self.SpelledIntervalClassArrayIter(self)
        
    # interval interface

    @classmethod
    def unison(cls, shape):
        """
        Return an array of the given shape filled with perfect unisons (P1).

        :param shape: the shape of the resulting array (tuple of integers)
        :return: a ``SpelledIntervalClassArray`` of shape ``shape`` filled with P1
        """
        return cls(np.full(shape, 0, dtype=np.int_))

    @classmethod
    def octave(cls, shape):
        """
        Same as unison() since octaves are equivalent to unisons in interval-class space.

        :param shape: the shape of the resulting array (tuple of integers)
        :return: a ``SpelledIntervalClassArray`` of shape ``shape`` filled with P1
        """
        return cls.unison(shape)

    @classmethod
    def chromatic_semitone(cls, shape):
        """
        Returns an array of the given shape filled with chromatic semitones (a1).

        :param shape: the shape of the resulting array (tuple of integers)
        :return: a ``SpelledIntervalClassArray`` of shape ``shape`` filled with a1
        """
        return cls(np.full(shape, 7, dtype=np.int_))

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
        """
        Returns the (element-wise) directions of the intervals.
        The direction of each interval is determined by its shortest realization:
        ``m2``/``-M7`` is upward (1) while ``M7``/``-m2`` is downward (-1).
        Perfect unisons (``P1``) are neutral (0).
        
        :return: an array of ``-1`` / ``0`` / ``1`` (integer)
        """
        ds = self.diatonic_steps()
        mask = ds == 0
        out = np.ones_like(ds, dtype=np.int_)
        out[ds > 3] = -1
        out[mask] = np.sign((self.fifths()[mask] + 1) // 7)
        return out

    def ic(self):
        return self

    def embed(self):
        return SpelledIntervalArray.from_independent(self.fifths(), np.zeros_like(self.fifths()))

    def is_step(self):
        return np.isin(self.degree(), [0,1,6])

    # spelled interface

    def name(self):
        def intervalclass_name(fifths):
            return Spelled.interval_class_from_fifths(fifths)
        return np.vectorize(intervalclass_name, otypes=[np.str_])(self.fifths())

    def compare(self, other):
        """
        Element-wise comparison between two spelled arrays.

        Returns 0 where the elements are equal,
        1 where the first element is greater,
        and -1 where the second element is greater.

        Spelled interval classes use line-of-fifth ordering,
        for example ``P4 < P1 < P5 < M2``.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).
        To test the overall equality of two spelled arrays,
        use :py:meth:`array_equal <SpelledIntervalClasssArray.array_equal>`

        :param other: another ``SpelledIntervalClassArray`` or ``SpelledIntervalClass``
        :return: an array of ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, SpelledIntervalClass) or isinstance(other, SpelledIntervalClassArray):
            return np.sign((self - other).fifths())
        else:
            raise TypeError(f"Cannot elements of {type(self)} to {type(other)}.")

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

    def onehot(self, fifth_range, dtype=int):
        """
        Returns a one-hot encoding of the interval classes in fifths as the innermost dimension.
        The range of fifths is given by ``fifth_range`` as a tuple ``(lower, upper)``.
        The outer shape of the output tensor is identical to the shape of the original array,
        so the resulting shape is ``original_shape + (n_fifths,)``.

        :param fifth_range: the (inclusive) range of fifths (pair of integers)
        :param dtype: dtype of the resulting array (default: ``int``)
        :return: a one-hot tensor (numpy array)
        """
        flow, fhigh = fifth_range
        f = self.fifths()
        if (f < flow).any() or (f > fhigh).any():
            raise ValueError(f"The interval {self} is outside the given fifth range {fifth_range}.")
        # translate fifths and octaves to 0-based indices (from [low,high] to [0,high-low])
        f = f - flow

        # compute one-hot indices
        inner_shape = f.shape
        # a tuple of indices:
        # the first dimensions encode the position in the original array,
        # the last dimension encodes the fifth position.
        indices = tuple(np.indices(inner_shape)) + (f,)

        # initialize one-hot tensor with 0s
        out = np.zeros(inner_shape + (fhigh-flow+1,), dtype=dtype)
        # set all elements picked by the indices to 1
        out[indices] = 1
        return out

class SpelledPitchArray(SpelledArray, AbstractSpelledArrayPitch, Pitch):
    """
    Represents an array of spelled pitches.
    """

    _print_name = "asp"

    # constructors
    
    def __init__(self, fifths, octaves):
        """
        Takes two numpy arrays,
        one for fifths and one for (internal/dependent) octaves,
        both as integers.

        :param fifths: the internal fifths of each pitch (numpy array of integers)
        :param octaves: the internal octaves of each pitch (numpy array of integers)
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

        :param fifths:  the internal fifths of each pitch (numpy array of integers)
        :param octaves: the external/independent octaves of each pitch (numpy array of integers)
        :return: the corresponding pitch array
        """
        return SpelledPitchArray(fifths, octaves - (fifths * 4) // 7)

    @staticmethod
    def from_strings(strings):
        """
        Create a pitch array from an array of strings.

        :param strings: an array-like of pitch notation strings
        :return: the corresponding pitch array
        """
        # assert isinstance(strings.dtype, np.str_)
        def parse_pitch(string):
            octave, fifth = Spelled.parse_pitch(string)
            if octave is None:
                raise ValueError(f"Missing octave specifier in pitch '{string}'.")
            return octave, fifth
        octaves, fifths = np.vectorize(parse_pitch, otypes=[np.int_, np.int_])(strings)
        return SpelledPitchArray.from_independent(fifths, octaves)

    @staticmethod
    def from_array(pitches):
        """
        Create a pitch array from an array of pitches.

        :param intervals: an array-like of ``SpelledPitch``
        :return: the corresponding pitch array
        """
        def from_pitch(pitch):
            return pitch.fifths(), pitch.internal_octaves()
        fifths, octaves = np.vectorize(from_pitch, otypes=[np.int_, np.int_])(pitches)
        return SpelledPitchArray(fifths, octaves)

    @staticmethod
    def from_onehot(onehot, fifth_low, octave_low):
        """
        Create a spelled pitch array from a one-hot tensor.
        ``fifth_low`` denotes the lower bound of the fifth range used in the vector,
        ``octave_low`` the lower bound of the octave range.
        The shape of the resulting array will be equivalent to the first n-2 dimensions of the input tensor.

        :param onehot: a one-hot tensor representing the pitches (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot tensor (integer)
        :param octave_low: the lowest octave expressible in the one-hot tensor (integer)
        :return: the corresponding pitch array
        """
        if (onehot.sum((-2,-1)) != 1).any():
            raise ValueError(f"{onehot} is not a one-hot tensor.")
        
        ones = np.where(onehot==1)
        indices = ones[:-2] # first n-2 dimensions are indices
        fifths_values = ones[-2] + fifth_low
        octs_values = ones[-1] + octave_low

        new_shape = onehot.shape[:-2]
        new_fifths = np.zeros(new_shape, dtype=int)
        new_fifths[indices] = fifths_values
        new_octaves = np.zeros(new_shape, dtype=int)
        new_octaves[indices] = octs_values
        return SpelledPitchArray.from_independent(new_fifths, new_octaves)

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
            return ((self.fifths() == item.fifths()) & \
                    (self.internal_octaves() == item.internal_octaves())).any()
        else:
            return False

    def __len__(self):
        return len(self.fifths())
    
    class SpelledPitchArrayIter:
        def __init__(self, array):
            self._fifths_iter = array.fifths().__iter__()
            self._octaves_iter = array.internal_octaves().__iter__()

        def __next__(self):
            f = self._fifths_iter.__next__()
            o = self._octaves_iter.__next__()
            if isinstance(f, numbers.Integral):
                return SpelledPitch.from_fifths_and_octaves(f, o)
            else:
                return SpelledPitchArray(f, o)
        
    def __iter__(self):
        return self.SpelledPitchArrayIter(self)
        
    # Pitch interface

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

    def compare(self, other):
        """
        Element-wise comparison between two spelled arrays.

        Returns 0 where the elements are equal,
        1 where the first element is greater,
        and -1 where the second element is greater.

        Spelled pitches use diatonic ordering,
        for example ``F4 < F#4 < F####4 < Gb4 < G4``.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).
        To test the overall equality of two spelled arrays,
        use :py:meth:`array_equal <SpelledPitch.array_equal>`

        :param other: another ``SpelledPitchArray`` or ``SpelledPitch``
        :return: an array of ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, SpelledPitch) or isinstance(other, SpelledPitchArray):
            return (self - other).direction()
        else:
            raise TypeError(f"Cannot elements of {type(self)} to {type(other)}.")

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

    def alteration(self):
        return (self.fifths() + 1) // 7

    def letter(self):
        return ((self.degree() + 2) % 7 + ord('A')).astype(np.uint8).view('c').astype(np.str_)

    def onehot(self, fifth_range, octave_range, dtype=int):
        """
        Returns a one-hot encoding of the pitches in fifths and independent octaves as the innermost dimensions.
        The range of fifths and octaves is given by ``fifth_range`` and ``octave_range`` respectively,
        where each is a tuple ``(lower, upper)``.
        The outer shape of the output tensor is identical to the shape of the original array,
        so the resulting shape is ``original_shape + (n_fifths, n_octaves)``.

        :param fifth_range: the (inclusive) range of fifths (pair of integers)
        :param octave_range: the (inclusive) range of octaves (pair of integers)
        :param dtype: dtype of the resulting array (default: ``int``)
        :return: a one-hot tensor (numpy array)
        """
        flow, fhigh = fifth_range
        olow, ohigh = octave_range
        f = self.fifths()
        o = self.octaves()
        if (f < flow).any() or (f > fhigh).any():
            raise ValueError(f"The pitch {self} is outside the given fifth range {fifth_range}.")
        if (o < olow).any() or (o > ohigh).any():
            raise ValueError(f"The pitch {self} is outside the given octave range {octave_range}.")
        # translate fifths and octaves to 0-based indices (from [low,high] to [0,high-low])
        f = f - flow
        o = o - olow

        # compute one-hot indices
        inner_shape = f.shape
        # a tuple of indices:
        # the first dimensions encode the position in the original array,
        # the last two dimensions encode the fifth and octave position.
        indices = tuple(np.indices(inner_shape)) + (f, o)

        # initialize one-hot tensor with 0s
        out = np.zeros(inner_shape + (fhigh-flow+1, ohigh-olow+1), dtype=dtype)
        # set all elements picked by the indices to 1
        out[indices] = 1
        return out

class SpelledPitchClassArray(SpelledArray, AbstractSpelledArrayPitch, Pitch):
    """
    Represents a spelled pitch class, i.e. a pitch without octave information.
    """

    _print_name = "aspc"

    def __init__(self, fifths):
        """
        Takes a numpy array of fifths as integers.

        :param fifths: the internal fifths of each pitch class (numpy array of integers)
        """
        self._fifths = fifths

    @staticmethod
    def from_strings(strings):
        """
        Create a pitch-class array from an array of strings.

        :param strings: an array-like of pitch-class notation strings
        :return: the corresponding pitch-class array
        """
        def parse_pc(string):
            octave, fifth = Spelled.parse_pitch(string)
            if octave is not None:
                raise ValueError(f"Pitch classes cannot have octave specifiers ({string}).")
            return fifth
        fifths = np.vectorize(parse_pc, otypes=[np.int_])(strings)
        return SpelledPitchClassArray(fifths)

    @staticmethod
    def from_array(pitches):
        """
        Create an pitch class array from an array of pitch classes.

        :param intervals: an array-like of ``SpelledPitchClass``
        :return: the corresponding pitch-class array
        """
        fifths = np.vectorize(lambda i: i.fifths(), otypes=[np.int_])(pitches)
        return SpelledPitchClassArray(fifths)

    @staticmethod
    def from_onehot(onehot, fifth_low):
        """
        Create a spelled pitch-class array from a one-hot tensor.
        ``fifth_low`` denotes the lower bound of the fifth range used in the vector.
        The shape of the resulting array will be equivalent to the first n-1 dimensions of the input tensor.

        :param onehot: a one-hot tensor representing the pitch classes (numpy array)
        :param fifth_low: the lowest fifth expressible in the one-hot tensor (integer)
        :return: the corresponding pitch-class array
        """
        if (onehot.sum(-1) != 1).any():
            raise ValueError(f"{onehot} is not a one-hot tensor.")
        
        ones = np.where(onehot==1)
        indices = ones[:-1] # first n-1 dimensions are indices
        fifths_values = ones[-1] + fifth_low

        new_shape = onehot.shape[:-1]
        new_fifths = np.zeros(new_shape, dtype=int)
        new_fifths[indices] = fifths_values
        return SpelledPitchClassArray(new_fifths)

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

    def __len__(self):
        return len(self.fifths())
    
    class SpelledPitchClassArrayIter:
        def __init__(self, array):
            self._fifths_iter = array.fifths().__iter__()
            
        def __next__(self):
            f = self._fifths_iter.__next__()
            if isinstance(f, numbers.Integral):
                return SpelledPitchClass.from_fifths(f)
            else:
                return SpelledPitchClassArray(f)
        
    def __iter__(self):
        return self.SpelledPitchClassArrayIter(self)
        
    # pitch interface

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

    def name(self):
        def pitchclass_name(fifths):
            return Spelled.pitch_class_from_fifths(fifths)
        return np.vectorize(pitchclass_name, otypes=[np.str_])(self.fifths())

    def compare(self, other):
        """
        Element-wise comparison between two spelled arrays.

        Returns 0 where the elements are equal,
        1 where the first element is greater,
        and -1 where the second element is greater.

        Spelled pitch classes use line-of-fifth ordering,
        for example ``Bb < F < C < G < D``.

        This method can be indirectly used through binary comparison operators
        (including ``==``, ``<`` etc.).
        To test the overall equality of two spelled arrays,
        use :py:meth:`array_equal <SpelledPitchClassArray.array_equal>`

        :param other: another ``SpelledPitchClassArray`` or ``SpelledPitchClass``
        :return: an array of ``-1`` / ``0`` / ``1`` (integer)
        """
        if isinstance(other, SpelledPitchClass) or isinstance(other, SpelledPitchClassArray):
            return np.sign((self - other).fifths())
        else:
            raise TypeError(f"Cannot elements of {type(self)} to {type(other)}.")

    def fifths(self):
        return self._fifths

    def octaves(self):
        return 0

    def internal_octaves(self):
        return 0

    def alteration(self):
        return (self.fifths() + 1) // 7

    def letter(self):
        return ((self.degree() + 2) % 7 + ord('A')).astype(np.uint8).view('c').astype(np.str_)

    def onehot(self, fifth_range, dtype=int):
        """
        Returns a one-hot encoding of the pitch classes in fifths as the innermost dimension.
        The range of fifths is given by ``fifth_range`` as a tuple ``(lower, upper)``.
        The outer shape of the output tensor is identical to the shape of the original array,
        so the resulting shape is ``original_shape + (n_fifths,)``.

        :param fifth_range: the (inclusive) range of fifths (pair of integers)
        :param dtype: dtype of the resulting array (default: ``int``)
        :return: a one-hot tensor (numpy array)
        """
        flow, fhigh = fifth_range
        f = self.fifths()
        if (f < flow).any() or (f > fhigh).any():
            raise ValueError(f"The interval {self} is outside the given fifth range {fifth_range}.")
        # translate fifths and octaves to 0-based indices (from [low,high] to [0,high-low])
        f = f - flow

        # compute one-hot indices
        inner_shape = f.shape
        # a tuple of indices:
        # the first dimensions encode the position in the original array,
        # the last dimension encodes the fifth position.
        indices = tuple(np.indices(inner_shape)) + (f,)

        # initialize one-hot tensor with 0s
        out = np.zeros(inner_shape + (fhigh-flow+1,), dtype=dtype)
        # set all elements picked by the indices to 1
        out[indices] = 1
        return out

# shorthand constructors

def asi(things, things2=None):
    """
    A quick way to construct a spelled-interval array.
    Takes an array-like of strings or spelled intervals,
    or two array-likes of integers (fifths and internal/dependent octaves).

    :param things: an array-like of strings / fifths (integers) / ``SpelledInterval``
    :param things2: an array-like of dependent octaves (integers), when providing fifths in the first parameter
    :return: a spelled-interval array of the same shape as the input
    """
    input = np.array(things)
    if input.dtype.type is np.str_ or input.dtype.type is np.string_:
        return SpelledIntervalArray.from_strings(input)
    if isinstance(input.flat[0], SpelledInterval):
        return SpelledIntervalArray.from_array(input)
    else:
        return SpelledIntervalArray(input, np.array(things2))

def asic(things):
    """
    A quick way to construct a spelled-interval-class array.
    Takes either an array-like of strings or spelled interval classes,
    or an array-like of integers (fifths).

    :param things: an array-like of strings / fifths (integers) / ``SpelledIntervalClass``
    :return: a spelled-interval-class array of the same shape as the input
    """
    input = np.array(things)
    if input.dtype.type is np.str_ or input.dtype.type is np.string_:
        return SpelledIntervalClassArray.from_strings(input)
    if isinstance(input.flat[0], SpelledIntervalClass):
        return SpelledIntervalClassArray.from_array(input)
    else:
        return SpelledIntervalClassArray(input)

def asp(things, things2=None):
    """
    A quick way to construct a spelled-pitch array.
    Takes either an array-like of strings or spelled pitches,
    or two array-likes of integers (fifths and internal/dependent octaves).

    :param things: an array-like of strings / fifths (integers) / ``SpelledPitch``
    :param things2: an array-like of dependent octaves (integers), when providing fifths in the first parameter
    :return: a spelled-pitch array of the same shape as the input
    """
    input = np.array(things)
    if input.dtype.type is np.str_ or input.dtype.type is np.string_:
        return SpelledPitchArray.from_strings(input)
    if isinstance(input.flat[0], SpelledPitch):
        return SpelledPitchArray.from_array(input)
    else:
        return SpelledPitchArray(input, np.array(things2))

def aspc(things):
    """
    A quick way to construct a spelled-pitch-class array.
    Takes either an array-like of strings or spelled pitch classes,
    or an array-like of integers (fifths).

    :param things: an array-like of strings / fifths (integers) / ``SpelledPitchClass``
    :return: a spelled-pitch-class array of the same shape as the input
    """
    input = np.array(things)
    if input.dtype.type is np.str_ or input.dtype.type is np.string_:
        return SpelledPitchClassArray.from_strings(input)
    if isinstance(input.flat[0], SpelledPitchClass):
        return SpelledPitchClassArray.from_array(input)
    else:
        return SpelledPitchClassArray(input)
