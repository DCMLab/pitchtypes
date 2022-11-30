Spelled Pitch
=============

Overview
--------

Spelled pitches and intervals are the standard types of the Western music notation system.
Unlike MIDI pitches, spelled pitches distinguish between enharmonically equivalent pitches
such as ``E♭`` and ``D♯``.
Similarly, spelled intervals distinguish between intervals
such as ``m3`` (minor 3rd) and ``a2`` (augmented second) that would be equivalent in the MIDI system.

You can construct spelled pitches and intervals
by calling the constructor of a class
on a string representation of a pitch or interval.
Spelled pitch classes are represented by an uppercase letter followed by zero or more accidentals,
which can be either written as ``b/#`` or as ``♭/♯``.
Spelled pitches take an additional octave number after the letter and the accidentals.

  >>> from pitchtypes import *
  >>> SpelledPitchClass("Eb")
  Eb
  >>> SpelledPitch("Eb4")
  Eb4

Spelled interval classes consist of one or more letters that indicate the quality of the interval
and a number between 1 and 7 that indicates the generic interval,
e.g. ``P1`` for a perfect unison, ``m3`` for a minor 3rd or ``aa4`` for a double augmented 4th.

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
written a suffix ``:n``, e.g. ``P1:0`` or ``m3:20``.
By default, intervals are directed upwards. Downwards intervals are indicated by a negative sign,
e.g. ``-M2:1`` (a major 9th down).
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

  >>> SpelledInterval.from_fifths_and_octaves(2,-1) # two 5ths, one octave
  M2:0

This representation is convenient for arithmetics, which can usually be done component-wise.
However, special care needs to be taken when converting to other representations.
For example, the notated octave number (e.g. ``:0`` in ``i"M2:0"``)
does *not* correspond to the internal octaves of the interval (-1 in this case).
In the notation, the interval class (``M2``) and the octave (``:0``) are *independent*.

Interpreting the "internal" (or dependent) octave dimension of the interval
does not make much sense without looking at the fifths.
Therefore, the function :py:meth:`octaves <pitchtypes.Spelled.octaves>` returns the "external" (or independent) octaves
as used in the string representation, e.g.

   >>> SpelledInterval("M2:0").octaves()
   0
   >>> SpelledInterval("M2:1").octaves()
   1
   >>> SpelledInterval("-M2:0").octaves()
   -1

If you want to look at the internal octaves, use  :py:meth:`internal_octaves <pitchtypes.SpelledInterval.internal_octaves>`.

Diatonic Steps and Alterations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We provide a number of convenience functions to derive other properties from this representation.
The generic interval (i.e. the number of diatonic steps) can be obtained using :py:meth:`generic <pitchtypes.Spelled.generic>`.
``generic`` respects the direction of the interval but is limitied to a single octave (0 to ±6).
If you need the total number of diatonic steps, including octaves, use :py:meth:`diatonic_steps <pitchtypes.Spelled.diatonic_steps>`.
The method :py:meth:`degree <pitchtypes.Spelled.degree>` returns the scale degree implied by the interval relative to some root.
Since scale degrees are always above the root,
``degree`` treats negative intervals like their positive complements,
expressing the interval as a diatonic scale degree (I = 0, II = 1, ...):

    >>> SpelledInterval("-M3:1").generic() # some kind of 3rd down
    -2
    >>> SpelledInterval("-M3:1").diatonic_steps() # a 10th down
    -9
    >>> SpelledInterval("-M3:1").degree() # scale degree VI
    5

For interval classes, all three functions are equivalent.
Note that all three count from 0 (for unison/I), not 1.

Complementary to the generic interval methods,
:py:meth:`alteration <pitchtypes.SpelledInterval.alteration>` returns the specific quality of the interval.
For perfect or major intervals, it returns ``0``.
Larger absolute intervals return positive values,
smaller intervals return negative values.
For interval classes, :py:meth:`alteration <pitchtypes.SpelledIntervalClass.alteration>`
always refers to the upward interval,
just like :py:meth:`degree <pitchtypes.SpelledIntervalClass.degree>`:

    >>> SpelledIntervalClass("-M3")
    m6
    >>> SpelledIntervalClass("-M3").degree() # VI
    5
    >>> SpelledIntervalClass("-M3").alteration()
    -1

:py:meth:`degree <pitchtypes.Spelled.degree>` and :py:meth:`alteration <pitchtypes.Spelled.alteration>` also work on pitches.
``degree(p)`` returns an integer corresponding to the letter (C=0, D=1, ...),
while ``alteration(p)`` provides the accidentals (natural=0, sharps -> positive, flats -> negative).
For convenience, :py:meth:`letter <pitchtypes.SpelledPitch.letter>` returns the letter as an uppercase character.

    >>> SpelledPitch("Dbb4").degree()
    1
    >>> SpelledPitch("Dbb4").alteration()
    -2

.. _spelled.ordering:
    
