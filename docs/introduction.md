# Overview

The idea behind this library is that the central object is the *interval*.
Pitches are derived from intervals by interpreting them with respect to a reference point.
This is much like the relation between vectors (= intervals) and points (= pitches).
For example, the pitch ``E♭4`` can be represented as an interval (e.g. a minor third, ``m3:0``)
above a reference pitch such as Middle C (``C4``).
Intervals and Pitches come in families of four variants:
* `*Interval` represents a normal interval
* `*Pitch` represents a normal pitch
* `*IntervalClass` represents an interval with octave equivalence
* `*PitchClass` represents a pitch with octave equivalence

Similar to vectors and points, intervals and pitches support a number of operations
such as addition and scalar multiplication.

The following representations of intervals and pitches are implemented so far:

* [spelled](types/spelled): based on Western notation
* [enharmonic](types/enharmonic): based on the chromatic 12-tone system
* [frequency](types/frequencies): based on the frequency of a sound wave

## Generic Operations

**TODO: check that implementation is complete and fix names!**

The operations of the generic interface are based on intervals as the fundamental elements.
Intervals can be thought of as vectors in a vector space (or more precisely: a module over integers).
They can be added, subtracted, negated, and multiplied with integers.
Pitches, on the other hand, can be seen as points in this space and are represented as intervals
in relation to an (implicit) origin.

Interval types (here denoted as `I`) define the following operations:

- `I + I`
- `I - I`
- `-I`
- `I * Integer`
- `Integer * I`
- `sign(I)`
- `abs(I)`

The sign indicates the logical direction of the interval by musical convention
(upward = positive, downward = negative),
even if the interval space is multi-dimensional.
Consequently, `abs` ensures that an interval is neutral or upward-directed.
For interval classes (which are generally undirected),
the sign indicates the direction of the "shortest" class member:

```
julia> sign(i"P4")
1

julia> sign(i"P5") # == -i"P4"
-1
```

In addition to arithmetic operations, some special intervals are defined:

- `unison(Type{I})` / `zero(Type{I})`
- `octave(Type{I})`
- `chromsemi(Type{I})` (a chromatic semitone, optional)
- `isstep(I)` (optional, a predicate that test whether the interval is considered a "step")

Finally, some operations specify the relationship between intervals and interval classes:

- `ic(I)`: Returns the corresponding interval class.
- `embed(IC [, octs::Int])`: Returns a canonical embedding of an interval class into interval space.
- `intervaltype(Type{IC}) = I`
- `intervalclasstype(Type{I}) = IC`

Pitch operations generally interact with intervals
(and can be derived from the interval operations):

- `P + I -> P`
- `I + P -> P`
- `P - I -> P`
- `P - P -> I`
- `pc(P) -> PC`
- `embed(PC [, octaves]) -> P`

Besides the specific functions of the interface,
pitch and interval types generally implement basic functions such as

- `isless`
- `isequal`
- `hash`
- `show` (usually also specialized for `Pitch{I}`)

Note that the ordering of pitches is generally not unique,
so `isless` uses an appropriate convention for each interval type.

