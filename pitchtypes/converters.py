#  Copyright (c) 2021 Robert Lieck

from pitchtypes import Converters, Spelled, Enharmonic, LogFreq

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
        else:
            spelled_ref_point = Spelled.Pitch("C4")
            enharmonic_ref_point = Enharmonic.Pitch("C4")
        return enharmonic_ref_point - convert_spelled_to_enharmonic(spelled_ref_point - spelled)


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