Ordering
^^^^^^^^

Spelled intervals and pitches can be compared through binary comparison operators (``==``, ``<``, etc.)
or through the :py:meth:`compare <pitchtypes.Spelled.compare>` method.

Non-class intervals/pitches have a meaningful diatonic ordering,
that goes by the diatonic step (or note name + octave) first and by alteration second:

.. code-block:: none
                   
   P4:0 < a4:0 < aaaa4:0 < dddd5:0 < d5:0 < P5:0
   F4   < F#4  < F####4  < Gbbbb4  < Gb4  < G4

Interval/pitch classes are circular in their diatonic ordering,
so a line-of-fifths ordering is used instead:

.. code-block:: none
                   
   m7 < P4 < P1 < P5 < M2
   Bb < F  < C  < G  < D

Examples:
   
    >>> sorted(map(SpelledInterval, ["P5:0", "d5:0", "dddd5:0", "aaaa4:0", "a4:0", "P4:0"]))
    [P4:0, a4:0, aaaa4:0, dddd5:0, d5:0, P5:0]
    >>> SpelledIntervalClass("P4") < SpelledIntervalClass("P1") # LoF ordering
    True
    >>> SpelledPitchClass("Eb").compare(SpelledPitchClass("D#")) # Eb < D# (LoF)
    -1

.. _spelled.one-hot:
    
One-hot Encoding
^^^^^^^^^^^^^^^^

Spelled types support conversion to and from one-hot vectors.
Pitch and interval classes are one-dimensional
and are expressed on a segment of the line of fifths.
When converting to one-hot vectors, the LoF range must be provided
as a tuple ``(lower, upper)``, where the range includes both bounds.
When converting back from a one-hot vector only the lower bound is required:

    >>> SpelledIntervalClass("M7").onehot(fifth_range=(-7,7))
    array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0])
    >>> SpelledPitchClass.from_onehot(np.array([0, 0, 0, 1, 0]), -2)
    G

Non-class intervals and pitches are two dimensional and are thus encoded in a one-hot matrix.
The first dimension corresponds to the line of fifths (as for classes),
the second dimension corresponds to independent octaves.
Both ranges must be provided as ``(lower, upper)`` tuples (inclusive) for encoding
while only the lower bounds are required for decoding:

    >>> SpelledInterval("M2:0").onehot((-3,3), (-1,1))
    array([[0, 0, 0],
           [0, 0, 0],
           [0, 0, 0],
           [0, 0, 0],
           [0, 0, 0],
           [0, 1, 0],
           [0, 0, 0]])
    >>> SpelledPitch.from_onehot(np.array([[0,0,0],
    ...                                    [0,0,0],
    ...                                    [0,0,0],
    ...                                    [1,0,0],
    ...                                    [0,0,0]]), -2, 3)
    G3

In the above example, the interval ``M2:0`` (fifth = 2, independent octaves = 0)
is encoded with the fifths dimension (1st dimension, 7 entries) ranging from -3 (``m3``) to 3 (``M6``)
and an octave dimension (2nd, 3 entries) ranging from -1 to 1.
The pitch ``G3`` (fifths = 2, independent octaves = 3)
is encoded with fifths dimension (5 entries) ranging from -2 (``Bb``) to 2 (``D``)
and the octaves dimension (3 entries) ranging from 3 to 5.

.. code-block:: none

   M2:0 (f=2, o=0)

   0  0  0  -3
   0  0  0  -2
   0  0  0  -1
   0  0  0   0 fifth
   0  0  0   1
   0  1  0   2
   0  0  0   3

   -1 0  1
   octave

   G3 (f=1, o=3)

   0  0  0  -2
   0  0  0  -1
   0  0  0   0 fifth
   1  0  0   1
   0  0  0   2

   3  4  5
   octave
    
Reference
---------

General Interface
^^^^^^^^^^^^^^^^^

.. autoclass:: pitchtypes.Spelled
   :members:
   :member-order: bysource

.. autoclass:: pitchtypes.AbstractSpelledInterval
   :members:
   :member-order: bysource

.. autoclass:: pitchtypes.AbstractSpelledPitch
   :members:
   :member-order: bysource

Spelled Interval and Pitch
^^^^^^^^^^^^^^^^^^^^^^^^^^
             
.. autoclass:: pitchtypes.SpelledInterval(string)
   :special-members: __init__
   :members:
   :inherited-members:
   :member-order: bysource

.. autoclass:: pitchtypes.SpelledPitch(string)
   :special-members: __init__
   :members:
   :inherited-members:
   :member-order: bysource

Spelled Interval and Pitch Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
             
.. autoclass:: pitchtypes.SpelledIntervalClass(string)
   :special-members: __init__
   :members:
   :inherited-members:
   :member-order: bysource
                  
.. autoclass:: pitchtypes.SpelledPitchClass(string)
   :special-members: __init__
   :members:
   :inherited-members:
   :member-order: bysource
