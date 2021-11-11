#  Copyright (c) 2020 Robert Lieck

import numpy as np
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


class Interval:
    """
    The basic interface implemented by every interval (and interval class) type.
    """

    @classmethod
    def unison(cls):
        """
        Return the unison interval of this type.
        """
        raise NotImplementedError

    @classmethod
    def octave(cls):
        """
        Return the octave interval of this type.
        """
        raise NotImplementedError

    def direction(self):
        """
        Return the direction of the interval:
        1 for up, -1 for down and 0 for neutral.
        Different types may have different conventions for the direction of an interval.
        """
        raise NotImplementedError

    def abs(self):
        """
        For downward intervals, return their upward counterpart, otherwise just return the interval itself.
        """
        raise NotImplementedError

    def ic(self):
        """
        Return the interval class that corresponds to this interval.
        If the interval is already an interval class, it is returned itself.
        """
        raise NotImplementedError

    def to_class(self):
        """
        Alias for ic(), but also supported by pitch types.
        """
        return self.ic()

    def embed(self):
        """
        For interval classes, return an embedding into the interval space in a (type-dependent) default octave.
        For non-class intervals, return the interval itself.
        """
        raise NotImplementedError


class Chromatic:
    """
    Some intervals have the notion of a chromatic semitone and implement this interface.
    """

    @classmethod
    def chromatic_semitone(cls):
        """
        Return a chromatic semitone (augmented unison) of this type.
        """
        raise NotImplementedError


class Diatonic:
    """
    Some intervals have a notion of a diatonic step and implement this interface.
    """

    def is_step(self):
        """
        Return True if the interval is considered a step, False otherwise.
        """
        raise NotImplementedError


class Pitch:
    """
    The basic interface that is implemented by every pitch (and pitch class) type.
    """

    def pc(self):
        """
        Returns the pitch class corresponding to the pitch.
        For pitch classes, it returns the pitch class itself.
        """
        raise NotImplementedError

    def to_class(self):
        """
        Alias for pc(), but also supported by interval types.
        """
        return self.pc()

    def embed(self):
        """
        For a pitch class, returns the corresponding pitch in a (type-dependent) default octave.
        For non-class pitches, returns the pitch itself.
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
