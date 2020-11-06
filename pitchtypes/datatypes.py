#  Copyright (c) 2020 Robert Lieck
import re
import numpy as np
import numbers
from functools import total_ordering
from typing import Any


class Object:
    """
    This class provides an intermediate layer between 'object' and AbstractBase class to allow for freezing
    AbstractBase but still set attributes in the __init__ method.
    """
    pass


class AbstractBase(Object):

    @staticmethod
    def set_func_attr(sub_type, flags, names, funcs):
        for flag, name, func in zip(flags, names, funcs):
            if flag or flag is None and name not in vars(sub_type):
                setattr(sub_type, name, func)

    @staticmethod
    def name_check(cls, sub_type, suffix, skip_name_check):
        if not skip_name_check:
            got_name = sub_type.__name__
            expected_name = cls.__name__ + suffix
            if got_name != expected_name:
                raise TypeError(f"Got class named {got_name}, but expected {expected_name}. "
                                f"Use skip_name_check=True to suppress.")

    @classmethod
    def link_pitch_type(cls,
                        skip_name_check=False,
                        create_init=None,
                        create_add=None,
                        create_sub=None):
        def decorator(sub_type):
            # link types
            cls.Pitch = sub_type
            sub_type._base_type = cls

            # create default functions
            def __init__(self, value, **kwargs):
                super(sub_type, self).__init__(value=value, is_pitch=True, is_class=False, **kwargs)

            def __add__(self, other):
                if type(other) == self.Interval:
                    return self.Pitch(self.value + other.value)
                return NotImplemented

            def __sub__(self, other):
                if type(other) == self.Pitch:
                    return self.Interval(self.value - other.value)
                elif type(other) == self.Interval:
                    return self.Pitch(self.value - other.value)
                return NotImplemented

            # set default functions
            AbstractBase.set_func_attr(sub_type,
                                       [create_init, create_add, create_sub],
                                       ['__init__', '__add__', '__sub__'],
                                       [__init__, __add__, __sub__])

            # check name
            AbstractBase.name_check(cls, sub_type, "Pitch", skip_name_check)

            return sub_type
        return decorator

    @classmethod
    def link_interval_type(cls,
                           skip_name_check=False,
                           create_init=None,
                           create_add=None,
                           create_sub=None,
                           create_mul=None,
                           create_div=None):
        def decorator(sub_type):
            # link types
            cls.Interval = sub_type
            sub_type._base_type = cls

            # create default functions
            def __init__(self, value, **kwargs):
                super(sub_type, self).__init__(value=value, is_pitch=False, is_class=False, **kwargs)

            def __add__(self, other):
                if type(other) == self.Interval:
                    return self.Interval(self.value + other.value)
                return NotImplemented

            def __sub__(self, other):
                if type(other) == self.Interval:
                    return self.Interval(self.value - other.value)
                return NotImplemented

            def __mul__(self, other):
                return sub_type(self.value * other)

            def __rmul__(self, other):
                return self.__mul__(other)

            def __truediv__(self, other):
                return self.__mul__(1 / other)

            # set default functions
            AbstractBase.set_func_attr(sub_type,
                                       [create_init, create_add, create_sub, create_mul, create_mul, create_div],
                                       ['__init__', '__add__', '__sub__', '__mul__', '__rmul__', '__truediv__'],
                                       [__init__, __add__, __sub__, __mul__, __rmul__, __truediv__])

            # perform name check
            AbstractBase.name_check(cls, sub_type, "Interval", skip_name_check)

            return sub_type
        return decorator

    @classmethod
    def link_pitch_class_type(cls,
                              skip_name_check=False,
                              create_init=None,
                              create_add=None,
                              create_sub=None):
        def decorator(sub_type):
            # link types
            cls.PitchClass = sub_type
            sub_type._base_type = cls

            # create default functions
            def __init__(self, value, **kwargs):
                super(sub_type, self).__init__(value=value, is_pitch=True, is_class=True, **kwargs)

            def __add__(self, other):
                if type(other) == self.IntervalClass:
                    return self.PitchClass(self.value + other.value)
                return NotImplemented

            def __sub__(self, other):
                if type(other) == self.PitchClass:
                    return self.IntervalClass(self.value - other.value)
                elif type(other) == self.IntervalClass:
                    return self.PitchClass(self.value - other.value)
                return NotImplemented

            # set default functions
            AbstractBase.set_func_attr(sub_type,
                                       [create_init, create_add, create_sub],
                                       ['__init__', '__add__', '__sub__'],
                                       [__init__, __add__, __sub__])

            # check name
            AbstractBase.name_check(cls, sub_type, "PitchClass", skip_name_check)

            return sub_type
        return decorator

    @classmethod
    def link_interval_class_type(cls,
                                 skip_name_check=False,
                                 create_init=None,
                                 create_add=None,
                                 create_sub=None,
                                 create_mul=None,
                                 create_div=None):
        def decorator(sub_type):
            # link types
            cls.IntervalClass = sub_type
            sub_type._base_type = cls

            # create default functions
            def __init__(self, value, **kwargs):
                super(sub_type, self).__init__(value=value, is_pitch=False, is_class=True, **kwargs)

            def __add__(self, other):
                if type(other) == self.IntervalClass:
                    return self.IntervalClass(self.value + other.value)
                return NotImplemented

            def __sub__(self, other):
                if type(other) == self.IntervalClass:
                    return self.IntervalClass(self.value - other.value)
                return NotImplemented

            def __mul__(self, other):
                return self.IntervalClass(self.value * other)

            def __rmul__(self, other):
                return self.__mul__(other)

            def __truediv__(self, other):
                return self.__mul__(1 / other)

            # set default functions
            AbstractBase.set_func_attr(sub_type,
                                       [create_init, create_add, create_sub, create_mul, create_mul, create_div],
                                       ['__init__', '__add__', '__sub__', '__mul__', '__rmul__', '__truediv__'],
                                       [__init__, __add__, __sub__, __mul__, __rmul__, __truediv__])

            # perform name check
            AbstractBase.name_check(cls, sub_type, "IntervalClass", skip_name_check)

            return sub_type
        return decorator

    @staticmethod
    def create_subtypes():
        def decorator(cls):
            # for the four Pitch/Interval(Class) types:
            # 1) create a class
            # 2) name it appropriately
            # 3) link to base class

            # Pitch
            class Pitch(cls):
                pass
            Pitch.__name__ = cls.__name__ + "Pitch"
            cls.link_pitch_type()(Pitch)

            # Interval
            class Interval(cls):
                pass
            Interval.__name__ = cls.__name__ + "Interval"
            cls.link_interval_type()(Interval)

            # PitchClass
            class PitchClass(cls):
                pass
            PitchClass.__name__ = cls.__name__ + "PitchClass"
            cls.link_pitch_class_type()(PitchClass)

            # IntervalClass
            class IntervalClass(cls):
                pass
            IntervalClass.__name__ = cls.__name__ + "IntervalClass"
            cls.link_interval_class_type()(IntervalClass)

            # return the class (which now has the linked sub-types)
            return cls
        return decorator

    # type hints for class attributes set below
    is_pitch: bool
    is_interval: bool
    is_class: bool
    value: Any

    def __init__(self, value, is_pitch, is_class, **kwargs):
        # call __init__ on super to be cooperative in multi-inheritance,
        # otherwise this should just call object.__init__ and **kwargs should be empty
        super().__init__(**kwargs)
        # initialise values (use Object's __setattr__ because the class is frozen)
        self.setattr('is_pitch', is_pitch)
        self.setattr('is_interval', not is_pitch)
        self.setattr('is_class', is_class)
        self.setattr('value', value)

    def setattr(self, name, value):
        """
        Set an attribute to the frozen class. This should only be used in the __init__ method. As the attributes are
        set indirectly via Object, you should additionally provide type hints in the class definition to let type
        checkers and IDE know of these attributes.
        :param name: name of the attribute
        :param value: value of the attribute
        """
        super(Object, self).__setattr__(name, value)

    def __setattr__(self, key, value):
        raise AttributeError("Class is frozen, attributes cannot be set")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"

    def __eq__(self, other):
        if type(other) == type(self):
            assert self.is_pitch == other.is_pitch
            assert self.is_class == other.is_class
            if isinstance(self.value, np.ndarray) or isinstance(other.value, np.ndarray):
                return np.array_equal(self.value, other.value)
            else:
                return self.value == other.value
        return False

    def __hash__(self):
        return hash((self.__class__.__name__, self.value, self.is_pitch, self.is_class))

    def convert_to(self, other_type):
        return Converters.convert(self, other_type)


