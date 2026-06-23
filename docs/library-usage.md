# Library usage

## Dependencies

All public devices are `.subckt` wrappers in
[`lib/ngfuncs.lib`](../lib/ngfuncs.lib).

Custom-model wrappers require both files:

| Wrapper families | Required files |
| --- | --- |
| Resettable integrators, modulo integrator, sample-and-hold | `build/ngfuncs.cm` and `lib/ngfuncs.lib` |
| `NG_DDT`, smooth comparators | `lib/ngfuncs.lib`; stock ngspice `analog.cm` support |

## Custom-model load order

`pre_codemodel` must run before ngspice parses instances of custom models:

```spice
.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib

Vin in 0 dc 1
Vrst rst 0 pulse(0 1 1m 1u 1u 100u 2m)
X1 in rst out NG_INT_RISE params: ic=0 gain=1 vth=0.5

Rin in 0 1G
Rrst rst 0 1G
Rout out 0 1G

.tran 10u 5m
.end
```

High-value resistors provide DC paths for voltage-mode XSPICE pins.

## Stock-only wrappers

`NG_DDT`, `NG_COMP_SMOOTH_DIFF`, and `NG_COMP_SMOOTH_SE` do not add code to
`ngfuncs.cm`:

```spice
.include lib/ngfuncs.lib

Vin in 0 pwl(0 0 1m 1)
X1 in slope NG_DDT params: gain=1
Rin in 0 1G
Rout slope 0 1G

.tran 1u 1m
.end
```

## Building

```sh
make build-cm
```

The target copies canonical sources from `src/xspice/icm/ngfuncs/` into the
vendored ngspice build tree, invokes its XSPICE build harness, and writes
`build/ngfuncs.cm`.

Override the source tree if needed:

```sh
make build-cm NGSPICE_SRC=/path/to/ngspice-source
```

## Transient timestep guidance

Reset and sample edges must be observable by the transient solver. Use finite
source rise/fall times and a maximum timestep small enough to resolve them.
Comparator simulations should use a maximum timestep substantially shorter
than the smallest configured `trise` or `tfall`.
