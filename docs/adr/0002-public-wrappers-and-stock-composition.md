# ADR 0002: Public wrappers may compose custom and stock models

## Status

Accepted

## Context

Users need consistent `.subckt` interfaces, but not every function requires
project C code. ngspice already supplies `d_dt` and `slew`.

## Decision

Expose all public devices through `lib/ngfuncs.lib`. Back stateful functions
with custom `ngfuncs.cm` models, and compose stock primitives for derivative
and smooth comparator wrappers.

## Consequences

- Public interface ownership remains centralized in one library.
- Stock-only wrappers do not require `ngfuncs.cm`.
- Validation must distinguish direct wrapper tests from raw stock smoke tests.
