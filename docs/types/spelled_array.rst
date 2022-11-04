Spelled Interval and Pitch Arrays
=================================

Overview
--------

With large datasets, it is often necessary or convenient to represent and process them
in vectorized form, for example in ``numpy`` arrays.
Putting spelled pitches or intervals directly in a ``numpy`` array
does not have any performance benefits
since numpy has no support for the operations between these types.
However, the underlying representation of pitches is numeric and most operations on them
directly translate to arithmetics on the underlying numbers.

This module provides vectorized types for spelled interval and pitch arrays.
They correspond to the types in the :doc:`pitchtypes.spelled <spelled>` module
and generally share the same interface.
Internally, spelled array types use ``numpy`` arrays to encode their data
and implement all of their arithmetic operations in vectorized form.
The main exception to native vectorization is printing and parsing,
which means that those should be handled with care on large datasets.

Array Creation
--------------

From Numeric Arrays
^^^^^^^^^^^^^^^^^^^

The default way to construct a spelled array is by directly providing its underlying arrays
of fifths and (dependent) octaves as a numpy array
or something that supports the same interface such as a pandas series.

    >>> from pitchtypes import *
    >>> import numpy as np
    >>> SpelledIntervalClassArray(np.array([1,2,3]))
    asic(['P5', 'M2', 'M6'])
    >>> SpelledPitchClassArray(np.arange(3))
    aspc(['C', 'G', 'D'])
    >>> SpelledIntervalArray(np.arange(1,4), np.array([0,-1,-1]))
    asi(['P5:0', 'M2:0', 'M6:0'])
    >>> import pandas as pd
    >>> df = pd.DataFrame({'fifths': [1,2,3], 'octaves':[4,3,3]})
    >>> SpelledPitchArray(df.fifths, df.octaves)
    asp(['G4', 'D4', 'A4'])

If the data is given using *independent* octaves
(e.g., derived from the name and octave of a pitch),
intervals and pitches can also be constructed from those using
the class method ``from_independent(fifths, octaves)``.
This is usually more natural for pitches than for intervals

    >>> SpelledPitchArray.from_independent(np.array([1,2,3]), np.array([4,4,4]))
    asp(['G4', 'D4', 'A4'])
    >>> SpelledIntervalArray.from_independent(np.array([-2,-1,0,1,2]), np.array([0,0,0,0,0]))
    asi(['m7:0', 'P4:0', 'P1:0', 'P5:0', 'M2:0'])

From String Arrays
^^^^^^^^^^^^^^^^^^
    
Spelled arrays can also be created from arrays of strings using the ``from_strings(strings)`` class method.
Note that the parsing is done entirely in Python and thus can be slow on large datasets.

    >>> SpelledIntervalArray.from_strings(["M2:0", "-P4:1"])
    asi(['M2:0', '-P4:1'])
    >>> SpelledPitchClassArray.from_strings([["Db", "D", "D#"], ["Eb", "E", "E#"]])
    aspc([['Db', 'D', 'D#'],
     ['Eb', 'E', 'E#']])

Shorthands
^^^^^^^^^^

When writing code that uses spelled array types,
you should generally use one of the above methods for creating spelled arrays,
as they make the intention of the code clear.
However, for quickly testing or trying something in an interactive way,
there are shortcut functions that accept arrays or nested lists
of both strings and numeric fifths/octaves values.

    >>> asi(["aaa1:1"])
    asi(['aaa1:1'])
    >>> asi([21], [-11])
    asi(['aaa1:1'])
    >>> asic(["aaa1"])
    asic(['aaa1'])
    >>> asic([21])
    asic(['aaa1'])
    >>> asp(["A##4", "C5"])
    asp(['A##4', 'C5'])
    >>> asp([17, 0], [-5, 5])
    asp(['A##4', 'C5'])
    >>> aspc(["A##", "C"])
    aspc(['A##', 'C'])
    >>> aspc([17, 0])
    aspc(['A##', 'C'])

Working with Spelled Arrays
---------------------------

Array Return Values
^^^^^^^^^^^^^^^^^^^

Most methods on spelled arrays now return either another spelled array
or a numeric array:

    >>> asi(["P1:0", "M3:0", "-m2:1"]).direction()
    array([ 0,  1, -1])
    >>> abs(asi(["P1:0", "M3:0", "-m2:1"]))
    asi(['P1:0', 'M3:0', 'm2:1'])
    >>> cs = aspc(["C", "C#", "C##", "Cb"])
    >>> cs.alteration()
    array([ 0,  1,  2, -1])
    >>> cs.degree()
    array([0, 0, 0, 0])
    >>> cs.letter()
    array(['C', 'C', 'C', 'C'], dtype='<U1')

Regular spelled types can be converted to a string representation using :py:func:`str`.
Calling :py:func:`str` or `py:func:`repr` on spelled arrays also works
but returns one string for the full array.
If you want instead to get an array of strings
(one for each pitch or interval in the original array),
you can use the method :py:func:`name() <pitchtypes.SpelledArray.name>`.

    >>> unisons = asi([0, 7, 14, 21], [0, -4, -8, -12])
    >>> unisons
    asi(['P1:0', 'a1:0', 'aa1:0', 'aaa1:0'])
    >>> str(unisons)
    '[P1:0 a1:0 aa1:0 aaa1:0]'
    >>> print(unisons)
    [P1:0 a1:0 aa1:0 aaa1:0]
    >>> unisons.name()
    array(['P1:0', 'a1:0', 'aa1:0', 'aaa1:0'], dtype='<U6')

Special Intervals
^^^^^^^^^^^^^^^^^

For special intervals such as :py:func:`unison() <pitchtypes.Interval.unison>`,
:py:func:`octave() <pitchtypes.Interval.octave>`,
and :py:func:`chromatic_semitone() <pitchtypes.Chromatic.chromatic_semitone>`,
you now have to provide a shape:

    >>> print(SpelledIntervalArray.unison(12))
    [P1:0 P1:0 P1:0 P1:0 P1:0 P1:0 P1:0 P1:0 P1:0 P1:0 P1:0 P1:0]
    >>> print(SpelledIntervalClassArray.chromatic_semitone((3,5)))
    [[a1 a1 a1 a1 a1]
     [a1 a1 a1 a1 a1]
     [a1 a1 a1 a1 a1]]

Reference
---------

.. autofunction:: pitchtypes.asi
.. autofunction:: pitchtypes.asic
.. autofunction:: pitchtypes.asp
.. autofunction:: pitchtypes.aspc

General Interface
^^^^^^^^^^^^^^^^^

.. autoclass:: pitchtypes.SpelledArray()
   :members:
   :inherited-members:
   :member-order: bysource

Spelled Interval and Pitch
^^^^^^^^^^^^^^^^^^^^^^^^^^
             
.. autoclass:: pitchtypes.SpelledIntervalArray
   :special-members: __init__
   :members:
   :inherited-members:
   :member-order: bysource

.. autoclass:: pitchtypes.SpelledPitchArray(fifths, octaves)
   :special-members: __init__
   :members:
   :inherited-members:
   :member-order: bysource

Spelled Interval and Pitch Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
             
.. autoclass:: pitchtypes.SpelledIntervalClassArray(fifths)
   :special-members: __init__
   :members:
   :inherited-members:
   :member-order: bysource

.. autoclass:: pitchtypes.SpelledPitchClassArray(fifths)
   :special-members: __init__
   :members:
   :inherited-members:
   :member-order: bysource
             
