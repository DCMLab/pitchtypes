from typing import Optional


class CustomException(Exception):
    """Exception that have a default message that can be extended. Default messages
    should be defined without trailing punctuation.
    """

    default_message = "Exception"

    def __init__(self, message: Optional[str], **kwargs):
        if message:
            msg = f"{self.default_message}: {message}"
        else:
            msg = self.default_message + "."
        self.message = msg
        super().__init__(self.message)


# region TypeErrors


class CustomTypeError(CustomException, TypeError):
    """TypeErrors that have a default message that can be extended. Default messages
    should be defined without trailing punctuation.

    Examples:

        >>> raise CustomTypeError
        TypeError.
        >>> raise CustomTypeError("This is a custom message.")
        TypeError: This is a custom message.

    """

    default_message = "TypeError"


class PropertyUndefined(CustomTypeError):
    """
    Raised when a property is not defined for the given type.
    This usually means that an object needs to be converted to another type first.
    """

    default_message = "Property not defined for this type"


class UnexpectedType(CustomTypeError):
    """
    Raised when an unexpected type is encountered.
    """

    default_message = "Unexpected type"

    def __init__(self, message: Optional[str], type=None, **kwargs):
        """Raised when an unexpected type is encountered.

        Args:
            message: Custom message.
            type: Unexpected type.
        """
        if message:
            msg = f"{self.default_message}: {message}"
        else:
            msg = self.default_message + "."
        if type:
            msg += "\n"
        if type:
            msg += f"Type: {type!r}"
        self.arg = type
        self.message = msg
        super().__init__(self.message)


# endregion TypeErrors
# region ValueErrors


class CustomValueError(CustomException, ValueError):
    """ValueErrors that have a default message that can be extended. Default messages
    should be defined without trailing punctuation.
    """

    default_message = "ValueError"


class InvalidInitValue(CustomValueError):
    """Raised when an invalid value is passed to an object's initializer."""

    default_message = "Object cannot be initialized from the given value"

    def __init__(self, message: Optional[str], cls=None, val=None, **kwargs):
        """Raised when an invalid value is passed to an object's initializer.

        Args:
            message: Custom message.
            cls: Class that cannot be initialized from the given value.
            val: Invalid value.
        """
        if message:
            msg = f"{self.default_message}: {message}"
        else:
            msg = self.default_message + "."
        if cls or val:
            msg += "\n"
        if cls:
            msg += f"Class: {cls}"
            if val:
                msg += ", "
        if val:
            msg += f"Value: {val!r}"
        self.cls = cls
        self.val = val
        self.message = msg
        super().__init__(self.message)


class InvalidArgument(CustomValueError):
    """Raised when an invalid argument is passed to a method or a function."""

    default_message = "Invalid argument"

    def __init__(self, message: Optional[str], arg=None, **kwargs):
        """Raised when an invalid argument is passed to a method or a function.

        Args:
            message: Custom message.
            arg: Invalid argument.
        """
        if message:
            msg = f"{self.default_message}: {message}"
        else:
            msg = self.default_message + "."
        if arg:
            msg += "\n"
        if arg:
            msg += f"Argument: {arg!r}"
        self.arg = arg
        self.message = msg
        super().__init__(self.message)


class UnexpectedValue(CustomValueError):
    """Raised when an unexpected value is encountered."""

    default_message = "Unexpected value"

    def __init__(self, message: Optional[str], val=None, **kwargs):
        """Raised when an unexpected value is encountered.

        Args:
            message: Custom message.
            val: Unexpected value.
        """
        if message:
            msg = f"{self.default_message}: {message}"
        else:
            msg = self.default_message + "."
        if val:
            msg += "\n"
        if val:
            msg += f"Value: {val!r}"
        self.val = val
        self.message = msg
        super().__init__(self.message)

# endregion ValueErrors
