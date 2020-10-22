![tests](https://github.com/DCMLab/pitchtypes/workflows/tests/badge.svg)

# pitchtypes

Musically meaningful pitch types

This library provides Python types that handle pitch in a musically correct way. For instance, spelled pitch is handled correctly:

```python
>>> from pitchtypes import SpelledPitchClass
>>> p1 = SpelledPitchClass("C#")
>>> p2 = SpelledPitchClass("Gb")
>>> i = p1 - p2
>>> print(type(i))
<class 'pitchtypes.datatypes.SpelledIntervalClass'>
>>> print(i)
+AA4
```

Of course, you can also convert spelled pitches to their enharmonic equivalents:

```python
>>> from pitchtypes import SpelledPitch, EnharmonicPitch
>>> spelled = SpelledPitch("C#4")
>>> enharmonic = spelled.convert_to(EnharmonicPitch)
>>> print(type(enharmonic))
<class 'pitchtypes.datatypes.EnharmonicPitch'>
>>> print(enharmonic.midi)
61
>>> print(enharmonic.name('sharp'))
C#4
>>> print(enharmonic.name('flat'))
Db4
```

And used continuous log-frequency space (assuming twelve-tone equal temperament for enharmonic pitch):

```python
>>> from pitchtypes import EnharmonicPitch, LogFreqPitch
>>> enharmonic = EnharmonicPitch("A4")
>>> logfreq = enharmonic.convert_to(LogFreqPitch)
>>> print(logfreq)
440.Hz
```

