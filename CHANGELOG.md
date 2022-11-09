# Changes

## v0.4.0

### new features

- implement spelled array types
  - vectorized operations (using numpy)
  - supports array interface (indexing, iteration, etc.)
- add one-hot encoding/decoding for all spelled types

### breaking changes

- update definition of "direction" on spelled types
  - now altered unisons have a direction (except the perfect unison) for spelled types
  - `d1:0` is now normalized to `-a1:0` (because `d1:0` is considered downward)
  - compliant with the other libraries
- remove `generic` and `diatonic_steps` from spelled pitch types
  - both don't make sense (conceptually) for pitches
  - potentially leak the underlying interval representation
  - only degree is meaningful for pitches

### improvements

- better docstring formatting (parameters and return values)

### bug fixes

- implement ordering for spelled types in a consistent way
  - add docs
  - fixes bug where `Cb-1 > C-1` was true

## v0.3.0

first version that is compliant with the other libraries
