# ngspice function block helpers

This project provides reusable transient function blocks for ngspice through
custom XSPICE code models and user-facing `.subckt` wrappers.

Supported families include resettable and modulo integrators, sample-and-hold,
a derivative wrapper, and smooth analog comparators.

## Quick start

Build the custom code-model library and run the regression suite:

```sh
make build-cm
make test
make check-stock
```

Load `ngfuncs.cm` before circuit parsing when using a custom model, then include
the wrapper library:

```spice
.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib

XINT in reset out NG_INT_RISE params: ic=0 gain=1 vth=0.5
```

`NG_DDT` and the smooth comparator wrappers use stock ngspice code models.
They need `lib/ngfuncs.lib`, but do not require `build/ngfuncs.cm`.

## Documentation

- [Documentation index](docs/index.md)
- [Device catalog](docs/device-catalog.md)
- [Library usage](docs/library-usage.md)
- [Validation guide](docs/validation-guide.md)
- [Development guide](docs/development.md)

The canonical custom-model sources are under `src/xspice/icm/ngfuncs/`.
`src/ngspice/` is a vendored ngspice 46 source tree used as the build harness.
