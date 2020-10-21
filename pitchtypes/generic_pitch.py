# Pitch as a wrapper for intervals.
# =================================

# TODOs:
# - converters
# - a more elegant abstraction of string constructors (reduce boilerplate)

import math

# helper for type checking
def assert_type(obj, typ):
    if not isinstance(obj, typ): raise TypeError(f"expected an object of type {typ}, got {type(obj)}")

# A generic class Pitch is used to represent pitches as intervals.
# All pitch-interval arithmetic is defered to the wrapped interval type.
# Special pitch types only implement functionality that is specific to the type, e.g. constructors, printing, etc.

class Pitch():
    _interval_type = NotImplemented
    
    # constructors
    #-------------    
    """Raw constructor that just sets the internal interval."""
    def __init__(self, interval):
        self._interval = interval

    # common methods that always work based on intervals
    # --------------------------------------------------

    def __add__(self, other):
        # check types
        assert type(other) == type(self._interval)
        return self.__class__(self._interval + other)
    # note: implement Interval + Pitch in Interval base class?

    def __sub__(self, other):
        # check types
        if type(other) == type(self._interval):
            # subtract interval -> new pitch
            return self.__class__(self._interval - other)
        elif type(other) == type(self):
            # subtract pitch -> interval between pitches
            return self._interval - other._interval
        else:
            raise TypeError(f"can't subtract a {type(other)} from a {type(self)}")

    def __eq__(self, other):
        return type(self) == type(other) and self._interval == other._interval

    def __hash__(self):
        return hash(self._interval)

    def __lt__(self, other):
        assert type(other) == type(self)
        return self._interval < other._interval

    """Convert to pitch class. (Identity for pitch class types.)"""
    def pc(self):
        return self._interval.ic()._to_pitch()

    """Convert to interval. Returns the internal interval."""
    def _to_interval(self):
        return self._interval

    """Returns True if pitch class, False if not."""
    @classmethod
    def is_class(cls):
        return cls.interval_type().is_class()

    # fallback methods

    def __repr__(self):
        return f"Pitch({self._interval})"

    """Returns the corresponding interval type."""
    @classmethod
    def interval_type(cls):
        return cls._interval_type

    # static method template

    """Turns a string representation into a pitch."""
    @classmethod
    def _parse(cls, string):
        raise NotImplementedError(f"{cls} doesn't implement string parsing.")


# The base classes for intervals and interval classes
# serve as type tags and define an interface.

class Interval():
    """Returns True if interval class, false otherwise."""
    @classmethod
    def is_class(cls):
        # return False by default, override in IntervalClass
        return False

    # interface (besides operator methods such as __add__ etc.)
    
    """
    Turns an interval into a the corresponding pitch type.
    Should only be used internally.
    """
    def _to_pitch(self):
        pass

    """Returns the corresponding interval class."""
    def ic(self):
        pass

    """Returns the unison of this interval type."""
    @staticmethod
    def unison():
        pass

    """Returns the octave of this interval type."""
    @staticmethod
    def octave():
        pass

class IntervalClass(Interval):
    @classmethod
    def is_class(cls):
        return True

    # interface

    def embed(self, octave=0):
        pass

# Specific classes
# ================

# Midi interval / pitch
# ---------------------

class MidiInterval(int, Interval):
    def __repr__(self):
        return "i" + str(int(self))

    def _to_pitch(self):
        return MidiPitch(self)

    def __add__(self, other):
        assert_type(other, int)
        return MidiInterval(int(self) + int(other))

    def __sub__(self, other):
        assert_type(other, int)
        return MidiInterval(int(self) - int(other))

    def ic(self):
        return MidiIC(self)

    """Convert the interval to a 12-TET frequency ratio."""
    def to_freq(self):
        return LogFreqInterval(math.log(2)/12*self)

    @staticmethod
    def unison():
        return MidiInterval(0)

    @staticmethod
    def octave():
        return MidiInterval(12)
    
