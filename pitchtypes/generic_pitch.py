# Pitch as a wrapper for intervals.
# =================================

# A generic class Pitch is used to represent pitches as intervals.
# All pitch-interval arithmetic is defered to the wrapped interval type.
# Special pitch types only implement functionality that is specific to the type, e.g. constructors, printing, etc.

class Pitch():
    # constructors
    #-------------
    
    "Raw constructor that just sets the internal interval."
    def __init__(self, interval: I) -> None:
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

    def pc(self):
        return self.__class__(self._interval.ic())

    # fallback methods

    def __repr__(self):
        return f"Pitch({self._interval})"

# Specific classes
# ================

# Midi interval / pitch
# ---------------------

class MidiInterval(int):
    def __repr__(self):
        return "i" + str(int(self))

    def ic():
        return MidiIC(self)
    
class MidiPitch(Pitch):
    # custom constructor
    def __init__(self, interval):
        if type(interval) == MidiInterval:
            super().__init__(interval)
        else:
            super().__init__(MidiInterval(interval))

    # custom printing
    def __repr__(self):
        return "p" + str(int(self._interval))

    # no need to specify __add__(), __sub__(), or pc()

# Midi interval / pitch class
# ---------------------------

class MidiIC(int):
    def __new__(cls, value):
        return int.__new__(cls, value % 12)

    def __add__(self, other):
        return MidiIC(int(self) + int(other))

    def __sub__(self, other):
        return MidiIC(int(self) - int(other))

    def ic(self):
        return self
    
    def __repr__(self):
        return "ic" + str(int(self))

class MidiPC(Pitch):
    # custom constructor
    def __init__(self, interval):
        if type(interval) == MidiIC:
            super().__init__(interval)
        else:
            super().__init__(MidiIC(interval))
    
    # custom printing:
    def __repr__(self):
        return "pc" + str(int(self._interval))

    # no need to specify __add__(), __sub__(), or pc()
