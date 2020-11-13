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
                        create_sub=None,
                        create_to_class=None):
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

            def to_class(self):
                return self.PitchClass(self.value)

            # set default functions
            AbstractBase.set_func_attr(sub_type,
                                       [create_init, create_add, create_sub, create_to_class],
                                       ['__init__', '__add__', '__sub__', 'to_class'],
                                       [__init__, __add__, __sub__, to_class])

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
                           create_div=None,
                           create_neg=None,
                           create_to_class=None):
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

            def __neg__(self):
                return -1 * self

            def to_class(self):
                return self.IntervalClass(self.value)

            # set default functions
            AbstractBase.set_func_attr(
                sub_type,
                [create_init, create_add, create_sub, create_mul, create_mul, create_div, create_neg, create_to_class],
                ['__init__', '__add__', '__sub__', '__mul__', '__rmul__', '__truediv__', '__neg__', 'to_class'],
                [__init__, __add__, __sub__, __mul__, __rmul__, __truediv__, __neg__, to_class]
            )

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
                                 create_div=None,
                                 create_neg=None):
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

            def __neg__(self):
                return -1 * self

            # set default functions
            AbstractBase.set_func_attr(
                sub_type,
                [create_init, create_add, create_sub, create_mul, create_mul, create_div, create_neg],
                ['__init__', '__add__', '__sub__', '__mul__', '__rmul__', '__truediv__', '__neg__'],
                [__init__, __add__, __sub__, __mul__, __rmul__, __truediv__, __neg__]
            )

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
        if isinstance(self.value, np.ndarray):
            assert self.value.flags.writeable is False
            return hash((self.__class__.__name__, self.value.data.tobytes(), self.is_pitch, self.is_class))
        else:
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
    _interval_regex = re.compile("^(?P<sign>[-+])?(?P<quality>(a+)|(M)|(p)|(m)|(d+))(?P<generic>[1-7])(?P<octave>(:[0-9]+)?)$")

    @staticmethod
    def parse_pitch(s):
        """
        Parse a string as a spelled pitch or spelled pitch class. Returns a tuple (octave, fifths), where octave
        indicates the octave the pitch lies in (None for spelled pitch classes) and fifths indicates the steps taken
        along the line of fifths.
        :param s: string to parse
        :return: (octave, fifths)
        """
        if not isinstance(s, str):
            raise TypeError(f"expected string as input, got {s}")
        pitch_match = Spelled._pitch_regex.match(s)
        if pitch_match is None:
            raise ValueError(f"could not match '{s}' with regex: '{Spelled._pitch_regex.pattern}'")
        octave = pitch_match['octave']
        # initialise fifth steps from diatonic pitch class
        fifth_steps = Spelled.fifths_from_diatonic_pitch_class(pitch_match['class'])
        # add modifiers
        if "#" in pitch_match['modifiers']:
            fifth_steps += 7 * len(pitch_match['modifiers'])
        else:
            fifth_steps -= 7 * len(pitch_match['modifiers'])
        # add octave
        if octave == "":
            return None, fifth_steps
        else:
            return int(octave), fifth_steps

    @staticmethod
    def parse_interval(s):
        """
        Parse a string as a spelled interval or spelled interval class. Returns a tuple (sign, octave, fifths), where
        sign is +1 or -1 and indicates the sign given in the string (no sign means positive), octave indicates the
        number of full octave steps (in positive or negative direction; None for spelled interval classes), and fifths
        indicates the steps taken along the line of fifths (i.e. not actual fifth steps that would add to the octaves).
        :param s: string to parse
        :return: (sign, octave, fifths)
        """
        if not isinstance(s, str):
            raise TypeError("expecte string as input, got {s}")
        interval_match = Spelled._interval_regex.match(s)
        if interval_match is None:
            raise ValueError(f"could not match '{s}' with regex: '{Spelled._interval_regex.pattern}'")
        # initialise value with generic interval classes
        fifth_steps = Spelled.fifths_from_generic_interval_class(int(interval_match['generic']))
        # add modifiers
        if interval_match['quality'] in ["p", "M"]:
            pass
        elif interval_match['quality'] == "m":
            fifth_steps -= 7
        elif "a" in interval_match['quality']:
            fifth_steps += 7 * len(interval_match['quality'])
        elif "d" in interval_match['quality']:
            if interval_match['generic'] in ["4", "1", "5"]:
                fifth_steps -= 7 * len(interval_match['quality'])
            else:
                fifth_steps -= 7 * (len(interval_match['quality']) + 1)
        else:
            raise RuntimeError(f"Initialization from string failed: "
                               f"Unexpected interval quality '{interval_match['quality']}'. This is a bug and "
                               f"means that either the used regex is bad or the handling code.")
        # get octave
        if interval_match['octave'][1:] == "":
            octave = None
        else:
            octave = int(interval_match['octave'][1:])
        # get sign and bring adapt fifth steps
        if interval_match['sign'] == '-':
            sign = -1
        else:
            sign = 1
        return sign, octave, fifth_steps

    @staticmethod
    def pitch_class_from_fifths(fifth_steps):
        """
        Return the pitch class given the number of steps along the line of fifths
        :param fifth_steps: number of steps along the line of fifths
        :return: pitch class (e.g. C, Bb, F##, Abbb etc.)
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
        """
        if -5 <= fifth_steps <= 5:
            quality = ['m', 'm', 'm', 'm', 'p', 'p', 'p', 'M', 'M', 'M', 'M'][fifth_steps + 5]
        elif fifth_steps > 5:
            quality = 'a' * ((fifth_steps + 1) // 7)
        else:
            quality = 'd' * ((-fifth_steps + 1) // 7)
        return quality

    @staticmethod
    def diatonic_steps_from_fifths(fifth_steps):
        """
        Return the number of diatonic steps corresponding to the number of steps on the line of fifths
        (`4 * fifth_steps`).
        :param fifth_steps: number of fifth steps
        :return: number of diatonic steps
        """
        return 4 * fifth_steps

    @staticmethod
    def generic_interval_class_from_fifths(fifth_steps):
        """
        Return the generic interval class corresponding to the given number of fifths. This corresponds to the number of
        diatonic steps plus one. The generic interval also corresponds to the scale degree when interpreted as the tone
        reached when starting from the tonic.
        :param fifth_steps: number of fifth steps
        :return: scale degree (integer in 1,...,7)
        """
        return Spelled.diatonic_steps_from_fifths(fifth_steps) % 7 + 1

    @staticmethod
    def interval_class_from_fifths(fifths, inverse=False):
        """
        Return the interval class corresponding to the given number of steps along the line of fifths. This function
        combines Spelled.interval_quality_from_fifths and Spelled.generic_interval_class_from_fifths. Specifying
        inverse=True (default is False) returns the inverse interval class (m2 for M7, aa4 for dd5 etc.).
        :param fifths: number of fifth steps
        :param inverse: whether to return the inverse interval class
        :return: interval class (p1, M3, aa6 etc.)
        """
        if inverse:
            fifths = -fifths
        return f"{Spelled.interval_quality_from_fifths(fifths)}" \
               f"{Spelled.generic_interval_class_from_fifths(fifths)}"

    @staticmethod
    def fifths_from_diatonic_pitch_class(pitch_class):
        """
        Return the number of steps along the line of fifths corresponding to a diatonic pitch class.
        :param pitch_class: a diatonic pitch class; character in A, B, C, D, E, F, G
        :return: fifth steps; an integer in -1, 0, ... 5
        """
        pitch_classes = "ABCDEFG"
        if pitch_class not in pitch_classes:
            pitch_classes = "', '".join(pitch_classes)
            raise ValueError(f"diatonic pitch class must be one of '{pitch_classes}', but got {pitch_class}")
        return {"F": -1, "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5}[pitch_class]

    @staticmethod
    def fifths_from_generic_interval_class(generic):
        """
        Return the number of steps along the line of fifths corresponding to the given generic interval:
        (2 * generic - 1) % 7 - 1.
        :param generic: generic interval (integer in 1,...,7)
        :return: fifth steps (integer in -1, 0, ..., 5)
        """
        if not isinstance(generic, numbers.Integral) or not (1 <= generic <= 7):
            raise ValueError(f"generic interval must be an integer between 1 and 7 (incl.), got {generic}")
        return (2 * generic - 1) % 7 - 1

    def __init__(self, value, is_pitch, is_class, **kwargs):
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)
        if not is_class:
            self.value.flags.writeable = False

    def __repr__(self):
        return self.name()

    def convert_to_enharmonic(self):
        fifth_steps_from_f = self.fifth_steps() + 1
        # get the base pitch in 0,...,11
        base_pitch = ((fifth_steps_from_f % 7 - 1) * 7) % 12
        # get the accidental, i.e. chromatic semitone steps to add to base pitch
        # (floor-divide (//) rounds down, for negative numbers that is equal to the remainder of division minus one)
        accidentals = fifth_steps_from_f // 7
        if self.is_pitch:
            if self.is_class:
                return EnharmonicPitchClass(value=base_pitch + accidentals)
            else:
                return EnharmonicPitch(value=12 * (self.octave() + 1) + base_pitch + accidentals)
        else:
            if self.is_class:
                return EnharmonicIntervalClass(value=base_pitch + accidentals)
            else:
                return EnharmonicInterval(value=12 * (self.octave() + 1) + base_pitch + accidentals)

    def name(self):
        raise NotImplementedError

    def fifth_steps(self):
        raise NotImplementedError


@Spelled.link_pitch_type()
class SpelledPitch(Spelled):
    def __init__(self, value):
        if isinstance(value, str):
            octaves, fifths = self.parse_pitch(value)
            assert isinstance(octaves, numbers.Integral)
            assert isinstance(fifths, numbers.Integral)
            # correct for octaves taken by fifth steps
            octaves -= Spelled.diatonic_steps_from_fifths(fifths) // 7
            value = np.array([octaves, fifths])
        else:
            octaves, fifths = value
            assert isinstance(octaves, numbers.Integral)
            assert isinstance(fifths, numbers.Integral)
            value = np.array([octaves, fifths])
        assert isinstance(fifths, numbers.Integral)
        assert isinstance(octaves, numbers.Integral)
        super().__init__(value=value, is_pitch=True, is_class=False)

    def octave(self):
        return self.value[0] + self.diatonic_steps_from_fifths(self.fifth_steps()) // 7

    def fifth_steps(self):
        return self.value[1]

    def to_class(self):
        return self.PitchClass(self.fifth_steps())

    def name(self):
        return f"{self.pitch_class_from_fifths(self.fifth_steps())}{self.octave()}"


@Spelled.link_interval_type()
class SpelledInterval(Spelled):
    def __init__(self, value):
        if isinstance(value, str):
            sign, octaves, fifths = self.parse_interval(value)
            assert isinstance(sign, numbers.Integral)
            assert isinstance(octaves, numbers.Integral)
            assert isinstance(fifths, numbers.Integral)
            assert abs(sign) == 1
            assert octaves >= 0
            # correct octaves from fifth steps
            octaves -= Spelled.diatonic_steps_from_fifths(fifths) // 7
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

    def diatonic_steps(self):
        return self.diatonic_steps_from_fifths(self.fifth_steps())

    def octave(self):
        return self.value[0] + self.diatonic_steps() // 7

    def fifth_steps(self):
        return self.value[1]

    def sign(self):
        if self.octave() < 0:
            # if the octave is strictly positive the sign is positive
            return -1
        elif self.octave() > 0:
            # if the octave is strictly negative the sign is negative
            return 1
        else:
            # if the octave is zero the sign depends on the fifth steps
            if self.diatonic_steps() % 7 != 0:
                # for anything other than unisons the sign is positive
                return 1
            else:
                if self.fifth_steps() == 0:
                    # for a perfect unison the sign is zero (neutral element of addition)
                    return 0
                elif self.fifth_steps() < 0:
                    # for diminished unisons the sign is negative
                    return -1
                else:
                    # for augmented unisons the sign is positive
                    return 1

    def to_class(self):
        return self.IntervalClass(self.value[1])

    def name(self):
        octave = abs(self.octave())
        if self.sign() == -1:
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
        return sign + self.interval_class_from_fifths(self.fifth_steps(), inverse=inverse) + f":{octave}"


@Spelled.link_pitch_class_type()
class SpelledPitchClass(Spelled):
    def __init__(self, value):
        if isinstance(value, str):
            octaves, fifths = self.parse_pitch(value)
            assert octaves is None
        else:
            fifths = value
        assert isinstance(fifths, numbers.Integral)
        super().__init__(value=fifths, is_pitch=True, is_class=True)

    def fifth_steps(self):
        return self.value

    def name(self):
        return self.pitch_class_from_fifths(self.fifth_steps())


@Spelled.link_interval_class_type()
class SpelledIntervalClass(Spelled):
    def __init__(self, value):
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

    def fifth_steps(self):
        return self.value

    def name(self, inverse=False):
        if inverse:
            sign = "-"
        else:
            sign = ""
        return sign + self.interval_class_from_fifths(self.fifth_steps(), inverse=inverse)


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
                raise ValueError("'flat_sharp' has to be one of ['sharp', 'flat']")
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
            raise ValueError("parameter 'flat_sharp' must be one of ['sharp', 'flat']")
        return base_names[midi_pitch % 12]

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
                return LogFreqIntervalClass(self.freq(), is_ratio=True)
            else:
                return LogFreqInterval(self.freq(), is_ratio=True)

    def __int__(self):
        return self.value

    def __repr__(self):
        return self.name()

    def name(self, *args, **kwargs):
        raise NotImplementedError

    def octave(self):
        return self.value // 12 - 1

    def freq(self):
        return 2 ** ((self.value - 69) / 12) * 440


@Enharmonic.link_pitch_type()
class EnharmonicPitch(Enharmonic):

    def to_class(self):
        return self.PitchClass(value=self.value % 12)

    def name(self, as_int=None, flat_sharp=None):
        if as_int is None:
            as_int = self._print_as_int
        if flat_sharp is None:
            flat_sharp = self._print_flat_sharp
        if as_int:
            return str(self.value)
        return self.pitch_class_name_from_midi(self.value, flat_sharp=flat_sharp) + str(self.octave())

    @property
    def midi(self):
        return self.value


@Enharmonic.link_interval_type()
class EnharmonicInterval(Enharmonic):
    def to_class(self):
        return self.IntervalClass(value=self.value % 12)

    def name(self):
        sign = "-" if self.value < 0 else "+"
        return sign + str(abs(self.value))


@Enharmonic.link_pitch_class_type()
class EnharmonicPitchClass(Enharmonic):

    def name(self, as_int=None, flat_sharp=None):
        if as_int is None:
            as_int = self._print_as_int
        if flat_sharp is None:
            flat_sharp = self._print_flat_sharp
        if as_int:
            return str(self.value)
        return self.pitch_class_name_from_midi(self.value, flat_sharp=flat_sharp)


@Enharmonic.link_interval_class_type()
class EnharmonicIntervalClass(Enharmonic):
    def name(self):
        sign = "-" if self.value < 0 else "+"
        return sign + str(abs(self.value))


class LogFreq(AbstractBase):
    """
    Represents a pitches and intervals in continuous frequency space with the frequency value stored in log
    representation.
    """

    _print_precision = 2

    @classmethod
    def print_precision(cls, precision=None):
        if precision is not None:
            if not isinstance(precision, numbers.Integral):
                raise ValueError(f"precision has to be an integer, got {precision}")
            if cls == LogFreq:
                for sub_cls in [LogFreq.Pitch, LogFreq.Interval, LogFreq.PitchClass, LogFreq.IntervalClass]:
                    sub_cls.print_precision(precision)
            cls._print_precision = precision
        return cls._print_precision

    def __init__(self, value, is_pitch, is_class, is_log=True, **kwargs):
        """
        Initialise from frequency or log-frequency value.
        :param value: frequency or log-frequency (default) value
        :param is_log: whether value is frequency or log-frequency
        """
        if is_log:
            value = float(value)
        else:
            value = np.log(value)
        super().__init__(value=value, is_pitch=is_pitch, is_class=is_class, **kwargs)

    def __float__(self):
        return float(self.value)


@LogFreq.link_pitch_type()
class LogFreqPitch(LogFreq):
    def __init__(self, value, is_freq=True, **kwargs):
        super().__init__(value, is_pitch=True, is_class=False, is_log=not is_freq, **kwargs)

    def __repr__(self):
        return f"{np.format_float_positional(self.freq(), fractional=True, precision=self._print_precision)}Hz"

    def to_class(self):
        return self.PitchClass(self.value, is_freq=False)

    def freq(self):
        return np.exp(self.value)


@LogFreq.link_interval_type()
class LogFreqInterval(LogFreq):
    def __init__(self, value, is_ratio=True, **kwargs):
        super().__init__(value, is_pitch=False, is_class=False, is_log=not is_ratio, **kwargs)

    def __repr__(self):
        return f"{np.format_float_positional(self.ratio(), fractional=True, precision=self._print_precision)}"

    def to_class(self):
        return self.IntervalClass(self.value, is_ratio=False)

    def ratio(self):
        return np.exp(self.value)


@LogFreq.link_pitch_class_type()
class LogFreqPitchClass(LogFreq):
    def __init__(self, value, is_freq=True, **kwargs):
        if is_freq:
            value = np.log(value)
        else:
            value = float(value)
        value %= np.log(2)
        super().__init__(value, is_pitch=True, is_class=True, is_log=True, **kwargs)

    def __repr__(self):
        return f"{np.format_float_positional(self.freq(), fractional=True, precision=self._print_precision)}Hz"

    def freq(self):
        return np.exp(self.value)


@LogFreq.link_interval_class_type()
class LogFreqIntervalClass(LogFreq):
    def __init__(self, value, is_ratio=True, **kwargs):
        if is_ratio:
            value = np.log(value)
        else:
            value = float(value)
        value %= np.log(2)
        super().__init__(value, is_pitch=False, is_class=True, is_log=True, **kwargs)

    def __repr__(self):
        return f"{np.format_float_positional(self.ratio(), fractional=True, precision=self._print_precision)}"

    def ratio(self):
        return np.exp(self.value)


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
                           overwrite_implicit_converters=False,
                           create_implicit_converters=False):
        """
        Register a converter from from_type to other type. The converter function should be function taking as its
        single argument an from_type object and returning an other_type object.
        :param to_type: other type derived from AbstractBase, which the converter function converts to
        :param conv_func: converter function from from_type to other_type
        :param overwrite_explicit_converters: can be True, False, or None (default); if True and there exists an
        explicit converter (i.e. the list of converter functions is of length 1), replace it by this converter function;
        if False raise a ValueError if an explicit converter exists
        :param overwrite_implicit_converters: if there exists an implicit converter (i.e. the list of converter functions
        is of length greater than 1) replace it by this converter function
        :param create_implicit_converters: if there is an (explicit or implicit) converter from type X to type
        from_type, add an implicit converter from type X to other_type by extending the list of converter functions from
        X to from_type by this converter function; if there already exists an (explicit or implicit) converter from X to
        other_type, it will not be overwritten
        """
        # not self-conversion
        if from_type == to_type:
            raise TypeError(f"Not allowed to add converters from a type to itself (from: {from_type}, to: {to_type})")
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
                if overwrite_implicit_converters:
                    set_new_converter = True
                else:
                    raise ValueError("An implicit converter already exists. Set overwrite_implicit_converters=True to "
                                     "overwrite.")
        # set the new converter
        if set_new_converter:
            Converters._converters[from_type][to_type] = [conv_func]
        # extend implicit converters
        if create_implicit_converters:
            for another_from_type, other_converters in Converters._converters.items():
                # remember new converters to not change dict while iterating over it
                new_converters = []
                for another_to_type, converter_pipeline in other_converters.items():
                    # trying to prepend this converter (but don't add implicit self-converters)
                    # from_type --> another_to_type := (from_type --> to_type) + (another_from_type --> another_to_type)
                    if to_type == another_from_type and from_type != another_to_type:
                        # get existing converters from_type --> ???
                        converters = Converters.get_converter(from_type)
                        # add the extended converter if one does not exist
                        if another_to_type not in converters:
                            converters[another_to_type] = [conv_func] + converter_pipeline
                    # try to append this converter (but don't add implicit self-converters)
                    # another_from_type --> to_type := (another_from_type --> another_to_type) + ( from_type --> to_type)
                    if another_to_type == from_type and another_from_type != to_type:
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
