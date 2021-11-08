Spelled Pitch
=============

**TODO: adapt to python version**

Overview
--------

Spelled pitches and intervals are the standard types of the Western music notation system.
Unlike MIDI pitches, spelled pitches distinguish between enharmonically equivalent pitches
such as `E♭` and `D♯`.
Similarly, spelled intervals distinguish between intervals
such as `m3` (minor 3rd) and `a2` (augmented second) that would be equivalent in the MIDI system.

You can construct spelled pitches and intervals
by calling the constructor of a class
on a string representation of a pitch or interval.
Spelled pitch classes are represented by an uppercase letter followed by zero or more accidentals,
which can be either written as `b/#` or as `♭/♯`.
Spelled pitches take an additional octave number after the letter and the accidentals.

  >>> SpelledPitchClass("Eb")
  Eb
  >>> SpelledPitch("Eb4")
  Eb4

Spelled interval classes consist of one or more letters that indicate the quality of the interval
and a number between 1 and 7 that indicates the generic interval,
e.g. `P1` for a perfect unison, `m3` for a minor 3rd or `aa4` for a double augmented 4th.

====== =========================
letter quality
====== =========================
dd...  diminished multiple times
d      diminished
m      minor
P      perfect
M      major
a      augmented
aa...  augmented multiple times
====== =========================

Spelled intervals have the same elements as intervals but additionally take a number of octaves,
written a suffix `:n`, e.g. `P1:0` or `m3:20`.
By default, intervals are directed upwards. Downwards intervals are indicated by a negative sign,
e.g. `-M2:1` (a major 9th down).
For interval classes, downward and upward intervals cannot be distinguish,
so a downward interval is represented by its complementary upward interval:

  >>> -SpelledIntervalClass("M3")
  m6
  >>> SpelledIntervalClass("-M3")
  m6

Working with Spelled Intervals
------------------------------

Fifths and Octaves
^^^^^^^^^^^^^^^^^^

Internally, spelled intervals are represented by, 5ths and octaves.
Both dimensions are logically dependent:
a major 2nd up is represented by going two 5ths up and one octave down.

  >>> spelled(2,-1) # two 5ths, one octave
  M2:0

This representation is convenient for arithmetics, which can usually be done component-wise.
However, special care needs to be taken when converting to other representations.
For example, the notated octave number (e.g. `:0` in `i"M2:0"`)
does *not* correspond to the internal octaves of the interval (-1 in this case).
In the notation, the interval class (`M2`) and the octave (`:0`) are *independent*.

Interpreting the "internal" (or dependent) octave dimension of the interval
does not make much sense without looking at the fifths.
Therefore, the function [`octaves`](@ref) returns the "external" (or independent) octaves
as used in the string representation, e.g.

   julia> octaves(i"M2:0")
   0

   julia> octaves(i"M2:1")
   1

   julia> octaves(i"M2:-1")
   -1

If you want to look at the internal octaves, use [`internalocts`](@ref).
This corresponds to looking at the `.octaves` field, but works on interval classes too.

Diatonic Steps and Alterations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We provide a number of convenience functions to derive other properties from this representation.
The generic interval (i.e. the number of diatonic steps) can be obtained using [`generic`](@ref).
`generic` respects the direction of the interval but is limitied to a single octave (0 to ±6).
If you need the total number of diatonic steps, including octaves, use [`diasteps`](@ref).
The function [`degree`](@ref) returns the scale degree implied by the interval relative to some root.
Since scale degrees are always above the root, [`degree`](@ref),
it treats negative intervals like their positive complements:

  julia> Pitches.generic(Pitches.i"-M3:1") # some kind of 3rd down
  -2
  
  julia> Pitches.diasteps(Pitches.i"-M3:1") # a 10th down
  -9
  
  julia> Pitches.degree(Pitches.i"-M3:1") # scale degree VI
  5

For interval classes, all three functions are equivalent.
Note that all three count from 0 (for unison/I), not 1.

Complementary to the generic interval functions,
[`alteration`](@ref) returns the specific quality of the interval.
For perfect or major intervals, it returns `0`.
Larger absolute intervals return positive values,
smaller intervals return negative values.

[`degree`](@ref) and [`alteration`](@ref) also work on pitches.
`degree(p)` returns an integer corresponding to the letter (C=`0`, D=`1`, ...),
while `alteration(p)` provides the accidentals (natural=`0`, sharps -> positive, flats -> negative).
For convenience, [`letter(p)`](@ref) returns the letter as an uppercase character.

Reference
---------

.. autoclass:: pitchtypes.Spelled
   :members:
   :undoc-members:

.. autoclass:: pitchtypes.SpelledInterval
   :members:
   :undoc-members:
