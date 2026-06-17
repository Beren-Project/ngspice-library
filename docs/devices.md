# Device Reference

This project exposes ngspice function blocks as `.subckt` wrappers in
`lib/ngfuncs.lib`. Load the compiled code-model library before parsing the
netlist, then include the wrapper library:

```spice
.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib
```

The custom blocks are transient-behavior blocks. Use them in `.tran`
simulation.

## Trigger Inputs

Reset and sample trigger pins are ordinary analog voltage pins.

- With `vhyst=0`, the trigger is high when `V(trigger) >= vth`.
- With `vhyst>0`, the rising threshold is `vth + vhyst/2` and the falling
  threshold is `vth - vhyst/2`.
- Pulse-reset variants are level-sensitive: the block resets while the trigger
  is high.
- Rising-edge variants act only when the trigger changes from low to high.
- Falling-edge variants act only when the trigger changes from high to low.

Keep reset and sample pulses wide enough for the selected `.tran` timestep.
ngspice cannot detect a pulse that the transient solver completely skips.

## Common Parameters

| Parameter | Meaning |
| --- | --- |
| `ic` | Initial condition. For resettable integrators, this is also the reset output value. |
| `gain` | Multiplier applied to the input before integration or differentiation. |
| `vth` | Trigger threshold voltage for reset or sample input. |
| `vhyst` | Trigger hysteresis voltage band. Default `0` disables hysteresis. |
| `lo` | Lower output clamp limit. |
| `hi` | Upper output clamp limit. |
| `limit_range` | Smoothing/range parameter passed to the underlying XSPICE limiting behavior. |

## Resettable Integrator

Devices:

- `NG_INT_PULSE in rst out`
- `NG_INT_RISE in rst out`
- `NG_INT_FALL in rst out`

Parameters:

```spice
params: ic=0 gain=1 vth=0.5 vhyst=0 lo=-1e12 hi=1e12 limit_range=1e-9
```

Behavior:

```text
out = ic + integral(gain * V(in) dt)
```

The reset pin returns `out` to `ic`.

- `NG_INT_PULSE`: reset while `rst` is high.
- `NG_INT_RISE`: reset on the rising edge of `rst`.
- `NG_INT_FALL`: reset on the falling edge of `rst`.

Example:

```spice
Resettable integrator example

.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib

Vin in 0 dc 1
Vrst rst 0 pwl(0 0 1m 0 1.001m 1 1.2m 1 1.201m 0 3m 0)

Xint in rst out NG_INT_RISE params: ic=0.25 gain=1 vth=0.5

Rin in 0 1G
Rrst rst 0 1G
Rout out 0 1G

.tran 10u 3m
.end
```

## Anti-Windup Resettable Integrator

Devices:

- `NG_INT_AW_PULSE in rst out`
- `NG_INT_AW_RISE in rst out`
- `NG_INT_AW_FALL in rst out`

Parameters:

```spice
params: ic=0 gain=1 vth=0.5 vhyst=0 lo=-1e12 hi=1e12 limit_range=1e-9
```

Behavior is the same as the resettable integrator, with anti-windup enabled:

- If `out` is at `hi` and the input would drive it higher, integration pauses.
- If `out` is at `lo` and the input would drive it lower, integration pauses.
- If the input reverses direction, integration resumes.
- Reset still sets `out` to `ic`.

Important reset example:

```spice
Xaw in rst awout NG_INT_AW_PULSE params: ic=0 gain=1 lo=-1 hi=0.1 vth=0.5
```

Here a `1 V` reset pulse on `rst` resets the output to `0 V`, because `ic=0`.
The `1 V` pulse is only the trigger level. The reset condition is
`V(rst) >= vth`.

Example:

