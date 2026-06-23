# Design Notes

ngspice already has useful primitives:

- B-source `ddt(expr)` for derivative expressions
- XSPICE `d_dt` for a differentiator block
- XSPICE `int` for an integration block with output limits and `out_ic`

The missing behavior includes stateful reset, modulo wrap, edge-triggered
sampling, anti-windup, and reusable analog comparison. The first four
behaviors need accepted timestep state, so they are implemented as custom
XSPICE code models. Smooth comparison can be composed from a stateless
behavioral transfer and ngspice's stock stateful `slew` model.

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

`NG_COMP_SMOOTH_DIFF`

- Wrapper ports: `inp`, `inn`, `out`
- Parameters: `vlow`, `vhigh`, `voffset`, `vsmooth`, `trise`, `tfall`
- Uses a behavioral `tanh` source to produce a continuous target voltage.
- Passes the target through the stock XSPICE `slew` model.

`NG_COMP_SMOOTH_SE`

- Wrapper ports: `in`, `out`
- Parameters: `vth`, `vlow`, `vhigh`, `vsmooth`, `trise`, `tfall`
- Creates an instance-local voltage reference at `vth`.
- Instantiates `NG_COMP_SMOOTH_DIFF` with `voffset=0`.

## Smooth Comparator Transfer

The differential input and target voltage are:

```text
vdiff = V(inp) - V(inn) - voffset
target = vlow + (vhigh-vlow)/2
         * (1 + tanh(2.197224577 * vdiff / vsmooth))
```

The factor `2.197224577` is `2*atanh(0.8)`. It places the 10% and 90%
output points at `vdiff=-vsmooth/2` and `vdiff=+vsmooth/2`.

Configured full-scale 10-90% transition times are converted to the stock
model's voltage-per-second limits:

```text
rise_slope = 0.8 * (vhigh-vlow) / trise
fall_slope = 0.8 * (vhigh-vlow) / tfall
```

The behavioral transfer has no memory and creates no events. The slew stage
owns the dynamic state, so the complete comparator remains analog and
continuous. Internal target, threshold, and model names are scoped by their
subcircuit instances.

Required constraints are `vsmooth>0`, `trise>0`, `tfall>0`, and
`vhigh>vlow`. Invalid values are documented as unsupported rather than
clamped or rewritten. Propagation delay and hysteresis are intentionally
outside the first-version scope.

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