class Harmonic(AbstractBase):

    @staticmethod
    def parse_exponents(exponents):
        if isinstance(exponents, str):
            # remove all whitespace
            exponents_ = "".join(exponents.split())
            # assert starts and ends with '[' and ']' respectively
            if not (exponents_.startswith("[") and exponents_.endswith("]")):
                raise ValueError(f"'exponents' has to start and end with '[' and ']', respectively")
            try:
                exponents = np.array(exponents_[1:-1].split(','), dtype=np.int)
            except ValueError as e:
                raise ValueError(f"Could not interpret {exponents} as array of integers: {e}")
        else:
            exponents = np.array(exponents, dtype=np.int)
        return exponents

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@Harmonic.link_interval_type()
class HarmonicInterval(Harmonic):
    def __init__(self, exponents):
        super().__init__(value=self.parse_exponents(exponents=exponents),
                         is_pitch=False,
                         is_class=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self.value)})"

    def to_class(self):
        return self.IntervalClass(exponents=self.value[1:].copy())


@Harmonic.link_interval_class_type()
class HarmonicIntervalClass(Harmonic):
    def __init__(self, exponents):
        super().__init__(value=self.parse_exponents(exponents=exponents),
                         is_pitch=False,
                         is_class=True)

    def __repr__(self):
        return f"{self.__class__.__name__}({[None] + list(self.value)})"


