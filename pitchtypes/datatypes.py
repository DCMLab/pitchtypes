import re
import numpy as np
import numbers
from functools import total_ordering

@total_ordering
class Pitch:
    """
    Base class for objects describing a point in a pitch space. The purpose of this class is to make developing and
    maintaining pitch types convenient by providing basic functionality, like a one-liner to create the associated
    interval class and basic arithmetic operations (see Inverval class). Apart from that, the abstract Pitch class is
    just a wrapper around some value. The semantics of this value and any extended functionality is defined via the
    derived classes.
    """

    _associated_interval_type = None
    _pitch_class_origin = None
    _pitch_class_period = None
    is_pitch = True
    is_interval = False

    # store converters for classes derived from Pitch;
    # it's a dict of dicts, so that _converters[A][B] returns is a list of functions that, when executed
    # successively, converts A to B
    _converters = {}

    @classmethod
    def associate_interval_type(pitch_type, *, overwrite_pitch_type=None, overwrite_interval_type=None):
        """
        Class decorator to link 'pitch_type' and the specified interval class by adding _associated_interval_type and _associated_pitch_type
        attribute, respectively. Raises an error if one of the classes already has the corresponding attribute, which
        would be overwritten. Overwriting can be forced, which is for instance needed when linking a interval class to a
        pitch class that was derived from another pitch class, which already has an associated interval class.
        :param overwrite_pitch_type: if None (default), adds a pitch class to the interval class if is does not already
        have one and raises an AttributeError otherwise; if False, never adds a pitch class to the interval class; if
        True, always adds a pitch class to the interval class (possibly overwriting an existing one)
        :param overwrite_interval_type: if None (default), adds a interval class to the pitch class if is does not already
        have one and raises an AttributeError otherwise; if False, never adds a interval class to the pitch class; if
        True, always adds a interval class to the pitch class (possibly overwriting an existing one)
        """
        def decorator(interval_type):
            """
            :param interval_type: interval class to be linked (will be modified by adding the _associated_pitch_type attribute)
            :return: modified interval_class
            """
            # check that provided class is actually derived from Interval
            if Interval not in interval_type.__mro__:
                raise TypeError(f"Provided class {interval_type} does not derive from {Interval}")
            # check if pitch class already has an associated interval class
            if overwrite_interval_type is None and pitch_type._associated_interval_type is not None:
                raise AttributeError(
                    f"Class '{pitch_type}' already has an associated interval type ({pitch_type._associated_interval_type})")
            # check if interval class already has an associated pitch class
            if overwrite_pitch_type is None and interval_type._associated_pitch_type is not None:
                raise AttributeError(
                    f"Class '{interval_type}' already has an associated pitch type ({interval_type._associated_pitch_type})")
            # let the pitch class know its interval class and vice versa
            if overwrite_interval_type is None or overwrite_interval_type:
                pitch_type._associated_interval_type = interval_type
            if overwrite_pitch_type is None or overwrite_pitch_type:
                interval_type._associated_pitch_type = pitch_type
            return interval_type
        return decorator

    @classmethod
    def _assert_has_associated_interval_type(cls):
        if cls._associated_interval_type is None:
            raise AttributeError(f"This class ({cls}) does not have an associated interval class")

    @classmethod
    def _assert_is_pitch(cls, other):
        if not isinstance(other, cls):
            raise TypeError(f"Object is not of correct type (expected {cls}, got {type(other)}")

    @classmethod
    def _assert_is_interval(cls, other):
        if not isinstance(other, cls._associated_interval_type):
            raise TypeError(
                f"Object is not of correct type (expected {cls._associated_interval_type}, got {type(other)}")

    @staticmethod
    def _check_class_param_consistency(param_value, object_value):
        """
        Check consistency between the two values and set default
        :param param_value: value specified via parameter
        :param object_value: value obtained from object
        :return:
              param_value:  | None  | True  | False
        --------------------------------------------
        object value: None  | False | True  | False
        object value: True  | True  | True  | ERROR
        object value: False | False | ERROR | False
        """
        if param_value is None and object_value is None:
            return False
        elif param_value is None:
            return object_value
        elif object_value is None:
            return param_value
        else:
            if object_value == param_value:
                return param_value
            else:
                raise ValueError(f"Inconsistent values for class parameter between "
                                 f"provided object ({object_value}) and "
                                 f"parameter specification ({param_value})")

    @staticmethod
    def register_converter(from_type, to_type, conv_func,
                           overwrite_explicit_converters=None,
                           overwrite_implicit_converter=True,
                           create_implicit_converters=True):
        """
        Register a converter from from_type to other type. The converter function should be function taking as its
        single argument an from_type object and returning an other_type object.
        :param to_type: other type derived from Pitch, which the converter function converts to
        :param conv_func: converter function from from_type to other_type
        :param overwrite_explicit_converters: can be True, False, or None (default); if True and there exists an
        explicit converter (i.e. the list of converter functions is of length 1), replace it by this converter function;
        if False, don't replace explicit converters; if None, raise a ValueError if an explicit converter exists
        :param overwrite_implicit_converter: if there exists an implicit converter (i.e. the list of converter functions
        is of length greater than 1) replace it by this converter function
        :param create_implicit_converters: if there is an (explicit or implicit) converter from type X to type
        from_type, add an implicit converter from type X to other_type by extending the list of converter functions from
        X to from_type by this converter function; if there already exists an (explicit or implicit) converter from X to
        other_type, it will not be overwritten
        """
        # not self-conversion
        if from_type == to_type:
            raise TypeError(f"Not allows to add converters from a type to itself (from: {from_type}, to: {to_type})")
        # initialise converter dict if it does not exist
        if from_type not in Pitch._converters:
            Pitch._converters[from_type] = {}
        # get existing converters from from_type to to_type and decide whether to set new converter
        set_new_converter = False
        try:
            converter = Pitch.get_converter(from_type, to_type)
        except NotImplementedError:
            # no existing converters
            set_new_converter = True
        else:
            # implicit or explicit converter are already registered
            if len(converter) == 1:
                # explicit converter
                if overwrite_explicit_converters is None:
                    raise ValueError("An explicit converter already exists. Set overwrite_explicit_converters=True to "
                                     "overwrite.")
                elif overwrite_explicit_converters:
                    set_new_converter = True
            else:
                # implicit converter
                if overwrite_implicit_converter:
                    set_new_converter = True
        # set the new converter
        if set_new_converter:
            Pitch._converters[from_type][to_type] = [conv_func]
        # extend implicit converters
        if create_implicit_converters:
            for another_from_type, other_converters in Pitch._converters.items():
                # remember new converters to not change dict while iterating over it
                new_converters = []
                for another_to_type, converter_pipeline in other_converters.items():
                    # trying to prepend this converter [from_type --> to_type == another_from_type --> another_to_type]
                    if to_type == another_from_type:
                        # don't add implicit self-converters
                        if from_type == another_to_type:
                            continue
                        # get existing converters from_type --> ???
                        converters = Pitch.get_converter(from_type)
                        # add the extended converter if one does not exist
                        if another_to_type not in converters:
                            converters[another_to_type] = [conv_func] + converter_pipeline
                    # try to append this converter [another_from_type --> another_to_type == from_type --> to_type]
                    if another_to_type == from_type:
                        # don't add implicit self-converters
                        if another_from_type == to_type:
                            continue
                        # already initialised and we have the existing converters another_from_type --> ???
                        # add the extended converter if one does not exist
                        if to_type not in other_converters:
                            new_converters.append((to_type, converter_pipeline + [conv_func]))
                # insert new converters
                for another_to_type, converter_pipeline in new_converters:
                    other_converters[another_to_type] = converter_pipeline

    @staticmethod
    def get_converter(from_type, to_type=None):
        # return dedicated converter if other_type was specified or list of existing converters otherwise
        if to_type is not None:
            all_converters = Pitch.get_converter(from_type)
            try:
                return all_converters[to_type]
            except KeyError:
                raise NotImplementedError(f"Type '{from_type}' does not have any converter registered for type "
                                          f"'{to_type}'")
        else:
            try:
                return Pitch._converters[from_type]
            except KeyError:
                raise NotImplementedError(f"There are no converters registered for type '{from_type}'")

    @staticmethod
    def _convert(value, to_type):
        Pitch._check_type(value, bases=(Pitch, Interval))
        Pitch._check_type(to_type, bases=(Pitch, Interval), value_is_type=True)
        if to_type == value.__class__:
            # skip self-conversion
            return value
        else:
            # use conversion pipeline
            ret = value
            for converter in Pitch.get_converter(value.__class__, to_type):
                ret = converter(ret)
            # check for correct type
            if not isinstance(ret, to_type):
                raise TypeError(f"Conversion failed, expected type {to_type} but got {type(ret)}")
            if Pitch in value.__class__.__mro__:
                if not value.is_pitch_class() == ret.is_pitch_class():
                    raise TypeError(f"Conversion failed, inconsistent pitch class attribute "
                                    f"(before: {value.is_pitch_class()}, after: {ret._is_pitch_class})")
                else:
                    return ret if not value.is_pitch_class() else ret.to_pitch_class()
            elif Interval in value.__class__.__mro__:
                if not value.is_interval_class() == ret.is_interval_class():
                    raise TypeError(f"Conversion failed, inconsistent interval class attribute "
                                    f"(before: {value.is_interval_class()}, after: {ret._is_interval_class})")
                else:
                    return ret if not value.is_interval_class() else ret.to_interval_class()

    @staticmethod
    def _check_type(value, *, types=(), bases=(), value_is_type=False):
        # check for type
        if value_is_type:
            # type was given
            if value in types:
                return True
        else:
            # value was given
            if isinstance(value, types):
                return True
        # check for base classes
        for b in bases:
            if (value_is_type and b in value.__mro__) or (not value_is_type and b in value.__class__.__mro__):
                return True
        raise TypeError(f"argument should be of type [{', '.join([str(t) for t in types])}] "
                        f"or derived from [{', '.join([str(b) for b in bases])}]; "
                        f"got {value} of type {type(value)}")

    @classmethod
    def _map_to_pitch_class(cls, value):
        if cls._pitch_class_origin is None or cls._pitch_class_period is None:
            raise NotImplementedError
        else:
            return (value - cls._pitch_class_origin) % cls._pitch_class_period

    @classmethod
    def pitch_class_origin(cls):
        """Returns the origin with respect to which pitch classes are computed as pitch object"""
        if cls._pitch_class_origin is None:
            raise NotImplementedError
        else:
            return cls(cls._pitch_class_origin)

    @classmethod
    def pitch_class_period(cls):
        """Returns the perior used to compute pitch classes as interval object"""
        if cls._pitch_class_period is None:
            raise NotImplementedError
        else:
            cls._assert_has_associated_interval_type()
            return cls._associated_interval_type(cls._pitch_class_period)

    def is_pitch_class(self):
        return self._is_pitch_class

    def to_pitch_class(self):
        return self.__class__(value=self._value, is_pitch_class=True)

    def pitch_class_phase(self, two_pi=False):
        if self._pitch_class_period is None:
            raise NotImplementedError
        if not self.is_pitch_class():
            return self.to_pitch_class().pitch_class_phase(two_pi=two_pi)
        else:
            normed_phase = self._value / self._pitch_class_period
            if two_pi:
                return normed_phase * 2 * np.pi
            else:
                return normed_phase

    def __init__(self, value, *args, is_pitch_class=None, **kwargs):
        # if value is derived from Pitch, try to convert to this type and get the _value
        value_is_pitch_class = None
        if Pitch in value.__class__.__mro__:
            value_is_pitch_class = value.is_pitch_class()
            value = value.convert_to(self.__class__)._value
        super().__init__(*args, **kwargs)
        self._value = value
        # check consistency for class parameter
        is_pitch_class = Pitch._check_class_param_consistency(is_pitch_class, value_is_pitch_class)
        # set pitch class and return
        if is_pitch_class:
            self._value = self._map_to_pitch_class(self._value)
            self._is_pitch_class = True
        else:
            self._is_pitch_class = False

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value})"

    def __sub__(self, other):
        # do arithmetics
        self._assert_has_associated_interval_type()
        try:
            self._assert_is_pitch(other)
            ret = self._associated_interval_type(self._value - other._value)
        except TypeError:
            self._assert_is_interval(other)
            ret = self.__class__(self._value - other._value)
        # check for class/non-class
        if other.is_pitch:
            other_is_class = other.is_pitch_class()
        else:
            other_is_class = other.is_interval_class()
        if self.is_pitch_class() != other_is_class:
            raise TypeError(f"Cannot combine pitch class and non-class types "
                            f"(this: {self.is_pitch_class()}, other: {other_is_class})")
        # convert to class if required
        if self.is_pitch and self.is_pitch_class() or self.is_interval and self.is_interval_class():
            if ret.is_pitch:
                return ret.to_pitch_class()
            else:
                return ret.to_interval_class()
        else:
            return ret

    def __add__(self, other):
        # do arithmetics
        self._assert_has_associated_interval_type()
        self._assert_is_interval(other)
        ret = self.__class__(self._value + other._value)
        # check for class/non-class
        if self.is_pitch_class() != other.is_interval_class():
            raise TypeError(f"Cannot combine pitch class and non-class types "
                            f"(this: {self.is_pitch_class()}, other: {other.is_interval_class()})")
        # convert to class if required
        return ret if not self.is_pitch_class() else ret.to_pitch_class()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._value == other._value
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self._value)

    def __lt__(self, other):
        if self.is_pitch_class():
            raise TypeError("Cannot compare pitch classes (cyclic order)")
        else:
            if isinstance(other, self.__class__):
                return self._value < other._value
            else:
                return NotImplemented

    def to_interval(self):
        self._assert_has_associated_interval_type()
        return self._associated_interval_type(self._value, is_interval_class=self.is_pitch_class())

    def convert_to(self, other_type):
        Pitch._check_type(other_type, bases=(Pitch,), value_is_type=True)
        return Pitch._convert(self, other_type)


