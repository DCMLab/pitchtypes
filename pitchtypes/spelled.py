#  Copyright (c) 2021 Robert Lieck

import numbers
import re

import numpy as np

from pitchtypes.basetypes import AbstractBase, Pitch, Interval, Diatonic, Chromatic


class Spelled(AbstractBase):
    """
    A common base class for spelled pitch and interval types.
    See below for a set of common operations.
    """
    _pitch_regex = re.compile("^(?P<class>[A-G])(?P<modifiers>(b*)|(#*))(?P<octave>(-?[0-9]+)?)$")
    _interval_regex = re.compile("^(?P<sign>[-+])?("
                                 "(?P<quality0>P)(?P<generic0>[145])|"          # perfect intervals
                                 "(?P<quality1>|(M)|(m))(?P<generic1>[2367])|"  # imperfect intervals
                                 "(?P<quality2>(a+)|(d+))(?P<generic2>[1-7])"   # augmeted/diminished intervals
                                 ")(?P<octave>(:-?[0-9]+)?)$")

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
        # convert unicode flats and sharps (♭ -> b and ♯ -> #)
        s = s.replace("♭", "b")
        s = s.replace("♯", "#")
        # match with regex
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
        # get quality and generic interval (first corresponding group that is not None)
        for i in range(3):
            g = interval_match[f"generic{i}"]
            q = interval_match[f"quality{i}"]
            if g is not None and q is not None:
                generic = int(g)
                quality = q
                break
        else:
            raise RuntimeError(f"Could not match generic interval and quality, this is a bug in the regex ("
                               f"{[interval_match[f'generic{i}'] for i in range(3)]}, "
                               f"{[interval_match[f'quality{i}'] for i in range(3)]}"
                               f")")
        # initialise value with generic interval classes
        fifth_steps = Spelled.fifths_from_generic_interval_class(generic)
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
            raise RuntimeError(f"Initialization from string failed: "
                               f"Unexpected interval quality '{quality}'. This is a bug and "
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
            quality = ['m', 'm', 'm', 'm', 'P', 'P', 'P', 'M', 'M', 'M', 'M'][fifth_steps + 5]
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
    def _degree_from_fifths_(fifths):
        """
        Return the scale degree of a pitch/interval based on its fifths.
        Helper function for degree()
        """
        return (fifths*4) % 7

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

    def name(self):
        raise NotImplementedError

    # Spelled interface:

    def fifths(self):
        """
        Return the position of the interval on the line of fifths.
        """
        raise NotImplementedError

    def octaves(self):
        """
        For intervals, return the number of octaves the interval spans.
        Negative intervals start with -1, decreasing.
        For pitches, return the absolute octave of the pitch.
        """
        raise NotImplementedError

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
        return self._degree_from_fifths_(self.fifths())

    def generic(self):
        """
        Return the generic interval, i.e. the number of diatonic steps modulo octave.
        Unlike degree(), the result respects the sign of the interval
        (unison=0, 2nd up=1, 2nd down=-1).
        For pitches, use degree().
        """
        raise NotImplementedError

    def diatonic_steps(self):
        """
        Return the diatonic steps of the interval (unison=0, 2nd=1, ..., octave=7, ...).
        Respects both direction and octaves.
        """
        raise NotImplementedError

    def alteration(self):
        """
        Return the number of semitones by which the interval is altered from its the perfect or major variant.
        Positive alteration always indicates augmentation,
        negative alteration indicates diminution (minor or smaller) of the interval.
        For pitches, return the accidentals (positive=sharps, negative=flats, 0=natural).
        """
        raise NotImplementedError


@Spelled.link_pitch_type()
class SpelledPitch(Spelled, Pitch):
    """
    Represents a spelled pitch.

    The constructor takes a string consisting of the form
    <letter><accidentals?><octave>, e.g. "C#4", "E5", or "Db-2".
    Accidentals may be written as ASCII symbols (#/b)
    or with unicode symbols (♯/♭), but not mixed within the same note.
    """
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

    @staticmethod
    def from_fifths_and_octaves(fifths, octaves):
        """
        Create a pitch by directly providing its internal fifths and octaves.

        Each pitch is represented relative to C0
        by moving the specified number of fifths and octaves upwards
        (or downwards for negative values).
        """
        return SpelledPitch((octaves, fifths))

    def interval_from(self, other):
        if type(other) == SpelledPitch:
            octaves1, fifths1 = self.value
            octaves2, fifths2 = other.value
            return SpelledInterval.from_fifths_and_octaves(fifths1-fifths2, octaves1-octaves2)
        else:
            return NotImplemented
    
    def to_class(self):
        return self.PitchClass(self.fifths())

    def name(self):
        return f"{self.pitch_class_from_fifths(self.fifths())}{self.octaves()}"

    # Pitch interface
    def pc(self):
        return self.to_class()

    def embed(self):
        return self

    # Spelled interface

    def fifths(self):
        return self.value[1]

    def octaves(self):
        return self.value[0] + self.diatonic_steps_from_fifths(self.fifths()) // 7

    def internal_octaves(self):
        return self.value[0]

    def generic(self):
        # return self.degree()
        raise NotImplementedError

    def diatonic_steps(self):
        # return (self.fifths() * 4) + (self.internal_octaves() * 7)
        raise NotImplementedError

    def alteration(self):
        return (self.fifths() + 1) // 7

    def letter(self):
        return chr(ord('A') + (self.degree() + 2) % 7)


@Spelled.link_interval_type()
class SpelledInterval(Spelled, Interval, Diatonic, Chromatic):
    """
    Represents a spelled interval.

    The constructor takes a string consisting of the form
    -?<quality><generic-size>:<octaves>,
    e.g. "M6:0", "-m3:0", or "aa2:1",
    which stand for a major sixth, a minor third down, and a double-augmented ninth, respectively.
    possible qualities are d (diminished), m (minor), M (major), P (perfect), and a (augmented),
    where d and a can be repeated.
    """
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

    @staticmethod
    def from_fifths_and_octaves(fifths, octaves):
        """
        Create an interval by directly providing its internal fifths and octaves.
        """
        return SpelledInterval((octaves, fifths))

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

    def to_class(self):
        return self.IntervalClass(self.value[1])

    # interval interface

    @classmethod
    def unison(cls):
        """
        Return a perfect unison (P1:0).
        """
        return cls.from_fifths_and_octaves(0,0)

    @classmethod
    def octave(cls):
        """
        Return a perfect octave (P1:1).
        """
        return cls.from_fifths_and_octaves(0,1)

    def direction(self):
        """
        Return the direction of the interval (1=up / 0=neutral / -1=down).
        All unisons are considered neutral (including augmented and diminished unisons).
        """
        ds = self.diatonic_steps()
        if ds == 0:
            return 0
        elif ds < 0:
            return -1
        else:
            return 1

    def __abs__(self):
        if self.direction() < 0:
            return -self
        else:
            return self

    def ic(self):
        return self.to_class()

    def embed(self):
        return self
    
    @classmethod
    def chromatic_semitone(cls):
        return SpelledInterval.from_fifths_and_octaves(7,-4)

    def is_step(self):
        return abs(self.diatonic_steps()) <= 1

    # spelled interface

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


@Spelled.link_pitch_class_type()
class SpelledPitchClass(Spelled, Pitch):
    """
    Represents a spelled pitch class, i.e. a pitch without octave information.

    The constructor takes a string consisting of the form
    <letter><accidentals?>, e.g. "C#", "E", or "Dbb".
    Accidentals may be written as ASCII symbols (#/b)
    or with unicode symbols (♯/♭), but not mixed within the same note.
    """
    def __init__(self, value):
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
        """
        return SpelledPitchClass(fifths)

    def name(self):
        return self.pitch_class_from_fifths(self.fifths())

    def interval_from(self, other):
        if type(other) == SpelledPitchClass:
            return SpelledIntervalClass.from_fifths(self.value-other.value)
        else:
            return NotImplemented
    
    # pitch interface

    def pc(self):
        return self

    def embed(self):
        return SpelledPitch.from_fifths_and_octaves(self.fifths(), -((self.fifths() * 4) // 7))

    # spelled interface

    def fifths(self):
        return self.value

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
        return chr(ord('A') + (self.degree() + 2) % 7)


@Spelled.link_interval_class_type()
class SpelledIntervalClass(Spelled, Interval, Diatonic, Chromatic):
    """
    Represents a spelled interval class, i.e. an interval without octave information.

    The constructor takes a string consisting of the form
    -?<quality><generic-size>,
    e.g. "M6", "-m3", or "aa2",
    which stand for a major sixth, a minor third down (= major sixth up), and a double-augmented second, respectively.
    possible qualities are d (diminished), m (minor), M (major), P (perfect), and a (augmented),
    where d and a can be repeated.
    """
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

    @staticmethod
    def from_fifths(fifths):
        """
        Create an interval class by directly providing its internal fifths.
        """
        return SpelledIntervalClass(fifths)

    def name(self, inverse=False):
        if inverse:
            sign = "-"
        else:
            sign = ""
        return sign + self.interval_class_from_fifths(self.fifths(), inverse=inverse)

    # interval interface

    @classmethod
    def unison(cls):
        """
        Return a perfect unison (P1).
        """
        return cls.from_fifths(0)

    @classmethod
    def octave(cls):
        """
        Return a perfect unison (P1), which is the same as an octave for interval classes.
        """
        return cls.from_fifths(0)

    def direction(self):
        ds = self.diatonic_steps()
        if ds == 0:
            return 0
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

    @classmethod
    def chromatic_semitone(cls):
        return SpelledIntervalClass.from_fifths(7)

    def is_step(self):
        return self.degree() in [0,1,6]

    # spelled interface

    def fifths(self):
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