class Spelled(AbstractBase):

    _pitch_regex = re.compile("^(?P<class>[A-G])(?P<modifiers>(b*)|(#*))(?P<octave>(-?[0-9]+)?)$")
    _interval_regex = re.compile("^(?P<sign>[-+])(?P<quality>(A*)|(M)|(P)|(m)|(d*))(?P<generic>[1-7])(?P<octave>(:-?[0-9]+)?)$")

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

    def __init__(self, value, is_pitch, is_class, **kwargs):
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
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)

    def __repr__(self):
        return self.name()

    def __hash__(self):
        return hash((self.__class__.__name__, self.value[0], self.value[1], self.is_pitch, self.is_class))

    def convert_to_enharmonic(self):
        fifth_steps_from_f = self.fifth_steps() + 1
        # base pitch
        base_pitch = ((fifth_steps_from_f % 7 - 1) * 7) % 12
        # chromatic semitone steps
        if fifth_steps_from_f >= 0:
            accidentals = fifth_steps_from_f // 7
        else:
            # note: floor divide rounds down (for negative numbers that is equal to the remainder of division minus one)
            accidentals = fifth_steps_from_f // 7
        if self.is_pitch:
            if self.is_class:
                return EnharmonicPitchClass(value=12 * (self.octave() + 1) + base_pitch + accidentals)
            else:
                return EnharmonicPitch(value=12 * (self.octave() + 1) + base_pitch + accidentals)
        else:
            if self.is_class:
                return EnharmonicIntervalClass(value=12 * (self.octave() + 1) + base_pitch + accidentals)
            else:
                return EnharmonicInterval(value=12 * (self.octave() + 1) + base_pitch + accidentals)

    def to_class(self):
        if self.is_class:
            raise TypeError("Is already class.")
        return self.__class__(value=np.array([self.value[0], 0]), is_pitch=self.is_pitch, is_class=True)

    def name(self, negative=None):
        if self.is_pitch:
            if negative is not None:
                raise ValueError("specifying parameter 'negative' is only valid for interval class types")
            pitch_class = ["F", "C", "G", "D", "A", "E", "B"][(self.value[0] + 1) % 7]
            flat_sharp = (self.value[0] + 1) // 7
            pitch_class += ('#' if flat_sharp > 0 else 'b') * abs(flat_sharp)
            if self.is_class:
                return pitch_class
            else:
                return pitch_class + str(self.value[1])
        else:
            if self.is_class:
                if negative is None:
                    negative = False
            else:
                if negative is None:
                    negative = self.value[1] < 0
                else:
                    raise ValueError("specifying parameter 'negative' is only valid for interval class types")
            if negative:
                delta = -self.value[0]
                sign = "-"
            else:
                delta = self.value[0]
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
            if self.is_class:
                return sign + quality + generic_interval
            else:
                return sign + quality + generic_interval + ":" + str(abs(self.value[1]))

    def fifth_steps(self):
        return self.value[0]

    def octave(self):
        return self.value[1]


