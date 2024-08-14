#  Copyright (c) 2021 Robert Lieck

from pitchtypes import Converters, Spelled, Enharmonic, Generic, LogFreq


def convert_spelled_to_enharmonic(spelled):
    if spelled.is_pitch:
        fifth_steps_from_f = spelled.fifths() + 1
        # get the base pitch in 0,...,11
        base_pitch = ((fifth_steps_from_f % 7 - 1) * 7) % 12
        # get the accidental, i.e. chromatic semitone steps to add to base pitch
        # (floor-divide (//) rounds down, for negative numbers that is equal to the remainder of division minus one)
        accidentals = fifth_steps_from_f // 7
        if spelled.is_class:
            return Enharmonic.PitchClass(value=base_pitch + accidentals)
        else:
            return Enharmonic.Pitch(value=12 * (spelled.octaves() + 1) + base_pitch + accidentals)
    else:
        # convert intervals by going via reference pitches
        if spelled.is_class:
            spelled_ref_point = Spelled.PitchClass("C")
            enharmonic_ref_point = Enharmonic.PitchClass("C")
            return enharmonic_ref_point - convert_spelled_to_enharmonic(spelled_ref_point - spelled)
        else:
            spelled_ref_point = Spelled.Pitch("C4")
            enharmonic_ref_point = Enharmonic.Pitch("C4")
            return enharmonic_ref_point - convert_spelled_to_enharmonic(spelled_ref_point - spelled)


def convert_spelled_to_generic(spelled):
    if spelled.is_pitch:
        # get the base pitch in [0,6]
        base_pitch = (spelled.fifths() * 4) % 7
        if spelled.is_class:
            return Generic.PitchClass(value=base_pitch)
        else:
            return Generic.Pitch(value=7 * (spelled.octaves() + 1) + base_pitch)
    else:
        # convert intervals by going via reference pitches
        if spelled.is_class:
            spelled_ref_point = Spelled.PitchClass("C")
            generic_ref_point = Generic.PitchClass("C")
        else:
            spelled_ref_point = Spelled.Pitch("C4")
            generic_ref_point = Generic.Pitch("C4")
        return generic_ref_point - convert_spelled_to_generic(spelled_ref_point - spelled)


def convert_to_class(pitch):
    if pitch.is_pitch:
        return pitch.to_class()
    else:
        return pitch


Converters.register_converter(from_type=Spelled.Pitch,
                              to_type=Enharmonic.Pitch,
                              conv_func=convert_spelled_to_enharmonic)
Converters.register_converter(from_type=Spelled.Interval,
                              to_type=Enharmonic.Interval,
                              conv_func=convert_spelled_to_enharmonic)
Converters.register_converter(from_type=Spelled.PitchClass,
                              to_type=Enharmonic.PitchClass,
                              conv_func=convert_spelled_to_enharmonic)
Converters.register_converter(from_type=Spelled.IntervalClass,
                              to_type=Enharmonic.IntervalClass,
                              conv_func=convert_spelled_to_enharmonic)

Converters.register_converter(from_type=Enharmonic.Pitch,
                              to_type=LogFreq.Pitch,
                              conv_func=lambda enharmonic: enharmonic.convert_to_logfreq())
Converters.register_converter(from_type=Enharmonic.Interval,
                              to_type=LogFreq.Interval,
                              conv_func=lambda enharmonic: enharmonic.convert_to_logfreq())
Converters.register_converter(from_type=Enharmonic.PitchClass,
                              to_type=LogFreq.PitchClass,
                              conv_func=lambda enharmonic: enharmonic.convert_to_logfreq())
Converters.register_converter(from_type=Enharmonic.IntervalClass,
                              to_type=LogFreq.IntervalClass,
                              conv_func=lambda enharmonic: enharmonic.convert_to_logfreq())

Converters.register_converter(from_type=Spelled.Pitch,
                              to_type=Generic.Pitch,
                              conv_func=convert_spelled_to_generic)
Converters.register_converter(from_type=Spelled.PitchClass,
                              to_type=Generic.PitchClass,
                              conv_func=convert_spelled_to_generic)
Converters.register_converter(from_type=Spelled.Interval,
                              to_type=Generic.Interval,
                              conv_func=convert_spelled_to_generic)
Converters.register_converter(from_type=Spelled.IntervalClass,
                              to_type=Generic.IntervalClass,
                              conv_func=convert_spelled_to_generic)

Converters.register_converter(from_type=Enharmonic.Pitch,
                              to_type=Enharmonic.PitchClass,
                              conv_func=convert_to_class)
Converters.register_converter(from_type=Enharmonic.Interval,
                              to_type=Enharmonic.IntervalClass,
                              conv_func=convert_to_class)
Converters.register_converter(from_type=Spelled.Pitch,
                              to_type=Spelled.PitchClass,
                              conv_func=convert_to_class)
Converters.register_converter(from_type=Spelled.Interval,
                              to_type=Spelled.IntervalClass,
                              conv_func=convert_to_class)
Converters.register_converter(from_type=Generic.Pitch,
                              to_type=Generic.PitchClass,
                              conv_func=convert_to_class)
Converters.register_converter(from_type=Generic.Interval,
                              to_type=Generic.IntervalClass,
                              conv_func=convert_to_class)