```spice
Anti-windup integrator example

.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib

Vin in 0 pwl(0 1 3m 1 3.001m -1 8m -1)
Vrst rst 0 pwl(0 0 4m 0 4.001m 1 4.2m 1 4.201m 0 8m 0)

Xaw in rst awout NG_INT_AW_PULSE params: ic=0 gain=1 lo=-1 hi=0.1 vth=0.5

Rin in 0 1G
Rrst rst 0 1G
Rout awout 0 1G

.tran 10u 8m
.end
```

## Modulo Integrator

Device:

- `NG_INT_MOD in out`

Parameters:

```spice
params: ic=0 gain=1 modulus=1 lo=-1e12 hi=1e12 limit_range=1e-9
```

Parameter meanings:

| Parameter | Meaning |
| --- | --- |
| `modulus` | Wrap size. The output resets to `ic` when the integrated value reaches `ic + modulus`. |

Behavior:

```text
out = ic + integral(gain * V(in) dt)
```

When `out` reaches `ic + modulus`, the output wraps back to `ic`.

Example:

```spice
Modulo integrator example

.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib

Vin in 0 dc 1
Xphase in phase NG_INT_MOD params: ic=0 gain=1 modulus=0.25

Rin in 0 1G
Rphase phase 0 1G

.tran 0.25m 1
.end
```

## Sample and Hold

Devices:

- `NG_SAMPLE_RISE in trig out`
- `NG_SAMPLE_FALL in trig out`

Parameters:

```spice
params: ic=0 vth=0.5 vhyst=0
```

Behavior:

- `NG_SAMPLE_RISE`: copies `V(in)` to `out` on the rising edge of `trig`.
- `NG_SAMPLE_FALL`: copies `V(in)` to `out` on the falling edge of `trig`.
- Between trigger edges, `out` holds the last sampled value.
- Before the first trigger edge, `out = ic`.

Example:

```spice
Sample and hold example

.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib

Vsig sig 0 pwl(0 0 1m 1 2m 2 3m 3)
Vclk clk 0 pwl(0 0 0.5m 0 0.501m 1 0.7m 1 0.701m 0 1.5m 0 1.501m 1)

Xsamp sig clk held NG_SAMPLE_RISE params: ic=-1 vth=0.5

Rsig sig 0 1G
Rclk clk 0 1G
Rheld held 0 1G

.tran 5u 3m
.end
```

## Derivative

Device:

- `NG_DDT in out`

Parameters:

```spice
params: gain=1 out_offset=0 lo=-1e12 hi=1e12 limit_range=1e-9
```

Parameter meanings:

| Parameter | Meaning |
| --- | --- |
| `out_offset` | Constant added to the differentiator output. |

Behavior:

```text
out = out_offset + gain * d(V(in))/dt
```

For a ramp input, output is the ramp slope. For a pulse input with finite
transition time, output is a positive value during the rising transition, near
zero while flat, and a negative value during the falling transition.

Example:

```spice
Derivative example

.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib

Vramp ramp_in 0 pwl(0 0 1m 1)
Xddt1 ramp_in ramp_ddt NG_DDT params: gain=1

Vpulse pulse_in 0 pwl(0 0 0.2m 0 0.21m 1 0.7m 1 0.71m 0 1m 0)
Xddt2 pulse_in pulse_ddt NG_DDT params: gain=1

Rramp ramp_in 0 1G
Rrampddt ramp_ddt 0 1G
Rpulse pulse_in 0 1G
Rpulseddt pulse_ddt 0 1G

.tran 1u 1m
.end
```

## Full Minimal Netlist Pattern

Use this skeleton when adding any device to a new ngspice deck:

```spice
My ngfuncs simulation

.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib

* sources
Vin in 0 dc 1
Vrst rst 0 pulse(0 1 1m 1u 1u 100u 2m)

* ngfuncs block
X1 in rst out NG_INT_RISE params: ic=0 gain=1 vth=0.5

* high-value resistors give XSPICE pins a DC path
Rin in 0 1G
Rrst rst 0 1G
Rout out 0 1G

.tran 10u 5m
.end
```
