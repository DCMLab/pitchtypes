import re
import numbers

INTERVAL_REGEX = re.compile(
    "^(?P<sign>[-+])?("
    "(?P<quality0>P)(?P<generic0>[145])|"  # perfect intervals
    "(?P<quality1>|(M)|(m))(?P<generic1>[2367])|"  # imperfect intervals
    "(?P<quality2>(a+)|(d+))(?P<generic2>[1-7])"  # augmeted/diminished intervals
    ")(?P<octave>(:-?[0-9]+)?)$"
)
PITCH_REGEX = re.compile(
    "^(?P<class>[A-G])(?P<modifiers>(b*)|(#*))(?P<octave>(-?[0-9]+)?)$"
)


def fifths_from_generic_interval_class(generic):
    """
    Return the number of steps along the line of fifths corresponding to the given generic interval:
    (2 * generic - 1) % 7 - 1.

    :param generic: generic interval (integer in 1,...,7)
    :return: fifth steps (integer in -1, 0, ..., 5)

    :meta private:
    """
    if not isinstance(generic, numbers.Integral) or not (1 <= generic <= 7):
        raise ValueError(f"generic interval must be an integer between 1 and 7 (incl.), got {generic}")
    return (2 * generic - 1) % 7 - 1


def fifths_from_diatonic_pitch_class(pitch_class):
    """
    Return the number of steps along the line of fifths corresponding to a diatonic pitch class.

    :param pitch_class: a diatonic pitch class; character in A, B, C, D, E, F, G
    :return: fifth steps; an integer in -1, 0, ... 5

    :meta private:
    """
    pitch_classes = "ABCDEFG"
    if pitch_class not in pitch_classes:
        pitch_classes = "', '".join(pitch_classes)
        raise ValueError(f"diatonic pitch class must be one of '{pitch_classes}', but got {pitch_class}")
    return {"F": -1, "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5}[pitch_class]


def diatonic_steps_from_fifths(fifth_steps):
    """
    Return the number of diatonic steps corresponding to the number of steps on the line of fifths
    (`4 * fifth_steps`).

    :param fifth_steps: number of fifth steps
    :return: number of diatonic steps

    :meta private:
    """
    return 4 * fifth_steps
