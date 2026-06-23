# Architecture

## Project boundary

Project-owned model and wrapper sources are:

- `src/xspice/icm/ngfuncs/`: canonical custom XSPICE source
- `lib/ngfuncs.lib`: public `.subckt` wrappers
- `tests/`: regression and stock smoke decks
- `examples/`: runnable usage decks

`src/ngspice/` is a vendored ngspice 46 source/build tree. Its stock devices,
examples, and Verilog-A files are upstream material, not project-supported
devices.

## Backend architecture

```mermaid
flowchart LR
    USER["User netlist"] --> WRAP["lib/ngfuncs.lib wrappers"]
    WRAP --> CUSTOM["Custom wrappers"]
    WRAP --> STOCK["Stock-only wrappers"]
    CUSTOM --> CM["build/ngfuncs.cm"]
    CM --> RST["ng_int_rst"]
    CM --> MOD["ng_int_mod"]
    CM --> SAMPLE["ng_sample"]
    STOCK --> ANALOG["Stock analog code models"]
    ANALOG --> DDT["d_dt"]
    ANALOG --> SLEW["slew"]
```

Custom stateful functions use project code models. The derivative and
comparator families compose existing stock ngspice facilities.

## Wrapper expansion

```mermaid
flowchart LR
    X["Xint in rst out NG_INT_RISE"] --> SUB["NG_INT_RISE subcircuit"]
    SUB --> A["aint in rst out ng_int_rise_m"]
    A --> MODEL["ng_int_rise_m type ng_int_rst"]
    MODEL --> C["ucm_ng_int_rst"]
```

The wrapper fixes internal selector parameters such as `mode` and
`aw_enable`, while exposing the public parameter set.

## Stateful model design

The custom models store transient state through XSPICE analog state vectors.
Edge-sensitive behavior compares the current trigger classification with the
previous accepted timestep, not merely the previous solver call. This avoids
committing trial-timestep edges.

The reset and sample implementations also allocate `STATE_TRIG_RAW`, but the
current code never reads it. It is not part of the active edge-detection path.

## Build flow

```mermaid
flowchart TD
    MAKE["make build-cm"] --> INSTALL["make install-source"]
    SRC["src/xspice/icm/ngfuncs"] --> INSTALL
    LIST["modpath.lst"] --> INSTALL
    INSTALL --> COPY["src/ngspice/src/xspice/icm/ngfuncs"]
    INSTALL --> MF["GNUmakefile and GNUmakefile.in CMDIRS"]
    COPY --> BUILD["Vendored XSPICE build"]
    MF --> BUILD
    BUILD --> INNER["Vendored ngfuncs.cm"]
    INNER --> OUT["build/ngfuncs.cm"]
```

The vendored tree supplies generated headers, build rules, and XSPICE support
that are not provided by `cmpp` alone.

## Durable decisions

- [Stateful functions use custom XSPICE models](adr/0001-stateful-functions-use-custom-xspice.md)
- [Public wrappers may compose custom and stock models](adr/0002-public-wrappers-and-stock-composition.md)
- [The project vendors an ngspice build harness](adr/0003-vendored-ngspice-build-harness.md)
