Log-Frequency Pitch
===================

**Note: This type is functional and tested, but it does not yet conform to
the general API and the documentation is still incomplete.**

**TODO: examples from Julia implementation, adapt to python**

Overview
--------

Pitches and intervals can also be expressed
as physical frequencies and freqency ratios, respectively.
We provide wrappers around `Float64` that represent log frequencies and log freqency ratios,
and perform arithmetic with and without octave equivalence.
There are two versions of each constructor depending on whether you provide log or non-log values.
All values are printed as non-log.
Pitch and interval classes are printed in brackets to indicate that they are representatives of an equivalence class.

  julia> freqi(3/2)
  fr1.5
  
  julia> logfreqi(log(3/2))
  fr1.5
  
  julia> freqic(3/2)
  fr[1.5]
  
  julia> freqp(441)
  441.0Hz
  
  julia> freqpc(441)
  [1.7226562500000004]Hz

Because of the use of floats, rounding errors can occur:

  julia> freqp(440)
  439.99999999999983Hz

You can use Julia's builtin method `isapprox`/`≈` to test for approximate equality:

  julia> freqp(220) + freqi(2) ≈ freqp(440)
  true


Reference
---------

.. autoclass:: pitchtypes.LogFreq
   :members:

.. autoclass:: pitchtypes.LogFreqPitch
   :members:

.. autoclass:: pitchtypes.LogFreqInterval
   :members:

.. autoclass:: pitchtypes.LogFreqPitchClass
   :members:

.. autoclass:: pitchtypes.LogFreqIntervalClass
   :members:
