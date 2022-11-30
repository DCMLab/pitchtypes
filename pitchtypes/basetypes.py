#  Copyright (c) 2020 Robert Lieck
from typing import Iterable, Union, Any, Callable, Optional

import numpy as np
import abc

class AbstractBase:
    """
    This is the abstract base class for all pitch and interval types of the library.
    It provides some shared functionality and properties. See :doc:`/types/abstractbase` for
    more detailed explanations.
    """

    @staticmethod
    def set_func_attr(sub_type: Any,
                      flags: Iterable[Union[bool,None]],
                      names: Iterable[str],
                      funcs: Iterable[Callable]):
        """
        Add functions ``funcs`` as methods with ``names`` to class ``sub_type``, controlled by ``flags``.
        This is used by the decorators
        :meth:`link_pitch_type`, :meth:`link_interval_type`,
        :meth:`link_pitch_class_type` and :meth:`link_interval_class_type`.

        :param sub_type: class to add the methods to
        :param flags: Iterable of flags that control whether a particular method is added or not:
         if `True`, add the method, even if it already exists (i.e. overwrite existing methods);
         if `False`, don't add the method, even if it does not exist;
         if `None`, add the method if does not exist, otherwise do not add it
         (i.e. try to add but don't overwrite existing methods)
        :param names: name of the methods; if added, they will be accessible as via `*.name`
        :param funcs: callables (i.e. implementations of the methods)

        :meta private:
        """
        for flag, name, func in zip(flags, names, funcs):
            if flag or flag is None and name not in vars(sub_type):
                setattr(sub_type, name, func)

    @staticmethod
    def name_check(cls: Any, sub_type: Any, suffix: str, skip_name_check: bool):
        """
        Check if ``sub_type`` follows the standard naming convention. The `Pitch`, `Interval`, `PitchClass` and
        `IntervalClass` sub-type of a `Basetype` should be called `BasetypePitch`, `BasetypeInterval`,
        `BasetypePitchClass` and `BasetypeIntervalClass`. This is used by the decorators
        :meth:`link_pitch_type`, :meth:`link_interval_type`,
        :meth:`link_pitch_class_type` and :meth:`link_interval_class_type`.

        :param cls: base type
        :param sub_type: sub-type
        :param suffix: expected suffix (`Pitch`, `Interval`, `PitchClass`, or `IntervalClass`)
        :param skip_name_check: skip the check and don't raise
        :raises TypeError: if `sub_type.__name__` does not match `cls.__name__ + suffix`

        :meta private:
        """
        if not skip_name_check:
            got_name = sub_type.__name__
            expected_name = cls.__name__ + suffix
            if got_name != expected_name:
                raise TypeError(f"Got class named {got_name}, but expected {expected_name}. "
                                f"Use skip_name_check=True to suppress.")

    @classmethod
    def link_pitch_type(cls,
                        skip_name_check: bool = False,
                        create_init: Optional[bool] = None,
                        create_add: Optional[bool] = None,
                        create_sub: Optional[bool] = None,
                        create_to_class: Optional[bool] = None):
        """
        A decorator to link a pitch type to its base type.

        :meta private:
        """
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
                           skip_name_check: bool = False,
                           create_init: Optional[bool] = None,
                           create_add: Optional[bool] = None,
                           create_sub: Optional[bool] = None,
                           create_mul: Optional[bool] = None,
                           create_div: Optional[bool] = None,
                           create_neg: Optional[bool] = None,
                           create_to_class: Optional[bool] = None):
        """
        A decorator to link an interval type to its base type.

        :meta private:
        """
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
                              skip_name_check: bool = False,
                              create_init: Optional[bool] = None,
                              create_add: Optional[bool] = None,
                              create_sub: Optional[bool] = None):
        """
        A decorator to link a pitch class type to its base type.

        :meta private:
        """
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
                                 skip_name_check: bool = False,
                                 create_init: Optional[bool] = None,
                                 create_add: Optional[bool] = None,
                                 create_sub: Optional[bool] = None,
                                 create_mul: Optional[bool] = None,
                                 create_div: Optional[bool] = None,
                                 create_neg: Optional[bool] = None):
        """
        A decorator to link an interval class type to its base type.

        :meta private:
        """
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

    def __init__(self, value, is_pitch, is_class, **kwargs):
        # call __init__ on super to be cooperative in multi-inheritance,
        # otherwise this should just call object.__init__ and **kwargs should be empty
        super().__init__(**kwargs)
        # the class is frozen if __isfrozen__ == True
        # __setattr__ will check for that and raise an error
        # to set __isfrozen__ for the first time, we need to bypass __setattr__ via super
        # otherwise it would try to check on the not (yet) existing attribute
        super().__setattr__('__isfrozen__', False)
        # we can now set attributes normally (better than dynamically setting, because IDE's can autocomplete)
        self.is_pitch = is_pitch
        self.is_interval = not is_pitch
        self.is_class = is_class
        self.value = value
        # we now freeze the class so attributes cannot be changed anymore
        self.__isfrozen__ = True

    def __setattr__(self, key, value):
        if self.__isfrozen__:
            raise AttributeError("Class is frozen, attributes cannot be set")
        else:
            super().__setattr__(key, value)

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

class Interval(abc.ABC):
    """
    The basic interface implemented by every interval (and interval class) type.
    """

    # fixed intervals

    @classmethod
    @abc.abstractmethod
    def unison(cls):
        """
        Create the unison interval of this type.

        :return: a unison interval
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def octave(cls):
        """
        Create the octave interval of this type.

        :return: an octave interval
        """
        raise NotImplementedError

    # operators

    # @abc.abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    # @abc.abstractmethod
    def __add__(self, other):
        """
        Returns the sum of two intervals.
        """
        raise NotImplementedError

    # @abc.abstractmethod
    def __sub__(self, other):
        """
        Returns the difference of two intervals.
        """
        raise NotImplementedError
    
    # @abc.abstractmethod
    def __mul__(self, other):
        """
        Returns an integer multiple of the interval.
        """
        raise NotImplementedError
    
    def __rmul__(self, other):
        """
        Returns an integer multiple of the interval.
        """
        return self.__mul__(other)
    
    # @abc.abstractmethod
    def __neg__(self):
        """
        Returns the inversion of the interval (same size in the other direction).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __abs__(self):
        """
        For downward intervals, return their upward counterpart, otherwise just return the interval itself.
        """
        raise NotImplementedError

    
    # other interface methods
    
    @abc.abstractmethod
    def direction(self):
        """
        Determines the direction of the interval:
        1 for up, -1 for down and 0 for neutral.
        Different types may have different conventions for the direction of an interval.

        :return: the interval's direction (``-1`` / ``0`` / ``1``, integer)
        """
        raise NotImplementedError

    def abs(self):
        """
        For downward intervals, return their upward counterpart, otherwise just return the interval itself.

        :return: the absolute interval
        """
        return abs(self)
    
    @abc.abstractmethod
    def ic(self):
        """
        Return the interval class that corresponds to this interval.
        If the interval is already an interval class, it is returned itself.

        :return: the interval's corresponding interval class
        """
        raise NotImplementedError

    def to_class(self):
        """
        Alias for ic(), but also supported by pitch types.

        :return: the interval's corresponding interval class
        """
        return self.ic()

    @abc.abstractmethod
    def embed(self):
        """
        For interval classes, return an embedding into the interval space in a (type-dependent) default octave.
        For non-class intervals, return the interval itself.

        :return: a non-class version of this interval
        """
        raise NotImplementedError


class Chromatic(abc.ABC):
    """
    Some intervals have the notion of a chromatic semitone and implement this interface.
    """

    @classmethod
    @abc.abstractmethod
    def chromatic_semitone(cls):
        """
        Return a chromatic semitone (augmented unison) of this type.

        :return: a chromatic semitone interval
        """
        raise NotImplementedError


class Diatonic(abc.ABC):
    """
    Some intervals have a notion of a diatonic step and implement this interface.
    """

    @abc.abstractmethod
    def is_step(self):
        """
        Return True if the interval is considered a step, False otherwise.

        :return: the stepness of the interval (boolean)
        """
        raise NotImplementedError


class Pitch(abc.ABC):
    """
    The basic interface that is implemented by every pitch (and pitch class) type.
    """

    # arithmetic operations

    # @abc.abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    # @abc.abstractmethod
    def __add__(self, other):
        """
        Returns the pitch transposed by an interval

        :param other: an interval of matching type
        :return: the pitch transposed by ``other``
        """
        raise NotImplementedError

    def __sub__(self, other):
        """
        When subtracting another pitch (p1 - p2), return the interval from p2 to p1.
        When subtracting an interval (p - i), transpose the pitch by the inverse interval (p + -i).

        :param other: pitch or interval
        :return: if ``other`` is an interval, the transposed pitch;
                 if ``other`` is a pitch, the interval between both pitches
        """
        if isinstance(other, Pitch):
            try:
                return self.interval_from(other)
            except:
                return NotImplemented
        elif isinstance(other, Interval):
            return self + (-other)
        else:
            return NotImplemented

    # other pitch operations

    @abc.abstractmethod
    def interval_from(self, other):
        """
        Computes the interval from another pitch to this pitch.

        :param other: another pitch
        :return: the interval from other to self
        """
        raise NotImplementedError

    def interval_to(self, other):
        """
        Computes the interval from this pitch to another pitch.

        :param other: another pitch
        :return: the interval from self to other
        """
        return - self.interval_from(other)
    
    @abc.abstractmethod
    def pc(self):
        """
        Returns the pitch class corresponding to the pitch.
        For pitch classes, it returns the pitch class itself.

        :return: the pitch class that corresponds to this pitch
        """
        raise NotImplementedError

    def to_class(self):
        """
        Alias for pc(), but also supported by interval types.

        :return: the pitch class that corresponds to this pitch
        """
        return self.pc()

    @abc.abstractmethod
    def embed(self):
        """
        For a pitch class, returns the corresponding pitch in a (type-dependent) default octave.
        For non-class pitches, returns the pitch itself.

        :return: a non-class version of this pitch
        """
        raise NotImplementedError


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