@total_ordering
class Interval:
    """
    Base type for objects describing direction and magnitude in a pitch space. A type derived from Interval should have an
    associated Pitch type and should be defined via create_interval_class method, which will also
    take care of letting both types know of each other. Creating multiple Interval type for the same Pitch type
    is likely to cause trouble, but you can force it if feel that you absolutely need to.
    """

    _associated_pitch_type = None

    is_pitch = False
    is_interval = True

    @classmethod
    def _assert_has_associated_pitch_type(cls):
        if cls._associated_pitch_type is None:
            raise AttributeError(f"This type ({cls}) does not have an associated pitch type")

    @classmethod
    def _assert_is_interval(cls, other):
        if not isinstance(other, cls):
            raise TypeError(f"Object is not of correct type (expected {cls}, got {type(other)}")

    def __init__(self, value, *args, is_interval_class=None, **kwargs):
        # if value is derived from Interval, try to convert to converter to this type and get the _value
        value_is_interval_class = None
        if Interval in value.__class__.__mro__:
            value_is_interval_class = value.is_interval_class()
            value = value.convert_to(self.__class__)._value
        super().__init__(*args, **kwargs)
        self._value = value
        # check consistency for class parameter
        is_interval_class = Pitch._check_class_param_consistency(is_interval_class, value_is_interval_class)
        # set interval class and return
        if is_interval_class:
            self._value = self._map_to_interval_class(self._value)
            self._is_interval_class = True
        else:
            self._is_interval_class = False

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value})"

    def __sub__(self, other):
        # do arithmetics
        self._assert_is_interval(other)
        ret = self.__class__(self._value - other._value)
        # check for class/non-class
        if self.is_interval_class() != other.is_interval_class():
            raise TypeError(f"Cannot combine interval class and non-class types "
                            f"(this: {self.is_interval_class()}, other: {other.is_interval_class()})")
        # convert to class if required
        return ret if not self.is_interval_class() else ret.to_interval_class()

    def __add__(self, other):
        # do arithmetics
        self._assert_is_interval(other)
        ret = self.__class__(self._value + other._value)
        # check for class/non-class
        if self.is_interval_class() != other.is_interval_class():
            raise TypeError(f"Cannot combine interval class and non-class types "
                            f"(this: {self.is_interval_class()}, other: {other.is_interval_class()})")
        # convert to class if required
        return ret if not self.is_interval_class() else ret.to_interval_class()

    def __mul__(self, other):
        ret = self.__class__(self._value * other)
        return ret if not self.is_interval_class() else ret.to_interval_class()

    def __rmul__(self, other):
        return self.__mul__(other)

    def __lt__(self, other):
        if self.is_interval_class():
            raise TypeError("Cannot compare interval classes (cyclic order)")
        else:
            if isinstance(other, self.__class__):
                return self._value < other._value
            else:
                return NotImplemented

    def __truediv__(self, other):
        return self.__class__(self.__mul__(1 / other))

    def __abs__(self):
        return abs(self._value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._value == other._value
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self._value)

    def to_pitch(self):
        self._assert_has_associated_pitch_type()
        return self._associated_pitch_type(self._value, is_pitch_class=self.is_interval_class())

    @classmethod
    def _map_to_interval_class(cls, value):
        value %= cls._associated_pitch_type._pitch_class_period
        if value > cls._associated_pitch_type._pitch_class_period / 2:
            value -= cls._associated_pitch_type._pitch_class_period
        return value

    def is_interval_class(self):
        return self._is_interval_class

    def to_interval_class(self):
        return self.__class__(value=self._value, is_interval_class=True)

    def phase_diff(self, two_pi=False):
        if not self.is_interval_class():
            return self.to_interval_class().phase_diff(two_pi=two_pi)
        else:
            normed_phase_diff = self._value / self._associated_pitch_type._pitch_class_period
            if two_pi:
                return normed_phase_diff * 2 * np.pi
            else:
                return normed_phase_diff

    def convert_to(self, other_type):
        Pitch._check_type(other_type, bases=(Interval,), value_is_type=True)
        try:
            # try direct converter
            return Pitch._convert(self, other_type)
        except NotImplementedError:
            # try to convert via equivalent pitch types
            self._assert_has_associated_pitch_type()
            other_type._assert_has_associated_pitch_type()
            # convert interval-->equivalent pitch-->other pitch type-->equivalent interval
            other_interval = self.to_pitch().convert_to(other_type._associated_pitch_type).to_interval()
            # but pitch<-->value (pitch<-->interval) conversion relies on an implicit origin;
            # if the two origins of the two different pitch types are not identical,
            # we are off by the corresponding difference;
            # the origin can be retrieved as the equivalent pitch of the zero interval
            origin_from = (self - self).to_pitch().convert_to(other_type._associated_pitch_type) # pitch
            origin_to = (other_interval - other_interval).to_pitch() # pitch
            origin_difference = origin_to - origin_from # interval
            # now we add that difference (we move from the "from" origin to the "to" origin)
            out = other_interval + origin_difference
            # check for correct type
            if not isinstance(out, other_type):
                raise TypeError(f"Conversion failed, expected type {other_type} but got {type(out)}")
            return out if not self.is_interval_class() else out.to_interval_class()


