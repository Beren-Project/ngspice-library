# ADR 0001: Stateful functions use custom XSPICE models

## Status

Accepted

## Context

Resettable integration, modulo integration, and edge-triggered sampling require
accepted-timestep state and edge history. Stateless behavioral expressions do
not provide the required lifecycle.

## Decision

Implement these functions as custom XSPICE code models under
`src/xspice/icm/ngfuncs/`. Use analog state vectors and previous accepted state
for edge-sensitive behavior.

## Consequences

- The project needs the ngspice XSPICE build harness.
- Tests must exercise transient state and repeated edges.
- Narrow events remain dependent on transient timestep selection.