class MidiPitch(Pitch):
    _interval_type = MidiInterval
    # custom constructor
    def __init__(self, arg):
        if type(arg) == MidiInterval:
            super().__init__(arg)
        elif isinstance(arg, str):
            super().__init__(self._parse(arg)._interval)
        else:
            super().__init__(MidiInterval(arg))
        
    # string parsing
    @classmethod
    def _parse(cls, string):
        if string[0] == "p":
            return MidiPitch(int(string[1:]))
        else:
            raise ValueError("Invalid MidiPitch {string}")

    """Convert to 12-TET frequency."""
    def to_freq(self, tuning=LogFreqPitch(440.), is_log=False):
        if not isinstance(tuning, LogFreqPitch):
            tuning = LogFreqPitch(tuning, is_log)
        return tuning + (self - MidiPitch(69)).to_freq()

    # custom printing
    def __repr__(self):
        return "p" + str(int(self._interval))

# Midi interval / pitch class
# ---------------------------

class MidiIC(int, IntervalClass):
    def __new__(cls, value):
        return int.__new__(cls, value % 12)

    def __add__(self, other):
        assert_type(other, int)
        return MidiIC(int(self) + int(other))

    def __sub__(self, other):
        assert_type(other, int)
        return MidiIC(int(self) - int(other))

    def ic(self):
        return self

    def embed(self, octave=0):
        return MidiInterval(self + 12*octave)

    def _to_pitch(self):
        return MidiPC(self)

    def to_freq(self):
        # this is just one possibility, one could also provide direct conversion here
        raise NotImplementedError("Can't directly convert to frequency. Use .embed(oct).to_freq() instead.")
    
    def __repr__(self):
        return "ic" + str(int(self))

    # these could be simplified to rely on the corresponding Interval type
    # and defining them in the IntervalClass base class
    @staticmethod
    def unison(self):
        return MidiIC(0)

    @staticmethod
    def octave(self):
        return MidiIC(0)

class MidiPC(Pitch):
    _interval_type = MidiIC
    # custom constructor
    def __init__(self, arg):
        if type(arg) == MidiIC:
            super().__init__(arg)
        elif isinstance(arg, str):
            super().__init__(self._parse(arg)._interval)
        else:
            super().__init__(MidiIC(arg))

    # string parsing
    def _parse(cls, string):
        if string[0:2] == "pc":
            return MidiPitch(int(string[2:]))
        else:
            raise ValueError("Invalid MidiPC {string}")

    def to_freq(self, octave, *args, **kwargs):
        # this is another possibility (cf. MidiIC.to_freq())
        return self._interval.embed(octave).to_freq(*args, **kwargs)
    
    # custom printing:
    def __repr__(self):
        return "pc" + str(int(self._interval))

# Log Frequencies
# ---------------

# PrintPrecision mixin:
# provides individual print precision for each subclass
# (alternative: common print precision for all)
class PrintPrecision:
    _print_precision = 2

    @classmethod
    def print_precision(cls, precision=None):
        if precision is not None:
            cls._print_precision = precision
        return cls._print_precision

class LogFreqInterval(float, Interval, PrintPrecision):
    def __new__(cls, value, is_log=True):
        if is_log:
            return float.__new__(cls, value)
        else:
            return float.__new__(cls, math.log(value))

    def __add__(self, other):
        assert_type(other, float)
        return LogFreqInterval(float(self) + float(other))

    def __sub__(self, other):
        assert_type(other, float)
        return LogFreqInterval(float(self) + float(other))

    def _to_pitch(self):
        return LogFreq(self)

    def __repr__(self):
        return f"lfr{self:.{self.print_precision()}f}"

class LogFreqPitch(Pitch, PrintPrecision):
    _interval_type = LogFreqInterval
    
    def __init__(self, freq, is_log=True):
        if isinstance(freq, LogFreqInterval):
            self._interval = freq
        else:
            self._interval = LogFreqInterval(freq, is_log)

    def __repr__(self):
        return f"{math.exp(self._interval):.{self.print_precision()}f}Hz"
