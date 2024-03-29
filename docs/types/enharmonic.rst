Enharmonic Pitch
================

**Note: This type is functional and tested, but it does not yet conform to
the general API and the documentation is still incomplete.**

Overview
--------

Enharmonic pitches and intervals are specified in 12-TET semitones, with 60 as Middle C, as in the MIDI standard.
Both enharmonic pitches and intervals can be represented by integers,
However, we provides wrapper classes around `int` to distinguish
the different interpretations as pitches and intervals (and their respective class variants).
Enharmonic pitches can be easily created using the `Enharmonic*` constructors, all of which take integers.

+---------------------------------+--------------------------+
| constructor example             | printed representation   |
+=================================+==========================+
| ``EnharmonicInterval(15)``      | ``i15``                  |
| ``EnharmonicIntervalClass(15)`` | ``ic3``                  |
| ``EnharmonicPitch(60)``         | ``p60``                  |
| ``EnharmonicPitchClass(60)``    | ``pc0``                  |
+---------------------------------+--------------------------+


Reference
---------

.. autoclass:: pitchtypes.Enharmonic
   :members:

.. autoclass:: pitchtypes.EnharmonicPitch
   :members:

.. autoclass:: pitchtypes.EnharmonicInterval
   :members:

.. autoclass:: pitchtypes.EnharmonicPitchClass
   :members:

.. autoclass:: pitchtypes.EnharmonicIntervalClass
   :members:
