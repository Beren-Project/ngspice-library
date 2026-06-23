# Model authoring guide

## Choose an implementation type

Use a custom XSPICE model when behavior requires accepted-timestep state,
edge memory, or integration logic unavailable from a stock primitive.

Use a wrapper-only implementation when stock ngspice primitives can express
the behavior without project C code.

## Custom XSPICE model checklist

1. Add `src/xspice/icm/ngfuncs/<model>/ifspec.ifs`.
2. Add `cfunc.mod` in the same directory.
3. Add the directory to `src/xspice/icm/ngfuncs/modpath.lst`.
4. Add a public wrapper to `lib/ngfuncs.lib`.
5. Add focused regression decks under `tests/`.
6. Add or update a runnable example under `examples/`.
7. Update the device catalog and a family page under `docs/devices/`.
8. Add structure and, where useful, signal-flow Mermaid diagrams.
9. Run the validation procedure.

## Wrapper-only checklist

1. Add the wrapper to `lib/ngfuncs.lib`.
2. Cite the stock primitive and its source interface.
3. Add direct wrapper validation, not only a raw primitive smoke test.
4. Add an example and device documentation.
5. Run `make test` and `make check-stock` where applicable.

## Interface rules

- The `.subckt` pin order is the public pin order.
- Wrapper defaults must be documented even when they override stock-model
  defaults.
- Distinguish declared XSPICE limits from caller-required constraints.
- XSPICE parameter limits may warn and clamp rather than reject input.
- Do not describe a parameter as functional unless implementation reads it.
- Mark unvalidated combinations as `NEEDS_VERIFICATION`.

## Device-page template

Each family page must provide, per public wrapper:

- name, purpose, and status
- source and backing primitive/model/subcircuit
- minimal ngspice usage
- exact pin order
- parameters, units, defaults, ranges, enforcement, and notes
- behavior derived from source
- structure diagram
- signal-flow diagram when state/control paths are non-obvious
- example link
- validation link and status
- limitations and `NEEDS_VERIFICATION` items