class SpelledPitch(Pitch):
    _diatonic_fifth_steps = {"F": -1, "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5}
    name_regex = re.compile("^(?P<class>[A-G])(?P<modifiers>(b*)|(#*))(?P<octave>(-?[0-9]+)?)$")

    _pitch_class_origin = np.array([0, 0])

    @classmethod
    def _map_to_pitch_class(cls, value):
        return np.array([value[0], 0])

    def __init__(self, value, *args, is_pitch_class=None, **kwargs):
        Pitch._check_type(value, types=(numbers.Number, str, np.ndarray, list, tuple), bases=(Pitch,))
        # int-values --> pitch class
        if isinstance(value, numbers.Number):
            if is_pitch_class is False:
                raise ValueError(f"Initialisation with integer (value={value}) implies pitch class "
                                 f"but 'is_pitch_class' was explicitly set to {is_pitch_class}")
            value = [value, 0]
            is_pitch_class = True
        # pre-process value
        if isinstance(value, str):
            str_value = value
            # extract pitch class, modifiers, and octave
            match = SpelledPitch.name_regex.match(value)
            if match is None:
                raise ValueError(f"{value} does not match the regular expression for spelled pitch names "
                                 f"'{SpelledPitch.name_regex.pattern}'.")
            # initialise value with diatonic pitch class
            value = np.array([SpelledPitch._diatonic_fifth_steps[match['class']], 0])
            # add modifiers
            if "#" in match['modifiers']:
                value[0] += 7 * len(match['modifiers'])
            else:
                value[0] -= 7 * len(match['modifiers'])
            # add octave
            if match['octave'] == "":
                if is_pitch_class is None:
                    is_pitch_class = True
                else:
                    if not is_pitch_class:
                        raise ValueError(f"Inconsistent arguments: {str_value} indicates a pitch class but "
                                         f"'is_pitch_class' is {is_pitch_class}")
            else:
                if is_pitch_class is None:
                    is_pitch_class = False
                else:
                    if is_pitch_class:
                        raise ValueError(f"Inconsistent arguments: {str_value} does not indicate a pitch class but "
                                         f"'is_pitch_class' is {is_pitch_class}")
                value[1] += int(match['octave'])
        elif isinstance(value, (np.ndarray, list, tuple)):
            int_value = np.array(value, dtype=np.int)
            if not np.array_equal(int_value, value):
                raise ValueError(f"Expected integer values but got {value}")
            value = int_value
        # hand on initialisation to other base classes
        super().__init__(value=value, is_pitch_class=is_pitch_class, *args, **kwargs)

    def __repr__(self):
        pitch_class = ["F", "C", "G", "D", "A", "E", "B"][(self._value[0] + 1) % 7]
        sharp_flat = (self._value[0] + 1) // 7
        pitch_class += ('#' if sharp_flat > 0 else 'b') * abs(sharp_flat)
        if self.is_pitch_class():
            return pitch_class
        else:
            return pitch_class + str(self._value[1])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return tuple(self._value) == tuple(other._value)
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__) and self.is_pitch_class() and other.is_pitch_class():
            return self._value[0] < other._value[0]
        else:
            return NotImplemented

    def __hash__(self):
        return hash(tuple(self._value))

    def __int__(self):
        if self.is_pitch_class():
            return int(self._value[0])
        else:
            raise NotImplementedError

    def fifth_steps(self):
        return self._value[0]

    def octave(self):
        return self._value[1]

    def freq(self):
        raise NotImplementedError
        # return 2 ** ((self._value - 69) / 12) * 440


@SpelledPitch.associate_interval_type()
class SpelledPitchInterval(Interval):

    @classmethod
    def _map_to_interval_class(cls, value):
        return np.array([value[0], 0])

    def __init__(self, value, is_interval_class=None, *args, **kwargs):
        Pitch._check_type(value, types=(numbers.Number, np.ndarray, list, tuple), bases=(Interval,))
        # int-values --> interval class
        if isinstance(value, numbers.Number):
            if is_interval_class is False:
                raise ValueError(f"Initialisation with integer (value={value}) implies interval class "
                                 f"but 'is_interval_class' was explicitly set to {is_interval_class}")
            value = [value, 0]
            is_interval_class = True
        int_value = np.array(value, dtype=np.int)
        if not np.array_equal(int_value, value):
            raise ValueError(f"Expected integer values but got {value}")
        super().__init__(value=int_value, is_interval_class=is_interval_class, *args, **kwargs)

    def __repr__(self):
        return self.name()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return tuple(self._value) == tuple(other._value)
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__) and self.is_interval_class() and other.is_interval_class():
            return self._value[0] < other._value[0]
        else:
            return NotImplemented

    def __hash__(self):
        return hash(tuple(self._value))

    def __int__(self):
        if self.is_interval_class():
            return int(self._value[0])
        else:
            raise NotImplementedError

    def __abs__(self):
        if self.is_interval_class():
            return abs(self._value[0])
        else:
            raise NotImplementedError

    def name(self, negative=False):
        if negative:
            delta = -self._value[0]
            sign = "-"
        else:
            delta = self._value[0]
            sign = ""
        phase = delta % 7
        period = (5 - delta) // 7
        generic_interval = ["1", "5", "2", "6", "3", "7", "4"][phase]
        if abs(delta) <= 1:
            quality = "P"
        elif abs(delta) <= 5:
            if delta > 0:
                quality = "M"
            else:
                quality = "m"
        elif period > 0:
            quality = "d" * period
        elif period < 0:
            quality = "A" * abs(period)
        else:
            raise RuntimeWarning("This is a bug!")
        if self.is_interval_class():
            return sign + quality + generic_interval
        else:
            octave = self._value[1]
            octave_sign = "-" if octave < 0 else "+"
            return sign + quality + generic_interval + octave_sign + str(abs(octave))


