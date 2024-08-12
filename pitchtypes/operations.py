"""
The addition_convert_types and subtraction_convert_types dictionaries are used to determine valid operations
and the target types to perform these operation between two pitches or intervals.
The keys are tuples of the types of the two compatible operands for that specific operation,
and the values are tuples of the target types of the result.

For example, the key ('EnharmonicPitch', 'SpecificInterval') maps to the value
('EnharmonicPitch', 'EnharmonicInterval'), because a specific interval has to be
converted into an enharmonic interval to be added to an enharmonic pitch.
"""

addition_convert_types = {
    ('EnharmonicPitch', 'EnharmonicInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('EnharmonicPitch', 'SpelledInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('EnharmonicPitch', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('EnharmonicPitch', 'SpelledIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),

    ('SpelledPitch', 'EnharmonicInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('SpelledPitch', 'SpelledInterval'): ('SpelledPitch', 'SpelledInterval'),
    ('SpelledPitch', 'GenericInterval'): ('GenericPitch', 'GenericInterval'),
    ('SpelledPitch', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitch', 'SpelledIntervalClass'): ('SpelledPitchClass', 'SpelledIntervalClass'),
    ('SpelledPitch', 'GenericIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('GenericPitch', 'SpelledInterval'): ('GenericPitch', 'GenericInterval'),
    ('GenericPitch', 'GenericInterval'): ('GenericPitch', 'GenericInterval'),
    ('GenericPitch', 'SpelledIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('GenericPitch', 'GenericIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('EnharmonicInterval', 'EnharmonicInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('EnharmonicInterval', 'SpelledInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('EnharmonicInterval', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicInterval', 'SpelledIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),

    ('SpelledInterval', 'EnharmonicInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('SpelledInterval', 'SpelledInterval'): ('SpelledInterval', 'SpelledInterval'),
    ('SpelledInterval', 'GenericInterval'): ('GenericInterval', 'GenericInterval'),
    ('SpelledInterval', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalCLass'),
    ('SpelledInterval', 'SpelledIntervalClass'): ('SpelledIntervalClass', 'SpelledIntervalCLass'),
    ('SpelledInterval', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalCLass'),

    ('GenericInterval', 'EnharmonicInterval'): ('GenericInterval', 'GenericInterval'),
    ('GenericInterval', 'SpelledInterval'): ('GenericInterval', 'GenericInterval'),
    ('GenericInterval', 'GenericInterval'): ('GenericInterval', 'GenericInterval'),
    ('GenericInterval', 'EnharmonicIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericInterval', 'SpelledIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericInterval', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('EnharmonicIntervalClass', 'EnharmonicInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicIntervalClass', 'SpelledInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicIntervalClass', 'SpelledIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),

    ('SpelledIntervalClass', 'EnharmonicInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledIntervalClass', 'SpelledInterval'): ('SpelledIntervalClass', 'SpelledIntervalClass'),
    ('SpelledIntervalClass', 'GenericInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('SpelledIntervalClass', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledIntervalClass', 'SpelledIntervalClass'): ('SpelledIntervalClass', 'SpelledIntervalClass'),
    ('SpelledIntervalClass', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('GenericIntervalClass', 'SpelledInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericIntervalClass', 'GenericInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericIntervalClass', 'SpelledIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericIntervalClass', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
}

subtraction_convert_types = {
    ('EnharmonicPitch', 'EnharmonicPitch'): ('EnharmonicPitch', 'EnharmonicPitch'),
    ('EnharmonicPitch', 'SpelledPitch'): ('EnharmonicPitch', 'EnharmonicPitch'),
    ('EnharmonicPitch', 'EnharmonicInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('EnharmonicPitch', 'SpelledInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('EnharmonicPitch', 'EnharmonicPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('EnharmonicPitch', 'SpelledPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('EnharmonicPitch', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('EnharmonicPitch', 'SpelledIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),

    ('SpelledPitch', 'EnharmonicPitch'): ('EnharmonicPitch', 'EnharmonicPitch'),
    ('SpelledPitch', 'SpelledPitch'): ('SpelledPitch', 'SpelledPitch'),
    ('SpelledPitch', 'GenericPitch'): ('GenericPitch', 'GenericPitch'),
    ('SpelledPitch', 'EnharmonicInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('SpelledPitch', 'SpelledInterval'): ('SpelledPitch', 'SpelledInterval'),
    ('SpelledPitch', 'GenericInterval'): ('GenericPitch', 'GenericInterval'),
    ('SpelledPitch', 'EnharmonicPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('SpelledPitch', 'SpelledPitchClass'): ('SpelledPitchClass', 'SpelledPitchClass'),
    ('SpelledPitch', 'GenericPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('SpelledPitch', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitch', 'SpelledIntervalClass'): ('SpelledPitchClass', 'SpelledIntervalClass'),
    ('SpelledPitch', 'GenericIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('GenericPitch', 'SpelledPitch'): ('GenericPitch', 'GenericPitch'),
    ('GenericPitch', 'GenericPitch'): ('GenericPitch', 'GenericPitch'),
    ('GenericPitch', 'SpelledInterval'): ('GenericPitch', 'GenericInterval'),
    ('GenericPitch', 'GenericInterval'): ('GenericPitch', 'GenericInterval'),
    ('GenericPitch', 'SpelledPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('GenericPitch', 'GenericPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('GenericPitch', 'SpelledIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('GenericPitch', 'GenericIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('EnharmonicInterval', 'EnharmonicInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('EnharmonicInterval', 'SpelledInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('EnharmonicInterval', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicInterval', 'SpelledIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),

    ('SpelledInterval', 'EnharmonicInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('SpelledInterval', 'SpelledInterval'): ('SpelledInterval', 'SpelledInterval'),
    ('SpelledInterval', 'GenericInterval'): ('GenericInterval', 'GenericInterval'),
    ('SpelledInterval', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledInterval', 'SpelledIntervalClass'): ('SpelledIntervalClass', 'SpelledIntervalClass'),
    ('SpelledInterval', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('GenericInterval', 'EnharmonicInterval'): ('GenericInterval', 'GenericInterval'),
    ('GenericInterval', 'SpelledInterval'): ('GenericInterval', 'GenericInterval'),
    ('GenericInterval', 'GenericInterval'): ('GenericInterval', 'GenericInterval'),
    ('GenericInterval', 'EnharmonicIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericInterval', 'SpelledIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericInterval', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('EnharmonicPitchClass', 'EnharmonicPitch'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('EnharmonicPitchClass', 'SpelledPitch'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('EnharmonicPitchClass', 'EnharmonicInterval'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('EnharmonicPitchClass', 'SpelledInterval'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('EnharmonicPitchClass', 'EnharmonicPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('EnharmonicPitchClass', 'SpelledPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('EnharmonicPitchClass', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('EnharmonicPitchClass', 'SpelledIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),

    ('SpelledPitchClass', 'EnharmonicPitch'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('SpelledPitchClass', 'SpelledPitch'): ('SpelledPitchClass', 'SpelledPitchClass'),
    ('SpelledPitchClass', 'GenericPitch'): ('GenericPitchClass', 'GenericPitchClass'),
    ('SpelledPitchClass', 'EnharmonicInterval'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitchClass', 'SpelledInterval'): ('SpelledPitchClass', 'SpelledIntervalClass'),
    ('SpelledPitchClass', 'GenericInterval'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('SpelledPitchClass', 'EnharmonicPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('SpelledPitchClass', 'SpelledPitchClass'): ('SpelledPitchClass', 'SpelledPitchClass'),
    ('SpelledPitchClass', 'GenericPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('SpelledPitchClass', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitchClass', 'SpelledIntervalClass'): ('SpelledPitchClass', 'SpelledIntervalClass'),
    ('SpelledPitchClass', 'GenericIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('GenericPitchClass', 'SpelledPitch'): ('GenericPitchClass', 'GenericPitchClass'),
    ('GenericPitchClass', 'GenericPitch'): ('GenericPitchClass', 'GenericPitchClass'),
    ('GenericPitchClass', 'SpelledInterval'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('GenericPitchClass', 'GenericInterval'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('GenericPitchClass', 'SpelledPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('GenericPitchClass', 'GenericPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('GenericPitchClass', 'SpelledIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('GenericPitchClass', 'GenericIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('EnharmonicIntervalClass', 'EnharmonicInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicIntervalClass', 'SpelledInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicIntervalClass', 'SpelledIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),

    ('SpelledIntervalClass', 'EnharmonicInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledIntervalClass', 'SpelledInterval'): ('SpelledIntervalClass', 'SpelledIntervalClass'),
    ('SpelledIntervalClass', 'GenericInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('SpelledIntervalClass', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledIntervalClass', 'SpelledIntervalClass'): ('SpelledIntervalClass', 'SpelledIntervalClass'),
    ('SpelledIntervalClass', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('GenericIntervalClass', 'SpelledInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericIntervalClass', 'GenericInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericIntervalClass', 'SpelledIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericIntervalClass', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
}
