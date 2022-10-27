.. pitchtypes documentation master file, created by
   sphinx-quickstart on Mon Nov  8 16:25:49 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pitchtypes's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   types/spelled
   types/enharmonic
   types/frequencies
   types/harmonic
   types/abstractbase
   api_summary


A library for **handling musical pitches and intervals in a systematic way**.
For other (and mostly compatible) implementations see:

- `Pitches.js <https://github.com/DCMLab/Pitches.jl>`_ (Julia)
- `musicology-pitch <https://github.com/DCMLab/haskell-musicology/tree/master/musicology-pitch>`_ (Haskell)
- `purescript-pitches <https://github.com/DCMLab/purescript-pitches>`_ (Purescript)
- `pitches.rs <https://github.com/DCMLab/rust-pitches/blob/main/README.md>`_ (Rust)

Arithmetics
-----------

You can, for instance, compute the interval class between a B♭ and an F♯,
which is an augmented fifth

.. doctest::

   >>> import pitchtypes as pt
   >>> pt.SpelledPitchClass("F#") - pt.SpelledPitchClass("Bb")
   a5

and do all the standard arithmetic operations.

Generic Interface
-----------------

More generally, the library defines **different types of musical intervals and pitches**
as well as a **generic interface** for writing algorithms that work with different
pitch and interval types. This allows you to write generic functions

.. doctest::

   >>> def transposeby(pitches, interval):
   ...     return [pitch + interval for pitch in pitches]

and use them with different pitch types, including :class:`~pitchtypes.SpelledPitch`
(corresponding to written notes in Western notation)

.. doctest::

   >>> transposeby([pt.SpelledPitch("C4"), pt.SpelledPitch("Eb4"), pt.SpelledPitch("G#4")],
   ...             pt.SpelledInterval("m3:0"))
   [Eb4, Gb4, B4]

:class:`~pitchtypes.SpelledPitchClass` (which work the same but ignore octaves)

.. doctest::

   >>> transposeby([pt.SpelledPitchClass("C"), pt.SpelledPitchClass("Eb"), pt.SpelledPitchClass("G#")],
   ...             pt.SpelledIntervalClass("m3"))
   [Eb, Gb, B]

:class:`~pitchtypes.EnharmonicPitch` (corresponding to keys on the piano)

.. doctest::

   >>> transposeby([pt.EnharmonicPitch(60), pt.EnharmonicPitch(63), pt.EnharmonicPitch(68)],
   ...             pt.EnharmonicInterval(3))
   [D#4, F#4, B4]

:class:`~pitchtypes.LogFreqPitch` (i.e. **frequencies** with intervals corresponding to **frequency ratios**)

.. doctest::

   >>> transposeby([pt.LogFreqPitch("261.63Hz"), pt.LogFreqPitch("311.13Hz"), pt.LogFreqPitch("415.30Hz")],
   ...             pt.LogFreqInterval("1.19"))
   [311.34Hz, 370.24Hz, 494.21Hz]

and more.

Type Conversion
---------------

The library also provides **type conversions**, if they are reasonably well defined. For instance,
from :class:`~pitchtypes.SpelledPitch` to :class:`~pitchtypes.EnharmonicPitch`

.. doctest::

   >>> pt.SpelledPitch("F##4").convert_to(pt.EnharmonicPitch)
   G4

or from :class:`~pitchtypes.EnharmonicPitch` to :class:`~pitchtypes.LogFreqPitch`
(assuming twelve-tone equal temperament)

.. doctest::

   >>> pt.EnharmonicPitch("A4").convert_to(pt.LogFreqPitch)
   440.Hz

Installation
------------

To get started, install via pip::

  pip install pitchtypes

For more details on how to use this library, have a look at :doc:`the API overview <introduction>`.


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