class EnharmonicPitch(Pitch):

    _base_names_sharp = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    _base_names_flat = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    _pitch_class_origin = 60
    _pitch_class_period = 12

    @staticmethod
    def convert_from_SpelledPitch(spelled_pitch):
        fifth_steps_from_f = spelled_pitch.fifth_steps() + 1
        # base pitch
        base_pitch = ((fifth_steps_from_f % 7 - 1) * 7) % 12
        # chromatic semitone steps
        if fifth_steps_from_f >= 0:
            accidentals = fifth_steps_from_f // 7
        else:
            # note: floor divide rounds down (for negative numbers that is equal to the remainder of division minus one)
            accidentals = fifth_steps_from_f // 7
        return EnharmonicPitch(value=12 * (spelled_pitch.octave() + 1) + base_pitch + accidentals,
                               is_pitch_class=spelled_pitch.is_pitch_class())

    def __init__(self, value, *args, is_pitch_class=None, expect_int=True, **kwargs):
        Pitch._check_type(value, types=(str, numbers.Number), bases=(Pitch,))
        # pre-process value
        if isinstance(value, str):
            value = SpelledPitch(value=value, is_pitch_class=is_pitch_class)
        elif isinstance(value, numbers.Number) and expect_int:
            int_value = int(value)
            if int_value != value:
                raise ValueError(f"Expected integer pitch value but got {value}")
            value = int_value
        # hand on initialisation to other base classes
        super().__init__(value=value, is_pitch_class=is_pitch_class, *args, **kwargs)

    def __int__(self):
        return self._value

    def __repr__(self):
        return self.name()

    def octave(self):
        return self._value // 12 - 1

    def freq(self):
        return 2 ** ((self._value - 69) / 12) * 440

    def fifth_steps(self, sharp_flat=None):
        pitch_class = int(self.to_pitch_class())
        if pitch_class % 2 == 0:
            fifth_steps = pitch_class
        else:
            fifth_steps = (pitch_class + 6) % 12
        if sharp_flat is None:
            if fifth_steps > 6:
                fifth_steps -= 12
        elif sharp_flat == "sharp":
            pass
        elif sharp_flat == "flat":
            fifth_steps %= -12
        else:
            raise ValueError(f"parameter 'sharp_flat' must be one of {['sharp', 'flat', None]}")
        return fifth_steps

    def name(self, sharp_flat=None):
        if sharp_flat is None:
            sharp_flat = "sharp"
        if sharp_flat == "sharp":
            base_names = self._base_names_sharp
        elif sharp_flat == "flat":
            base_names = self._base_names_flat
        else:
            raise ValueError("parameter 'sharp_flat' must be one of ['sharp', 'flat']")
        pc = base_names[self._value % 12]
        if self.is_pitch_class():
            return pc
        else:
            return pc + str(self.octave())