@Spelled.link_pitch_type()
class SpelledPitch(Spelled):
    pass


@Spelled.link_interval_type()
class SpelledInterval(Spelled):
    pass


@Spelled.link_pitch_class_type()
@total_ordering
class SpelledPitchClass(Spelled):
    def __lt__(self, other):
        """Spelled pitch classes are ordered along the line of fifths."""
        if type(other) == SpelledPitchClass:
            return self.value < other.value
        return NotImplemented


@Spelled.link_interval_class_type()
class SpelledIntervalClass(Spelled):
    def __abs__(self):
        """Absolute value of steps along the line of fifths"""
        return abs(self.value)

    def __lt__(self, other):
        """Spelled interval classes are ordered along the line of fifths."""
        if type(other) == SpelledIntervalClass:
            return self.value < other.value
        return NotImplemented


class Enharmonic(AbstractBase):

    @classmethod
    def print_options(cls, as_int=None, flat_sharp=None):
        cls.Pitch.print_options(as_int=as_int, flat_sharp=flat_sharp)
        cls.PitchClass.print_options(as_int=as_int, flat_sharp=flat_sharp)

    def __init__(self, value, is_pitch, is_class, **kwargs):
        # pre-process value
        if isinstance(value, str):
            if is_pitch:
                if is_class:
                    value = SpelledPitchClass(value=value).convert_to(EnharmonicPitchClass).value
                else:
                    value = SpelledPitch(value=value).convert_to(EnharmonicPitch).value
            else:
                if is_class:
                    value = SpelledIntervalClass(value=value).convert_to(EnharmonicIntervalClass).value
                else:
                    value = SpelledInterval(value=value).convert_to(EnharmonicInterval).value
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
        if self.is_pitch:
            if self.is_class:
                return LogFreqPitchClass(self.freq(), is_freq=True)
            else:
                return LogFreqPitch(self.freq(), is_freq=True)
        else:
            if self.is_class:
                return LogFreqIntervalClass(self.freq(), is_freq=True)
            else:
                return LogFreqInterval(self.freq(), is_freq=True)

    def to_class(self):
        if self.is_class:
            raise TypeError("Is already class.")
        if self.is_pitch:
            return self.PitchClass(value=self.value % 12)
        else:
            return self.IntervalClass(value=self.value % 12)

    def __int__(self):
        return self.value

    def __repr__(self):
        return self.name()

    def octave(self):
        return self.value // 12 - 1

    def freq(self):
        return 2 ** ((self.value - 69) / 12) * 440

    def fifth_steps(self, flat_sharp=None):
        pitch_class = int(self.to_class())
        if pitch_class % 2 == 0:
            fifth_steps = pitch_class
        else:
            fifth_steps = (pitch_class + 6) % 12
        if flat_sharp is None:
            if fifth_steps > 6:
                fifth_steps -= 12
        elif flat_sharp == "sharp":
            pass
        elif flat_sharp == "flat":
            fifth_steps %= -12
        else:
            raise ValueError(f"parameter 'flat_sharp' must be one of {['sharp', 'flat', None]}")
        return fifth_steps

    def name(self, as_int=None, flat_sharp=None):
        if self.is_pitch:
            if flat_sharp is None:
                flat_sharp = "sharp"
            if as_int is None:
                as_int = False
            if as_int:
                return str(self.value)
            if flat_sharp == "sharp":
                base_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            elif flat_sharp == "flat":
                base_names = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
            else:
                raise ValueError("parameter 'flat_sharp' must be one of ['sharp', 'flat']")
            pc = base_names[self.value % 12]
            if self.is_class:
                return pc
            else:
                return pc + str(self.octave())
        else:
            if flat_sharp is not None:
                raise ValueError(f"parameter 'flat_sharp' can only be used for pitch types and should be None for "
                                 f"interval types (is {flat_sharp})")
            sign = "-" if self.value < 0 else "+"
            return sign + str(abs(self.value))

