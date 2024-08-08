import re

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


def diatonic_steps_from_fifths(fifth_steps):
    """
    Return the number of diatonic steps corresponding to the number of steps on the line of fifths
    (`4 * fifth_steps`).

    :param fifth_steps: number of fifth steps
    :return: number of diatonic steps

    :meta private:
    """
    return 4 * fifth_steps