Pitch.register_converter(from_type=SpelledPitch,
                         to_type=EnharmonicPitch,
                         conv_func=EnharmonicPitch.convert_from_SpelledPitch,
                         create_implicit_converters=False)


@EnharmonicPitch.associate_interval_type()
class EnharmonicPitchInterval(Interval):

    def __init__(self, value, *args, **kwargs):
        Pitch._check_type(value, types=(numbers.Number,), bases=(Interval,))
        super().__init__(value=value, *args, **kwargs)

    def __int__(self):
        return int(self._value)


class LogFreqPitch(Pitch):
    """
    Represents a pitch in continuous frequency space with the frequency value stored in log representation.
    """

    _pitch_class_origin = np.log(1)
    _pitch_class_period = np.log(2)

    _print_precision = 2

    @classmethod
    def print_precision(cls, precision=None):
        if precision is not None:
            cls._print_precision = precision
        return cls._print_precision

    @staticmethod
    def convert_from_midi_pitch(midi_pitch):
        return LogFreqPitch(midi_pitch.freq(), is_freq=True, is_pitch_class=midi_pitch.is_pitch_class())

    def __init__(self, value, is_freq=False, *args, **kwargs):
        """
        Initialise from frequency or log-frequency value.
        :param value: frequency or log-frequency (default) value
        :param is_freq: whether value is frequency or log-frequency
        """
        Pitch._check_type(value, types=(numbers.Number,), bases=(Pitch,))
        if is_freq:
            value = np.log(value)
        super().__init__(value=value, *args, **kwargs)

    def freq(self):
        return np.exp(self._value)

    def __float__(self):
        return float(self._value)

    def __repr__(self):
        return f"{np.format_float_positional(self.freq(), fractional=True, precision=self._print_precision)}Hz"