@Enharmonic.link_pitch_type()
class EnharmonicPitch(Enharmonic):

    # how should Pitch and PitchClass types be printed
    _print_as_int = False
    _print_flat_sharp = 'sharp'

    @classmethod
    def print_options(cls, as_int=None, flat_sharp=None):
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

    def name(self, as_int=None, flat_sharp=None):
        if as_int is None:
            as_int = self._print_as_int
        if flat_sharp is None:
            flat_sharp = self._print_flat_sharp
        return super().name(as_int=as_int, flat_sharp=flat_sharp)

    @property
    def midi(self):
        return self.value


@Enharmonic.link_interval_type()
class EnharmonicInterval(Enharmonic):
    pass


@Enharmonic.link_pitch_class_type()
class EnharmonicPitchClass(Enharmonic):

    # how should Pitch and PitchClass types be printed
    _print_as_int = False
    _print_flat_sharp = 'sharp'

    @classmethod
    def print_options(cls, as_int=None, flat_sharp=None):
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

    def name(self, as_int=None, flat_sharp=None):
        if as_int is None:
            as_int = self._print_as_int
        if flat_sharp is None:
            flat_sharp = self._print_flat_sharp
        return super().name(as_int=as_int, flat_sharp=flat_sharp)


@Enharmonic.link_interval_class_type()
class EnharmonicIntervalClass(Enharmonic):
    pass


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

    def __init__(self, value, is_pitch, is_class, is_freq=False, **kwargs):
        """
        Initialise from frequency or log-frequency value.
        :param value: frequency or log-frequency (default) value
        :param is_freq: whether value is frequency or log-frequency
        """
        if is_freq:
            value = np.log(value)
        else:
            value = float(value)
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)

    def to_class(self):
        if self.is_class:
            raise TypeError("Is already class.")
        return self.__class__(value=self.value % np.log(2), is_pitch=self.is_pitch, is_class=True)

    def freq(self):
        if self.is_pitch:
            return np.exp(self.value)
        else:
            raise NotImplementedError

    def __float__(self):
        return float(self.value)

    def __repr__(self):
        s = f"{np.format_float_positional(self.freq(), fractional=True, precision=self._print_precision)}"
        if self.is_pitch:
            s += "Hz"
        return s


@LogFreq.link_pitch_type()
class LogFreqPitch(LogFreq):
    pass


@LogFreq.link_interval_type()
class LogFreqInterval(LogFreq):
    pass


