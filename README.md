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

Start with [docs/project-guide.md](docs/project-guide.md) when returning to
this project after a break. It explains the project purpose, file ownership,
build flow, tests, generated files, and common failure modes.

## Build

Build the custom code-model library from the vendored ngspice tree:

```sh
make build-cm
make test
```

`make build-cm` copies `src/xspice/icm/ngfuncs` into
`src/ngspice/src/xspice/icm/ngfuncs`, builds `ngfuncs.cm` there, then copies
the result to `build/ngfuncs.cm`.

`make test` runs the regression decks and writes a self-contained HTML report
with pass/fail status, measurements, waveform plots, ngspice logs, and the
source netlist for each test:

```sh
tests/output/report/index.html
```

The regression decks are intentionally split by device/behavior:

- `test_integrator_reset_pulse.cir` - level-sensitive reset with repeated pulses
- `test_integrator_reset_rise.cir` - rising-edge reset with repeated pulses
- `test_integrator_reset_fall.cir` - falling-edge reset with repeated pulses
- `test_integrator_modulo.cir` - modulo reset
- `test_sample_rise.cir` - repeated rising-edge samples
- `test_sample_fall.cir` - repeated falling-edge samples
- `test_integrator_antiwindup_pulse.cir` - anti-windup clamp, reverse input recovery, and pulse reset
- `test_derivative.cir` - derivative wrapper

For `NG_INT_AW_PULSE`, `vth` is the reset threshold and `ic` is the reset
output value. For example, `params: ic=0 ... vth=0.5` resets to `0 V` while
`rst` is above `0.5 V`; a `1 V` reset pulse is only the trigger level, not the
reset output level.

To use a different source tree, override `NGSPICE_SRC`:

```sh
make build-cm NGSPICE_SRC=/path/to/ngspice-source
```

## Git

This workspace has a read-only `.git` mount, so the project repository uses
`.repo.git`. Use the helper script for normal Git commands:

```sh
scripts/project-git.sh status
scripts/project-git.sh log --oneline
```

## Use

See [docs/devices.md](docs/devices.md) for the full device reference,
parameter meanings, and copyable netlist examples.

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