Pitch.register_converter(from_type=EnharmonicPitch,
                         to_type=LogFreqPitch,
                         conv_func=LogFreqPitch.convert_from_midi_pitch,
                         create_implicit_converters=False)


@LogFreqPitch.associate_interval_type()
class LogFreqPitchInterval(Interval):
    """
    Represents an interval in continuous frequency space. An interval corresponds to a frequency ratio and is stored as
    a log-frequency difference.
    """

    def __init__(self, value, is_freq_ratio=False, *args, **kwargs):
        """
        Initialise from frequency ratio or log-frequency difference.
        :param value: frequency ratio or log-frequency difference (default)
        :param is_freq_ratio: whether value is a frequency ratio or log-frequency difference
        """
        Pitch._check_type(value, types=(numbers.Number,), bases=(Interval,))
        if is_freq_ratio:
            value = np.log(value)
        super().__init__(value=value, *args, **kwargs)

    def ratio(self):
        return np.exp(self._value)

    def __float__(self):
        return float(self._value)

    def __repr__(self):
        return f"{np.format_float_positional(self.ratio(), fractional=True, precision=LogFreqPitch._print_precision)}"


def linspace(start, stop, num=50, endpoint=True, retstep=False):
    step = (stop - start) / (num - int(endpoint))
    ret = [start + n * step for n in range(num)]
    if retstep:
        return ret, step
    else:
        return ret


def prange(start, stop, step=None, *, endpoint=False):
    if step is None:
        if isinstance(stop - start, Interval):
            step = (stop - start).__class__(1, is_interval_class=start.is_pitch_class())
        else:
            step = 1
    negative_step = step < (start - start)
    running = start
    while True:
        if not endpoint and running == stop:
            break
        if negative_step and running < stop:
            break
        if not negative_step and running > stop:
            break
        yield running
        running = running + step
