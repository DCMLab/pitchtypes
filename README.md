# pitchtypes

[![PyPI version](https://badge.fury.io/py/pitchtypes.svg)](https://badge.fury.io/py/pitchtypes)
![build](https://github.com/DCMLab/pitchtypes/workflows/build/badge.svg)
![tests](https://github.com/DCMLab/pitchtypes/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/DCMLab/pitchtypes/branch/main/graph/badge.svg)](https://codecov.io/gh/DCMLab/pitchtypes)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**Musically meaningful types**

The purpose of this Python library is to:

1. Provide types that handle pitch in a musically correct way.
2. Make it easy to implement other musically meaningful types.

For instance, spelled pitch is handled correctly:

```python
>>> from pitchtypes import SpelledPitchClass
>>> p1 = SpelledPitchClass("C#")
>>> p2 = SpelledPitchClass("Gb")
>>> i = p1 - p2
>>> type(i)
<class 'pitchtypes.datatypes.SpelledIntervalClass'>
>>> i
+AA4
```

Of course, you can also convert spelled pitches to their enharmonic equivalents:

```python
>>> from pitchtypes import SpelledPitch, EnharmonicPitch
>>> spelled = SpelledPitch("C#4")
>>> enharmonic = spelled.convert_to(EnharmonicPitch)
>>> type(enharmonic)
<class 'pitchtypes.datatypes.EnharmonicPitch'>
>>> enharmonic.midi
61
>>> enharmonic.name('sharp')
C#4
>>> enharmonic.name('flat')
Db4
```

And used continuous log-frequency space (assuming twelve-tone equal temperament for enharmonic pitch):

```python
>>> from pitchtypes import EnharmonicPitch, LogFreqPitch
>>> enharmonic = EnharmonicPitch("A4")
>>> logfreq = enharmonic.convert_to(LogFreqPitch)
>>> logfreq
440.Hz
```
For more examples, have a look at the [Tutorial.ipynb](Tutorial.ipynb)!
