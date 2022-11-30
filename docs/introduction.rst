Overview
========

The idea behind this library is that the central object is the *interval*.
Pitches are derived from intervals by interpreting them with respect to a reference point.
This is much like the relation between vectors (= intervals) and points (= pitches).
For example, the pitch ``E♭4`` can be represented as an interval (e.g. a minor third, ``m3:0``)
above a reference pitch such as Middle C (``C4``).
Intervals and Pitches come in families of four variants:

* ``*Interval`` represents a normal interval
* ``*Pitch`` represents a normal pitch
* ``*IntervalClass`` represents an interval with octave equivalence
* ``*PitchClass`` represents a pitch with octave equivalence

Similar to vectors and points, intervals and pitches support a number of operations
such as addition and scalar multiplication.

The following representations of intervals and pitches are implemented so far:

* :doc:`spelled <types/spelled>`: based on Western notation
* :doc:`spelled <types/spelled_array>`: based on Western notation
* :doc:`enharmonic <types/enharmonic>`: based on the chromatic 12-tone system (*)
* :doc:`frequency <types/frequencies>`: based on the frequencies and frequency ratios (*)
* :doc:`harmonic <types/harmonic>`: based prime-factorized just intervals (*)

(*): The interfaces for these types are not yet standardized/synchronized with the implementations in other languages
and lack detailed documentation.
They implement the basic pitch/interval interface,
but type-specific details (notation etc.) might change in the future.

Generic Operations
------------------

The operations of the generic interface are based on intervals as the fundamental elements.
Intervals can be thought of as vectors in a vector space (or more precisely: a module over integers).
They can be added, subtracted, negated, and multiplied with integers.
Pitches, on the other hand, can be seen as points in this space and are represented as intervals
in relation to an (implicit) origin.

Intervals. (here denoted as `i`) support the following operations:

- ``i + i``
- ``i - i``
- ``-i``
- ``i * int``
- ``int * i``
- :py:meth:`i.direction() <pitchtypes.Interval.direction>`
- :py:meth:`i.abs() <pitchtypes.Interval.abs>`

:py:meth:`i.direction() <pitchtypes.Interval.direction>`
indicates the logical direction of the interval by musical convention
(upward = positive, downward = negative),
even if the interval space is multi-dimensional.
Consequently, :py:meth:`i.abs() <pitchtypes.Interval.abs>`
ensures that an interval is neutral or upward-directed.
For interval classes (which are generally undirected),
the sign indicates the direction of the "shortest" class member:

.. testsetup::

  from pitchtypes import SpelledIntervalClass

.. doctest::

  >>> SpelledIntervalClass("P4").direction()
  1
  >>> SpelledIntervalClass("P5").direction() # == -"P4"
  -1

In addition to arithmetic operations, some special intervals are defined:

- :py:meth:`I.unison() <pitchtypes.Interval.unison>`
- :py:meth:`I.octave() <pitchtypes.Interval.octave>`
- :py:meth:`I.chromatic_semitone() <pitchtypes.Chromatic.chromatic_semitone>` (a chromatic semitone, optional)
- :py:meth:`i.is_step() <pitchtypes.Diatonic.is_step>` (optional, a predicate that test whether the interval is considered a "step")

Finally, some operations specify the relationship between intervals and interval classes:

- :py:meth:`i.ic() <pitchtypes.Interval.unison>`: Returns the corresponding interval class.
- :py:meth:`i.embed() <pitchtypes.Interval.embed>`: Returns a canonical embedding of an interval class into interval space.

Pitch operations generally interact with intervals
(and can be derived from the interval operations):

- ``p + i -> p``
- ``i + p -> p``
- ``p - i -> p``
- ``p - p -> i``
- :py:meth:`p.pc() -> pc <pitchtypes.Pitch.pc>`
- :py:meth:`pc.embed() -> p <pitchtypes.Pitch.embed>`

Besides the specific functions of the interface,
pitch and interval types generally implement basic functions such as

- equality
- comparison
- hashing
- printing in standard notation

Note that the ordering of pitches is generally not unique,
so comparison uses an appropriate convention for each interval type.
If you need musically valid comparisons,
use semantic methods such as :py:meth:`direction() <pitchtypes.Interval.direction>` as appropriate to your use case.

Reference
---------

Intervals
^^^^^^^^^

.. autoclass:: pitchtypes.Interval
   :members:

.. autoclass:: pitchtypes.Chromatic
   :members:

.. autoclass:: pitchtypes.Diatonic
   :members:

Pitches
^^^^^^^

.. autoclass:: pitchtypes.Pitch
   :members:
