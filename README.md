# ngspice function block helpers

This project provides LTspice-style transient function blocks for ngspice using
custom XSPICE code models plus friendly `.subckt` wrappers.

The initial library targets:

- resettable integration with pulse, rising-edge, or falling-edge reset
- modulo integration
- edge-triggered sample-and-hold
- derivative wrapper around ngspice's built-in `d_dt`
- resettable integration with anti-windup

This project vendors the ngspice-46 source/build tree under `src/ngspice`.
That tree supplies the XSPICE build harness needed to compile the custom
`ngfuncs.cm` library. Simulation uses the installed runtime on PATH, currently
`/home/chaiwichit-sura/.local/bin/ngspice`.

## Layout

- `src/xspice/icm/ngfuncs/` - project XSPICE code-model library source
- `src/ngspice/` - vendored ngspice-46 source/build tree used to build `.cm`
- `lib/ngfuncs.lib` - user-facing `.subckt` wrappers
- `examples/` - runnable example decks after `build/ngfuncs.cm` exists
- `tests/` - ngspice regression decks and test runner
- `scripts/` - helper scripts for source-tree installation and checks
- `docs/` - design and usage notes
- `build/` - expected location for generated `ngfuncs.cm`

## Build

Build the custom code-model library from the vendored ngspice tree:

```sh
make build-cm
make test
```

`make build-cm` copies `src/xspice/icm/ngfuncs` into
`src/ngspice/src/xspice/icm/ngfuncs`, builds `ngfuncs.cm` there, then copies
the result to `build/ngfuncs.cm`.

To use a different source tree, override `NGSPICE_SRC`:

```sh
make build-cm NGSPICE_SRC=/path/to/ngspice-source
```

## Use

Load the code model before circuit parsing and include the wrapper library:

```spice
.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib
```

Then instantiate blocks such as:

```spice
XINT in reset out NG_INT_RISE params: ic=0 gain=1 vth=0.5
XMOD in phase NG_INT_MOD params: ic=0 gain=1 modulus=1
XSAMP signal clk held NG_SAMPLE_RISE params: ic=0 vth=0.5
XDDT in slope NG_DDT params: gain=1
```
