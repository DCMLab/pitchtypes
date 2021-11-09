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


A library for handling musical pitches and intervals in a systematic way.
For other (and mostly compatible) implementations see:

- `Pitches.js <https://github.com/DCMLab/Pitches.jl>`_ (Julia)
- `musicology-pitch <https://github.com/DCMLab/haskell-musicology/tree/master/musicology-pitch>`_ (Haskell)
- `purescript-pitches <https://github.com/DCMLab/purescript-pitches>`_ (Purescript)
- `pitches.rs <https://github.com/DCMLab/rust-pitches/blob/main/README.md>`_ (Rust)

This library defines types for musical intervals and pitches
as well as a generic interface for writing algorithms
that work with different pitch and interval types:

.. testcode::

   import pitchtypes as pt

   # write a generic function

   def transposeby(pitches, interval):
     return [pitch + interval for pitch in pitches]

   # use it with different pitch types

   # spelled pitches correspond to written notes in Western notation
   spelled_pitches = [pt.SpelledPitch(p) for p in ["C4", "Eb4", "G#4"]]
   print(transposeby(spelled_pitches, pt.SpelledInterval("m3:0")))

   # spelled pitch classes work the same but they ignore octaves
   spelled_pitch_classes = [pt.SpelledPitchClass(p) for p in ["C", "Eb", "G#"]]
   print(transposeby(spelled_pitch_classes, pt.SpelledIntervalClass("m3")))

   # enharmonic pitches correspond to keys on the piano
   enharmonic_pitches = [pt.EnharmonicPitch(p) for p in [60, 63, 68]]
   print(transposeby(enharmonic_pitches, pt.EnharmonicInterval(3)))

Output:

.. testoutput::

   [Eb4, Gb4, B4]
   [Eb, Gb, B]
   [D#4, F#4, B4]

To get started, install this library via pip::

  pip install pitchtypes

For more details on how to use this library, have a look at :doc:`the API overview <introduction>`.


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
