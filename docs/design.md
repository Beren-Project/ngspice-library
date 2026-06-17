# Design Notes

ngspice already has useful primitives:

- B-source `ddt(expr)` for derivative expressions
- XSPICE `d_dt` for a differentiator block
- XSPICE `int` for an integration block with output limits and `out_ic`

The missing behavior is stateful reset, modulo wrap, edge-triggered sampling,
and anti-windup in reusable transient blocks. These behaviors need accepted
timestep state, so they are implemented as XSPICE code models rather than
arbitrary-source expressions.

## Models

`ng_int_rst`

- Ports: `in`, `rst`, `out`
- Parameters: `mode`, `ic`, `gain`, `vth`, `vhyst`, `lo`, `hi`, `limit_range`,
  `aw_enable`
- `mode=0`: level-active pulse reset
- `mode=1`: rising-edge reset
- `mode=2`: falling-edge reset

`ng_int_mod`

- Ports: `in`, `out`
- Parameters: `ic`, `gain`, `modulus`, `lo`, `hi`, `limit_range`
- Wraps to `ic` when the integrated result reaches `ic + modulus`.

`ng_sample`

- Ports: `in`, `trig`, `out`
- Parameters: `edge`, `ic`, `vth`, `vhyst`
- `edge=1`: sample on rising edge
- `edge=2`: sample on falling edge

## Trigger Semantics

Trigger inputs are ordinary analog voltage pins. With no hysteresis,
`V(trigger) >= vth` is high. With hysteresis, the high threshold is
`vth + vhyst/2` and the low threshold is `vth - vhyst/2`.

Edge-triggered blocks compare the current trigger level with the previous
accepted transient state (`cm_analog_get_ptr(tag, 1)`). That matters because
ngspice may evaluate a model several times at one timestep, or abandon a trial
timestep; updating edge memory from trial calls can otherwise lose the edge.

Very narrow pulses still require the simulator to evaluate or bracket the
transition. No model can detect a pulse that is completely skipped by transient
timestep selection, so practical decks should keep reset and sampling pulses
wide enough for the selected `.tran` step control.

## Build Dependency Layout

The project keeps the ngspice-46 source/build tree in `src/ngspice` so custom
XSPICE code models can be rebuilt without depending on an external source
checkout. The installed runtime at `/home/chaiwichit-sura/.local/bin/ngspice`
is used for simulation.

`cmpp` alone is not enough to build `ngfuncs.cm`; the dynamic code-model build
also needs ngspice's XSPICE build files and headers. `make build-cm` uses the
vendored tree for those files and copies the generated library to
`build/ngfuncs.cm`.
