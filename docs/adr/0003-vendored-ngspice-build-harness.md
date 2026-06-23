# ADR 0003: Vendor the ngspice build harness

## Status

Accepted

## Context

Building a dynamic XSPICE code-model library requires generated headers,
makefile fragments, and support files from an ngspice source tree. Installed
runtime packages and `cmpp` alone are insufficient.

## Decision

Keep an ngspice 46 source/build tree under `src/ngspice/`. Copy canonical
project model sources into that tree during `make build-cm`, build there, and
copy the resulting library to `build/ngfuncs.cm`.

## Consequences

- The vendored tree is build infrastructure, not the project device catalog.
- Canonical project model sources remain outside the vendored tree.
- Runtime and source versions should remain aligned.