@LogFreq.link_pitch_class_type()
class LogFreqPitchClass(LogFreq):
    pass


@LogFreq.link_interval_class_type()
class LogFreqIntervalClass(LogFreq):
    pass


class Converters:

    # store converters for classes derived from Pitch;
    # it's a dict of dicts, so that _converters[A][B] returns is a list of functions that, when executed
    # successively, converts A to B
    _converters = {}

    @staticmethod
    def convert(obj, to_type):
        # skip self-conversion
        if type(obj) == to_type:
            ret = obj
        else:
            # use conversion pipeline starting with the object itself
            ret = obj
            # sequentially apply converters from pipeline
            for converter in Converters.get_converter(type(obj), to_type):
                ret = converter(ret)
        # checks
        assert isinstance(ret, to_type), f"Conversion failed, expected type {to_type} but got {type(ret)}"
        assert obj.is_pitch == ret.is_pitch, f"{obj.is_pitch} {ret.is_pitch}"
        assert obj.is_class == ret.is_class, f"{obj.is_class} {ret.is_class}"
        return ret

    @staticmethod
    def get_converter(from_type, to_type=None):
        # return dedicated converter if other_type was specified or list of existing converters otherwise
        if to_type is not None:
            all_converters = Converters.get_converter(from_type)
            try:
                return all_converters[to_type]
            except KeyError:
                raise NotImplementedError(f"Type '{from_type}' does not have any converter registered for type "
                                          f"'{to_type}'")
        else:
            try:
                return Converters._converters[from_type]
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
        if from_type not in Converters._converters:
            Converters._converters[from_type] = {}
        # get existing converters from from_type to to_type and decide whether to set new converter
        set_new_converter = False
        try:
            converter = Converters.get_converter(from_type, to_type)
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
            Converters._converters[from_type][to_type] = [conv_func]
        # extend implicit converters
        if create_implicit_converters:
            for another_from_type, other_converters in Converters._converters.items():
                # remember new converters to not change dict while iterating over it
                new_converters = []
                for another_to_type, converter_pipeline in other_converters.items():
                    # trying to prepend this converter [from_type --> to_type == another_from_type --> another_to_type]
                    if to_type == another_from_type:
                        # don't add implicit self-converters
                        if from_type == another_to_type:
                            continue
                        # get existing converters from_type --> ???
                        converters = Converters.get_converter(from_type)
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


Converters.register_converter(from_type=Spelled.Pitch,
                              to_type=Enharmonic.Pitch,
                              conv_func=lambda spelled: spelled.convert_to_enharmonic())
Converters.register_converter(from_type=Spelled.Interval,
                              to_type=Enharmonic.Interval,
                              conv_func=lambda spelled: spelled.convert_to_enharmonic())
Converters.register_converter(from_type=Spelled.PitchClass,
                              to_type=Enharmonic.PitchClass,
                              conv_func=lambda spelled: spelled.convert_to_enharmonic())
Converters.register_converter(from_type=Spelled.IntervalClass,
                              to_type=Enharmonic.IntervalClass,
                              conv_func=lambda spelled: spelled.convert_to_enharmonic())

Converters.register_converter(from_type=Enharmonic.Pitch,
                              to_type=LogFreq.Pitch,
                              conv_func=lambda enharmonic: enharmonic.convert_to_logfreq())
Converters.register_converter(from_type=Enharmonic.Interval,
                              to_type=LogFreq.Interval,
                              conv_func=lambda enharmonic: enharmonic.convert_to_logfreq())
Converters.register_converter(from_type=Enharmonic.PitchClass,
                              to_type=LogFreq.PitchClass,
                              conv_func=lambda enharmonic: enharmonic.convert_to_logfreq())
Converters.register_converter(from_type=Enharmonic.IntervalClass,
                              to_type=LogFreq.IntervalClass,
                              conv_func=lambda enharmonic: enharmonic.convert_to_logfreq())
