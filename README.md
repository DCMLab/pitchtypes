# pitchtypes

[![docs (development version)](https://img.shields.io/badge/docs-dev-blue.svg)](https://dcmlab.github.io/pitchtypes/)

![build](https://github.com/DCMLab/pitchtypes/workflows/build/badge.svg)
[![PyPI version](https://badge.fury.io/py/pitchtypes.svg)](https://badge.fury.io/py/pitchtypes)

![tests](https://github.com/DCMLab/pitchtypes/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/DCMLab/pitchtypes/branch/master/graph/badge.svg)](https://codecov.io/gh/DCMLab/pitchtypes)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A library for handling musical pitches and intervals in a systematic way.
For other (and mostly compatible) implementations see:

- [Pitches.jl](https://github.com/DCMLab/Pitches.jl) (Julia)
- [musicology-pitch](https://github.com/DCMLab/haskell-musicology/tree/master/musicology-pitch) (Haskell)
- [purescript-pitches](https://github.com/DCMLab/purescript-pitches) (Purescript)
- [pitches.rs](https://github.com/DCMLab/rust-pitches/blob/main/README.md) (Rust)

The main goals of this library are:

- providing types and operations (such as arithmetics, printing and parsing) for common types of pitches and intervals,
  (in particular spelled pitches and intervals, which are often difficult to handle),
- providing a generic interface for writing code that is agnostic to the specific pitch or interval types.

## Installation

`pip install pitchtypes`

## Minimal Example

```python
import pitchtypes as pt

# write a generic function

def transposeby(pitches, interval):
    return [pitch + interval for pitch in pitches]

# use it with different pitch types

# spelled pitches correspond to written notes in Western notation
spelled_pitches = [pt.SpelledPitch(p)
                   for p in ["C4", "Eb4", "G#4"]]
print(transposeby(spelled_pitches, pt.SpelledInterval("m3:0"))

# spelled pitch classes work the same but they ignore octaves
spelled_pitch_classes = [pt.SpelledPitchClass(p)
                         for p in ["C", "Eb", "G#"]]
print(transposeby(spelled_pitches, pt.SpelledIntervalClass("m3"))

# enharmonic pitches correspond to keys on the piano
enharmonic_pitches = [pt.EnharmonicPitch(p)
                      for p in [60, 63, 68]]
print(transposeby(spelled_pitches, pt.EnharmonicInterval(3))
```

Output:

```
[Eb4, Gb4, B4]
[Eb, Gb, B]
[D#4, F#4, B4]
```

## Old Example (delete/adapt?)

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
