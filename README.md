# ngspice-library

Reusable XSPICE code models and subcircuit wrappers for ngspice transient simulation.

This project provides reusable transient function blocks for ngspice through
custom XSPICE code models and user-facing `.subckt` wrappers.

Supported families include resettable and modulo integrators, sample-and-hold,
a derivative wrapper, and smooth analog comparators.

## Quick start

For wrappers built only from stock ngspice models, include the library:

```spice
.include lib/ngfuncs.lib

XDDT in out NG_DDT params: gain=1
```

For wrappers backed by custom XSPICE models, load the code-model library before
circuit parsing, then include the wrapper library:

```spice
.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib

XINT in reset out NG_INT_RISE params: ic=0 gain=1 vth=0.5
```

Build the custom code-model library and run checks with:

```sh
make build-cm
make test
make check-stock
```

`NG_DDT` and the smooth comparator wrappers use stock ngspice code models. They
need `lib/ngfuncs.lib`, but do not require `build/ngfuncs.cm`.

Resettable integrators, anti-windup integrators, modulo integrators, and
sample-and-hold wrappers use custom XSPICE models. They require both
`pre_codemodel build/ngfuncs.cm` and `.include lib/ngfuncs.lib`.

## Repository layout

- `lib/` contains the public `.subckt` wrapper library.
- `src/xspice/icm/ngfuncs/` contains canonical custom XSPICE code-model source.
- `examples/` contains runnable usage decks.
- `tests/` contains regression and smoke-test decks.
- `docs/` contains device, usage, validation, and development documentation.
- `build/` contains generated or prebuilt runtime artifacts such as
  `build/ngfuncs.cm`.
- `src/ngspice/` contains a vendored ngspice 46 source tree used as the current
  custom code-model build harness.

## Vendored ngspice build harness

The project currently keeps `src/ngspice/` in-tree so `make build-cm` can copy
the canonical `ngfuncs` model source into ngspice's XSPICE code-model tree and
build `build/ngfuncs.cm` with the matching ngspice build system. This is a
build harness and upstream reference, not the canonical location for project
model source.

The vendored tree may be replaced later by a git submodule or a build-time
download script. No submodule migration has been performed in this repository
cleanup pass.

## Project status

This is an early personal engineering library. Public wrapper names, parameters,
validation coverage, and build packaging may change as the library matures.

## Documentation

- [Documentation index](docs/index.md)
- [Device catalog](docs/device-catalog.md)
- [Library usage](docs/library-usage.md)
- [Validation guide](docs/validation-guide.md)
- [Development guide](docs/development.md)

The canonical custom-model sources are under `src/xspice/icm/ngfuncs/`.
`src/ngspice/` is a vendored ngspice 46 source tree used as the build harness.

## License

License is not finalized yet.

TODO: Choose a license before encouraging public reuse.
