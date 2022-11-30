#  Copyright (c) 2021 Robert Lieck

import numpy as np

from pitchtypes.basetypes import AbstractBase


class Harmonic(AbstractBase):

    @staticmethod
    def parse_exponents(exponents):
        if isinstance(exponents, str):
            # remove all whitespace
            exponents_ = "".join(exponents.split())
            # assert starts and ends with '[' and ']' respectively
            if not (exponents_.startswith("[") and exponents_.endswith("]")):
                raise ValueError(f"'exponents' has to start and end with '[' and ']', respectively")
            try:
                exponents = np.array(exponents_[1:-1].split(','), dtype=int)
            except ValueError as e:
                raise ValueError(f"Could not interpret {exponents} as array of integers: {e}")
        else:
            exponents = np.array(exponents, dtype=int)
        return exponents

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@Harmonic.link_interval_type()
class HarmonicInterval(Harmonic):
    def __init__(self, exponents):
        super().__init__(value=self.parse_exponents(exponents=exponents),
                         is_pitch=False,
                         is_class=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self.value)})"

    def to_class(self):
        return self.IntervalClass(exponents=self.value[1:].copy())


@Harmonic.link_interval_class_type()
class HarmonicIntervalClass(Harmonic):
    def __init__(self, exponents):
        super().__init__(value=self.parse_exponents(exponents=exponents),
                         is_pitch=False,
                         is_class=True)

    def __repr__(self):
        return f"{self.__class__.__name__}({[None] + list(self.value)})"
