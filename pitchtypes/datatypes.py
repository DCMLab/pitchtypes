import re
import numpy as np
import numbers
from functools import total_ordering

@total_ordering
class AbstractBase:

    # store converters for classes derived from Pitch;
    # it's a dict of dicts, so that _converters[A][B] returns is a list of functions that, when executed
    # successively, converts A to B
    _converters = {}

    @staticmethod
    def _is_derived_from_abstract_base(object, object_is_type=False):
        if object_is_type:
            return AbstractBase in object.__mro__
        else:
            return AbstractBase in object.__class__.__mro__

    @staticmethod
    def _convert(value, to_type):
        AbstractBase._is_derived_from_abstract_base(value)
        AbstractBase._is_derived_from_abstract_base(to_type, object_is_type=True)
        if to_type == value.__class__:
            # skip self-conversion
            return value
        else:
            # use conversion pipeline
            ret = value
            for converter in AbstractBase.get_converter(value.__class__, to_type):
                ret = converter(ret)
            # checks
            assert isinstance(ret, to_type), f"Conversion failed, expected type {to_type} but got {type(ret)}"
            assert value.is_pitch() == ret.is_pitch(), f"{value.is_pitch()} {ret.is_pitch()}"
            assert value.is_class() == ret.is_class(), f"{value.is_class()} {ret.is_class()}"
            return ret

    @staticmethod
    def get_converter(from_type, to_type=None):
        # return dedicated converter if other_type was specified or list of existing converters otherwise
        if to_type is not None:
            all_converters = AbstractBase.get_converter(from_type)
            try:
                return all_converters[to_type]
            except KeyError:
                raise NotImplementedError(f"Type '{from_type}' does not have any converter registered for type "
                                          f"'{to_type}'")
        else:
            try:
                return AbstractBase._converters[from_type]
            except KeyError:
                raise NotImplementedError(f"There are no converters registered for type '{from_type}'")

    @staticmethod
    def register_converter(from_type, to_type, conv_func,
                           overwrite_explicit_converters=False,
                           overwrite_implicit_converter=False,
                           create_implicit_converters=False):
        """
        Register a converter from from_type to other type. The converter function should be function taking as its
        single argument an from_type object and returning an other_type object.
        :param to_type: other type derived from AbstractBase, which the converter function converts to
        :param conv_func: converter function from from_type to other_type
        :param overwrite_explicit_converters: can be True, False, or None (default); if True and there exists an
        explicit converter (i.e. the list of converter functions is of length 1), replace it by this converter function;
        if False raise a ValueError if an explicit converter exists
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
        if from_type not in AbstractBase._converters:
            AbstractBase._converters[from_type] = {}
        # get existing converters from from_type to to_type and decide whether to set new converter
        set_new_converter = False
        try:
            converter = AbstractBase.get_converter(from_type, to_type)
        except NotImplementedError:
            # no existing converters
            set_new_converter = True
        else:
            # implicit or explicit converter are already registered
            if len(converter) == 1:
                # explicit converter
                if overwrite_explicit_converters:
                    set_new_converter = True
                else:
                    raise ValueError("An explicit converter already exists. Set overwrite_explicit_converters=True to "
                                     "overwrite.")
            else:
                # implicit converter
                if overwrite_implicit_converter:
                    set_new_converter = True
        # set the new converter
        if set_new_converter:
            AbstractBase._converters[from_type][to_type] = [conv_func]
        # extend implicit converters
        if create_implicit_converters:
            for another_from_type, other_converters in AbstractBase._converters.items():
                # remember new converters to not change dict while iterating over it
                new_converters = []
                for another_to_type, converter_pipeline in other_converters.items():
                    # trying to prepend this converter [from_type --> to_type == another_from_type --> another_to_type]
                    if to_type == another_from_type:
                        # don't add implicit self-converters
                        if from_type == another_to_type:
                            continue
                        # get existing converters from_type --> ???
                        converters = AbstractBase.get_converter(from_type)
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

    def __init__(self, value, is_pitch=None, is_class=None, *args, **kwargs):
        # if value is derived from AbstractBase, try to convert to this type and get the _value
        if AbstractBase._is_derived_from_abstract_base(value):
            if is_class is not None and is_class != value.is_class():
                raise ValueError(f"Class property of provided value ({value.is_class()}) conflicts with explicitly "
                                 f"provided value ({is_class}).")
            is_class = value.is_class()
            if is_pitch is not None and is_pitch != value.is_pitch():
                raise ValueError(f"Pitch/Interval property of provided value ({value.is_pitch()}) conflicts with "
                                 f"explicitly provided value ({is_pitch}).")
            is_pitch = value.is_pitch()
            value = value.convert_to(self.__class__)._value  ## ToDo: this should be returned by using __new__
        # make sure is_pitch and is_class are set
        if is_pitch is None or is_class is None:
            raise ValueError("is_pitch and is_class parameter have to be set when initialising from value")
        # call __init__ on super to be cooperative in multi-inheritance,
        # otherwise this should just call object.__init__ and *args and **kwargs should be empty
        super().__init__(*args, **kwargs)
        # initialise values
        self._is_pitch = is_pitch
        self._is_class = is_class
        self._value = value

    def is_class(self):
        return self._is_class

    def to_class(self):
        if self.is_class():
            raise TypeError("Cannot convert to class type, is already class type.")
        return self.__class__(value=self._value, is_pitch=self.is_pitch(), is_class=True)

    def is_pitch(self):
        return self._is_pitch

    def to_pitch(self):
        if self.is_pitch():
            raise TypeError("Is already pitch.")
        return self.__class__(value=self._value, is_pitch=True, is_class=self.is_class())

    def is_interval(self):
        return not self._is_pitch

    def to_interval(self):
        if self.is_interval():
            raise TypeError("Is already interval.")
        return self.__class__(value=self._value, is_pitch=False, is_class=self.is_class())

    def _create_pitch(self, value):
        return self.__class__(value=value, is_pitch=True, is_class=self.is_class())

    def _create_interval(self, value):
        return self.__class__(value=value, is_pitch=False, is_class=self.is_class())

    def _is_pitch_of_same_type(self, other, do_raise=False, message=False):
        if do_raise and message:
            raise ValueError("Cannot do both raise a TypeError and return a message")
        if not isinstance(other, self.__class__):
            msg = f"Object is not of correct type (expected {self.__class__}, got {type(other)}"
            if do_raise:
                raise TypeError(msg)
            elif message:
                return msg
            else:
                return False
        if not other.is_pitch():
            msg = f"Object is not a pitch ({other}; type {type(other)})"
            if do_raise:
                raise TypeError(msg)
            elif message:
                return msg
            else:
                return False
        if self.is_class() != other.is_class():
            msg = f"Class mismatch (this: {self.is_class()}, other: {other.is_class()})"
            if do_raise:
                raise TypeError(msg)
            elif message:
                return msg
            else:
                return False
        if message:
            return ""
        else:
            return True

    def _is_interval_of_same_type(self, other, do_raise=False, message=False):
        if do_raise and message:
            raise ValueError("Cannot do both raise a TypeError and return a message")
        if not isinstance(other, self.__class__):
            msg = f"Object is not of correct type (expected {self.__class__}, got {type(other)}"
            if do_raise:
                raise TypeError(msg)
            elif message:
                return msg
            else:
                return False
        if not other.is_interval():
            msg = f"Object is not an interval ({other}; type {type(other)})"
            if do_raise:
                raise TypeError(msg)
            elif message:
                return msg
            else:
                return False
        if self.is_class() != other.is_class():
            msg = f"Mismatch in class property (this: {self.is_class()}, other: {other.is_class()})"
            if do_raise:
                raise TypeError(msg)
            elif message:
                return msg
            else:
                return False
        if message:
            return ""
        else:
            return True

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"{'Pitch' if self.is_pitch() else 'Interval'}" \
               f"{'Class' if self.is_class() else ''}" \
               f"({self._value})"

    def __sub__(self, other):
        if self.is_pitch():
            if self._is_pitch_of_same_type(other):
                return self._create_interval(self._value - other._value)
            elif self._is_interval_of_same_type(other):
                return self._create_pitch(self._value - other._value)
            else:
                raise TypeError(f"Expected pitch or interval of same type. Got the following error messages:\n"
                                f"    is not pitch of same type: "
                                f"{self._is_pitch_of_same_type(other, message=True)}\n"
                                f"    is not interval of same type: "
                                f"{self._is_interval_of_same_type(other, message=True)}")
        elif self.is_interval():
            if self._is_interval_of_same_type(other):
                return self._create_interval(self._value - other._value)
            else:
                self._is_interval_of_same_type(other, do_raise=True)
        else:
            raise NotImplementedError("This type is neither pitch nor interval")

    def __add__(self, other):
        if self.is_pitch():
            if self._is_interval_of_same_type(other):
                return self._create_pitch(self._value + other._value)
            else:
                raise TypeError("Cannot add a pitch to a pitch (second one must be an interval)")
        elif self.is_interval():
            if self._is_interval_of_same_type(other):
                return self._create_interval(self._value + other._value)
            else:
                raise TypeError("Cannot add a pitch to an interval (second one must be an interval)")
        else:
            raise NotImplementedError("This type is neither pitch nor interval")

    def __eq__(self, other):
        if self.is_pitch():
            if self._is_pitch_of_same_type(other):
                return self._value == other._value
            else:
                return NotImplemented
        elif self.is_interval():
            if self._is_interval_of_same_type(other):
                return self._value == other._value
            else:
                return NotImplemented
        else:
            raise NotImplementedError("This type is neither pitch nor interval")

    def __hash__(self):
        return hash((self._value, self._is_pitch, self._is_class))

    def __lt__(self, other):
        if self.is_class():
            # cyclic order
            return NotImplemented
        elif self.is_pitch():
            if self._is_pitch_of_same_type(other):
                return self._value < other._value
            else:
                return NotImplemented
        elif self.is_interval():
            if self._is_interval_of_same_type(other):
                return self._value < other._value
            else:
                return NotImplemented
        else:
            raise NotImplementedError("This type is neither pitch nor interval")

    def __mul__(self, other):
        if self.is_interval():
            return self._create_interval(self._value * other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if self.is_interval():
            return self.__mul__(1 / other)
        else:
            return NotImplemented

    def __abs__(self):
        if self.is_interval() and self.is_class():
            return abs(self._value)
        else:
            raise NotImplementedError

    def convert_to(self, other_type):
        AbstractBase._is_derived_from_abstract_base(other_type, object_is_type=True)
        return AbstractBase._convert(self, other_type)



class Spelled(AbstractBase):

    _pitch_regex = re.compile("^(?P<class>[A-G])(?P<modifiers>(b*)|(#*))(?P<octave>(-?[0-9]+)?)$")

    # ToDo: regex includes "P3", "m5" etc which are invalid values --> change that
    _interval_regex = re.compile("^(?P<sign>[-+])(?P<quality>(A*)|(M)|(P)|(m)|(d*))(?P<generic>[1-7])(?P<octave>(:-?[0-9]+)?)$")

    def to_class(self):
        if self.is_class():
            raise TypeError("Is already class.")
        return self.__class__(value=np.array([self._value[0], 0]), is_pitch=self.is_pitch(), is_class=True)

    @staticmethod
    def _init_from_int(value, is_pitch, is_class):
        try:
            int_value = int(value)
            float_value = float(value)
            if int_value != float_value:
                raise ValueError(f"Initialization from integer failed: Interpreting the provided value of {value} as "
                                 f"integer ({int_value}) differs from its interpretation as float ({float_value})")
            value = np.array([int(value), 0], dtype=np.int)
        except TypeError:
            raise ValueError(f"Initialization from integer failed: Could not inteprete {value} as integer")
        if is_class is False:
            raise TypeError(f"Initialization from integer failed: Only pitch and interval classes can be initialised "
                            f"from an integer value but is_class={is_class} was provided.")
        if is_pitch is None:
            raise ValueError(f"Initialization from integer failed: For initialisation from an integer, please "
                             f"explicitly provide the is_pitch argument as True or False.")
        return value, is_pitch, True

    @staticmethod
    def _init_from_str(value, is_pitch, is_class):
        if not isinstance(value, str):
            raise TypeError(f"Initialization from string failed: Value is not a string (got {value} of type "
                            f"{type(value)})")
        str_value = value
        pitch_match = Spelled._pitch_regex.match(value)
        interval_match = Spelled._interval_regex.match(value)
        if pitch_match is None and interval_match is None:
            raise ValueError(f"Initialization from string failed: "
                             f"{value} does neither match the regular expression for spelled pitch names "
                             f"'{Spelled._pitch_regex.pattern}' nor that for spelled interval names "
                             f"'{Spelled._interval_regex.pattern}'.")
        if pitch_match is not None and interval_match is not None:
            raise ValueError(f"Initialization from string failed: "
                             f"{value} matches both the regular expression for spelled pitch names "
                             f"'{Spelled._pitch_regex.pattern}' and that for spelled interval names "
                             f"'{Spelled._interval_regex.pattern}'. This is a bug (the two regex expressions should "
                             f"be disjoint).")
        octave = None
        if pitch_match is not None:
            if is_pitch is False:
                raise ValueError(f"Initialization from string failed: "
                                 f"{value} matches the regular expression for spelled pitch names "
                                 f"({Spelled._pitch_regex.pattern}) but is_pitch was explicitly specified as "
                                 f"{is_pitch}")
            octave = pitch_match['octave']
            is_pitch = True
            # initialise value with diatonic pitch class
            value = np.array([{"F": -1, "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5}[pitch_match['class']], 0])
            # add modifiers
            if "#" in pitch_match['modifiers']:
                value[0] += 7 * len(pitch_match['modifiers'])
            else:
                value[0] -= 7 * len(pitch_match['modifiers'])
        if interval_match is not None:
            if is_pitch is True:
                raise ValueError(f"Initialization from string failed: "
                                 f"{value} matches the regular expression for spelled interval names "
                                 f"({Spelled._interval_regex.pattern}) but is_pitch was explicitly specified as "
                                 f"{is_pitch}")
            octave = interval_match['octave'][1:]
            is_pitch = False
            # initialise value with generic interval classes
            value = np.array([{"4": -1, "1": 0, "5": 1, "2": 2, "6": 3, "3": 4, "7": 5}[interval_match['generic']], 0])
            # add modifiers
            if interval_match['quality'] in ["P", "M"]:
                pass
            elif interval_match['quality'] == "m":
                value[0] -= 7
            elif "A" in interval_match['quality']:
                value[0] += 7 * len(interval_match['quality'])
            elif "d" in interval_match['quality']:
                if interval_match['generic'] in ["4", "1", "5"]:
                    value[0] -= 7 * len(interval_match['quality'])
                else:
                    value[0] -= 7 * (len(interval_match['quality']) + 1)
            else:
                raise RuntimeError(f"Initialization from string failed: "
                                   f"Unexpected interval quality '{interval_match['quality']}'. This is a bug and "
                                   f"means that either the used regex is bad or the handling code.")
            if interval_match['sign'] == '-':
                value[0] *= -1
        # add octave
        if octave == "":
            if is_class is None:
                is_class = True
            else:
                if not is_class:
                    raise ValueError(f"Initialization from string failed: "
                                     f"Inconsistent arguments: {str_value} indicates a pitch class but "
                                     f"'is_class' is {is_class}")
        else:
            if is_class is None:
                is_class = False
            else:
                if is_class:
                    raise ValueError(f"Initialization from string failed: "
                                     f"Inconsistent arguments: {str_value} does not indicate a pitch class but "
                                     f"'is_class' is {is_class}")
            value[1] += int(octave)
        return value, is_pitch, is_class

    @staticmethod
    def _init_from_listlike(value, is_pitch, is_class):
        int_value = np.array(value, dtype=np.int)
        if not np.array_equal(int_value, value):
            raise ValueError(f"Initialization from list-like failed: "
                             f"Expected integer values but got {value}")
        if len(int_value) == 1:
            if not is_class:
                raise ValueError(f"Initialization from list-like failed: "
                                 f"Got a single value ({value}), which requires class type, but is_class={is_class} "
                                 f"was explicitly provided")
            int_value = np.array([int_value[0], 0], dtype=np.int)
            is_class = True
        elif len(int_value) == 2:
            if is_class:
                int_value = np.array([int_value[0], 0], dtype=np.int)
            else:
                is_class = False
        else:
            raise ValueError(f"Initialization from list-like failed: "
                             f"Got wrong number of values: {value}")
        if is_pitch is None:
            raise ValueError(f"Initialization from list-like failed: "
                             f"For initialisation from an integer(s), please explicitly provide the is_pitch argument "
                             f"as True or False.")
        return int_value, is_pitch, is_class

    def __init__(self, value, *, is_pitch=None, is_class=None, **kwargs):
        if not AbstractBase._is_derived_from_abstract_base(value):
            exceptions = []
            for f in [Spelled._init_from_int,
                      Spelled._init_from_str,
                      Spelled._init_from_listlike]:
                try:
                    value, is_pitch, is_class = f(value=value, is_pitch=is_pitch, is_class=is_class)
                except (ValueError, TypeError) as ex:
                    exceptions.append(ex)
                    continue
                break
            else:
                ex_list = '\n'.join([f"    {type(ex).__name__}: {ex}" for ex in exceptions])
                raise ValueError(f"Could not initialise with provided parameters (value={value}, is_pitch={is_pitch}, "
                                 f"is_class={is_class}). Different attempts resulted in the following exceptions being "
                                 f"raised:\n{ex_list}")
            assert is_pitch is not None
            assert is_class is not None
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)

    def __repr__(self):
        return self.name()

    def __eq__(self, other):
        if self.is_pitch():
            if self._is_pitch_of_same_type(other):
                return tuple(self._value) == tuple(other._value)
            else:
                return NotImplemented
        elif self.is_interval():
            if self._is_interval_of_same_type(other):
                return tuple(self._value) == tuple(other._value)
            else:
                return NotImplemented
        else:
            raise NotImplementedError("This type is neither pitch nor interval")

    def __lt__(self, other):
        if self.is_class():
            # cyclic order
            return NotImplemented
        elif self.is_pitch():
            if self._is_pitch_of_same_type(other):
                return self._value[0] < other._value[0]
            else:
                return NotImplemented
        elif self.is_interval():
            if self._is_interval_of_same_type(other):
                return self._value[0] < other._value[0]
            else:
                return NotImplemented
        else:
            raise NotImplementedError("This type is neither pitch nor interval")

    def __hash__(self):
        return hash((self._value[0], self._value[1], self._is_pitch, self._is_class))

    def __abs__(self):
        if self.is_interval() and self.is_class():
            return abs(self._value[0])
        else:
            raise NotImplementedError

    def name(self, negative=None):
        if self.is_pitch():
            if negative is not None:
                raise ValueError("specifying parameter 'negative' is only valid for interval class types")
            pitch_class = ["F", "C", "G", "D", "A", "E", "B"][(self._value[0] + 1) % 7]
            sharp_flat = (self._value[0] + 1) // 7
            pitch_class += ('#' if sharp_flat > 0 else 'b') * abs(sharp_flat)
            if self.is_class():
                return pitch_class
            else:
                return pitch_class + str(self._value[1])
        elif self.is_interval():
            if self.is_class():
                if negative is None:
                    negative = False
            else:
                if negative is None:
                    negative = self._value[1] < 0
                else:
                    raise ValueError("specifying parameter 'negative' is only valid for interval class types")
            if negative:
                delta = -self._value[0]
                sign = "-"
            else:
                delta = self._value[0]
                sign = "+"
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
                if generic_interval in ["4", "1", "5"]:
                    quality = "d" * period
                else:
                    quality = "d" * (period - 1)
            elif period < 0:
                quality = "A" * abs(period)
            else:
                raise RuntimeWarning("This is a bug!")
            if self.is_class():
                return sign + quality + generic_interval
            else:
                return sign + quality + generic_interval + ":" + str(abs(self._value[1]))

    def fifth_steps(self):
        return self._value[0]

    def octave(self):
        return self._value[1]


class Enharmonic(AbstractBase):

    def __init__(self, value, *, is_pitch=None, is_class=None, **kwargs):
        # pre-process value
        if isinstance(value, str):
            value = Spelled(value=value, is_class=is_class)
            is_pitch = value.is_pitch()
            is_class = value.is_class()
        elif isinstance(value, numbers.Number):
            int_value = int(value)
            if int_value != value:
                raise ValueError(f"Expected integer pitch value but got {value}")
            value = int_value
            if is_pitch is None:
                is_pitch = True
                # raise ValueError(f"is_pitch has to be True or False but is {is_pitch}. "
                #                  f"Did you mean to create a pitch or an interval?")
            if is_class is None:
                is_class = False
            if is_class:
                value = value % 12
                # raise ValueError(f"is_class has to be True or False but is {is_class}. "
                #                  f"Did you mean to create a pitch/interval or pitch/interval CLASS?")
        # hand on initialisation to other base classes
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)

    def to_class(self):
        if self.is_class():
            raise TypeError("Is already class.")
        return self.__class__(value=self._value % 12, is_pitch=self.is_pitch(), is_class=True)

    def __int__(self):
        return self._value

    def __repr__(self):
        return self.name()

    def octave(self):
        return self._value // 12 - 1

    def freq(self):
        return 2 ** ((self._value - 69) / 12) * 440

    def fifth_steps(self, sharp_flat=None):
        pitch_class = int(self.to_class())
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
        if self.is_pitch():
            if sharp_flat is None:
                sharp_flat = "sharp"
            if sharp_flat == "sharp":
                base_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            elif sharp_flat == "flat":
                base_names = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
            else:
                raise ValueError("parameter 'sharp_flat' must be one of ['sharp', 'flat']")
            pc = base_names[self._value % 12]
            if self.is_class():
                return pc
            else:
                return pc + str(self.octave())
        else:
            if sharp_flat is not None:
                raise ValueError(f"parameter 'sharp_flat' can only be used for pitch types and should be None for "
                                 f"interval types (is {sharp_flat})")
            sign = "-" if self._value < 0 else "+"
            return sign + str(abs(self._value))


class LogFreq(AbstractBase):
    """
    Represents a pitches and intervals in continuous frequency space with the frequency value stored in log
    representation.
    """

    _print_precision = 2

    @classmethod
    def print_precision(cls, precision=None):
        if precision is not None:
            cls._print_precision = precision
        return cls._print_precision

    def __init__(self, value, is_freq=False, *, is_pitch=None, is_class=None, **kwargs):
        """
        Initialise from frequency or log-frequency value.
        :param value: frequency or log-frequency (default) value
        :param is_freq: whether value is frequency or log-frequency
        """
        if not AbstractBase._is_derived_from_abstract_base(value):
            if is_freq:
                value = np.log(value)
            else:
                value = float(value)
            if is_pitch is None:
                is_pitch = True
            if is_class is None:
                is_class = False
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)

    def to_class(self):
        if self.is_class():
            raise TypeError("Is already class.")
        return self.__class__(value=self._value % np.log(2), is_pitch=self.is_pitch(), is_class=True)

    def freq(self):
        if self.is_pitch():
            return np.exp(self._value)
        else:
            raise NotImplementedError

    def __float__(self):
        return float(self._value)

    def __repr__(self):
        s = f"{np.format_float_positional(self.freq(), fractional=True, precision=self._print_precision)}"
        if self.is_pitch():
            s += "Hz"
        return s

def convert_spelled_to_enharmonic(spelled):
    if spelled.is_pitch():
        fifth_steps_from_f = spelled.fifth_steps() + 1
        # base pitch
        base_pitch = ((fifth_steps_from_f % 7 - 1) * 7) % 12
        # chromatic semitone steps
        if fifth_steps_from_f >= 0:
            accidentals = fifth_steps_from_f // 7
        else:
            # note: floor divide rounds down (for negative numbers that is equal to the remainder of division minus one)
            accidentals = fifth_steps_from_f // 7
        return Enharmonic(value=12 * (spelled.octave() + 1) + base_pitch + accidentals,
                          is_pitch=spelled.is_pitch(),
                          is_class=spelled.is_class())
    elif spelled.is_interval():
        raise NotImplementedError
    else:
        raise NotImplementedError

AbstractBase.register_converter(from_type=Spelled,
                                to_type=Enharmonic,
                                conv_func=convert_spelled_to_enharmonic)

def convert_enharmonic_to_logfreq(enharmonic):
    return LogFreq(enharmonic.freq(), is_freq=True, is_pitch=enharmonic.is_pitch(), is_class=enharmonic.is_class())

AbstractBase.register_converter(from_type=Enharmonic,
                                to_type=LogFreq,
                                conv_func=convert_enharmonic_to_logfreq)
