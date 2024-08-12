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
    ('EnharmonicPitch', 'SpelledInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('EnharmonicPitch', 'SpelledIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),

    ('SpelledPitch', 'EnharmonicInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('SpelledPitch', 'GenericInterval'): ('GenericPitch', 'GenericInterval'),
    ('SpelledPitch', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitch', 'GenericIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('GenericPitch', 'SpelledInterval'): ('GenericPitch', 'GenericInterval'),
    ('GenericPitch', 'SpelledIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('EnharmonicInterval', 'SpelledInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('EnharmonicInterval', 'SpelledIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),

    ('SpelledInterval', 'EnharmonicInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('SpelledInterval', 'GenericInterval'): ('GenericInterval', 'GenericInterval'),
    ('SpelledInterval', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalCLass'),
    ('SpelledInterval', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalCLass'),

    ('GenericInterval', 'SpelledInterval'): ('GenericInterval', 'GenericInterval'),
    ('GenericInterval', 'SpelledIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('EnharmonicPitchClass', 'SpelledInterval'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('EnharmonicPitchClass', 'SpelledIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),

    ('SpelledPitchClass', 'EnharmonicInterval'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitchClass', 'GenericInterval'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('SpelledPitchClass', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitchClass', 'SpelledIntervalClass'): ('SpelledPitchClass', 'SpelledIntervalClass'),

    ('GenericPitchClass', 'SpelledInterval'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('GenericPitchClass', 'SpelledIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('EnharmonicIntervalClass', 'SpelledInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicIntervalClass', 'SpelledIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),

    ('SpelledIntervalClass', 'EnharmonicInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledIntervalClass', 'GenericInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('SpelledIntervalClass', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledIntervalClass', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('GenericIntervalClass', 'SpelledInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericIntervalClass', 'SpelledIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
}

subtraction_convert_types = {
    ('EnharmonicPitch', 'SpelledPitch'): ('EnharmonicPitch', 'EnharmonicPitch'),
    ('EnharmonicPitch', 'SpelledInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('EnharmonicPitch', 'SpelledPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('EnharmonicPitch', 'SpelledIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),

    ('SpelledPitch', 'EnharmonicPitch'): ('EnharmonicPitch', 'EnharmonicPitch'),
    ('SpelledPitch', 'GenericPitch'): ('GenericPitch', 'GenericPitch'),
    ('SpelledPitch', 'EnharmonicInterval'): ('EnharmonicPitch', 'EnharmonicInterval'),
    ('SpelledPitch', 'GenericInterval'): ('GenericPitch', 'GenericInterval'),
    ('SpelledPitch', 'EnharmonicPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('SpelledPitch', 'GenericPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('SpelledPitch', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitch', 'GenericIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('GenericPitch', 'SpelledPitch'): ('GenericPitch', 'GenericPitch'),
    ('GenericPitch', 'SpelledInterval'): ('GenericPitch', 'GenericInterval'),
    ('GenericPitch', 'SpelledPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('GenericPitch', 'SpelledIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('EnharmonicInterval', 'SpelledInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('EnharmonicInterval', 'SpelledIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),

    ('SpelledInterval', 'EnharmonicInterval'): ('EnharmonicInterval', 'EnharmonicInterval'),
    ('SpelledInterval', 'GenericInterval'): ('GenericInterval', 'GenericInterval'),
    ('SpelledInterval', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledInterval', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('GenericInterval', 'SpelledInterval'): ('GenericInterval', 'GenericInterval'),
    ('GenericInterval', 'SpelledIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('EnharmonicPitchClass', 'SpelledPitch'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('EnharmonicPitchClass', 'SpelledInterval'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('EnharmonicPitchClass', 'SpelledPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('EnharmonicPitchClass', 'SpelledIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),

    ('SpelledPitchClass', 'EnharmonicPitch'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('SpelledPitchClass', 'GenericPitch'): ('GenericPitchClass', 'GenericPitchClass'),
    ('SpelledPitchClass', 'EnharmonicInterval'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitchClass', 'GenericInterval'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('SpelledPitchClass', 'EnharmonicPitchClass'): ('EnharmonicPitchClass', 'EnharmonicPitchClass'),
    ('SpelledPitchClass', 'GenericPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('SpelledPitchClass', 'EnharmonicIntervalClass'): ('EnharmonicPitchClass', 'EnharmonicIntervalClass'),
    ('SpelledPitchClass', 'GenericIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('GenericPitchClass', 'SpelledPitch'): ('GenericPitchClass', 'GenericPitchClass'),
    ('GenericPitchClass', 'SpelledInterval'): ('GenericPitchClass', 'GenericIntervalClass'),
    ('GenericPitchClass', 'SpelledPitchClass'): ('GenericPitchClass', 'GenericPitchClass'),
    ('GenericPitchClass', 'SpelledIntervalClass'): ('GenericPitchClass', 'GenericIntervalClass'),

    ('EnharmonicIntervalClass', 'SpelledInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('EnharmonicIntervalClass', 'SpelledIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),

    ('SpelledIntervalClass', 'EnharmonicInterval'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledIntervalClass', 'GenericInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('SpelledIntervalClass', 'EnharmonicIntervalClass'): ('EnharmonicIntervalClass', 'EnharmonicIntervalClass'),
    ('SpelledIntervalClass', 'GenericIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),

    ('GenericIntervalClass', 'SpelledInterval'): ('GenericIntervalClass', 'GenericIntervalClass'),
    ('GenericIntervalClass', 'SpelledIntervalClass'): ('GenericIntervalClass', 'GenericIntervalClass'),
}
