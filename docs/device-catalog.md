# Device catalog

This catalog covers the 12 public wrappers declared in
[`lib/ngfuncs.lib`](../lib/ngfuncs.lib). The custom code-model library itself
registers three internal models: `ng_int_rst`, `ng_int_mod`, and `ng_sample`.

Status meanings:

- `stable`: directly validated for the documented nominal behavior
- `needs verification`: exposed publicly but missing direct validation for a
  defining behavior

## Inventory

| Device | Status | Category and backing model | Exact pins | Parameters and defaults | Example | Validation | Documentation and diagram |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `NG_INT_PULSE` | stable | Level-reset integrator; `ng_int_rst(mode=0, aw_enable=false)` | `in rst out` | `ic=0 gain=1 vth=0.5 vhyst=0 lo=-1e12 hi=1e12 limit_range=1e-9` | [`resettable_integrator.cir`](../examples/resettable_integrator.cir) | [`test_integrator_reset_pulse.cir`](../tests/test_integrator_reset_pulse.cir) | [Resettable integrators](devices/resettable-integrators.md#structure-and-signal-flow) |
| `NG_INT_RISE` | stable | Rising-edge reset integrator; `ng_int_rst(mode=1, aw_enable=false)` | `in rst out` | same as above | [`resettable_integrator.cir`](../examples/resettable_integrator.cir) | [`test_integrator_reset_rise.cir`](../tests/test_integrator_reset_rise.cir) | [Resettable integrators](devices/resettable-integrators.md#structure-and-signal-flow) |
| `NG_INT_FALL` | stable | Falling-edge reset integrator; `ng_int_rst(mode=2, aw_enable=false)` | `in rst out` | same as above | [`resettable_integrator.cir`](../examples/resettable_integrator.cir) | [`test_integrator_reset_fall.cir`](../tests/test_integrator_reset_fall.cir) | [Resettable integrators](devices/resettable-integrators.md#structure-and-signal-flow) |
| `NG_INT_AW_PULSE` | stable | Gated/clamped level-reset integrator; `ng_int_rst(mode=0, aw_enable=true)` | `in rst out` | same as above | [`anti_windup.cir`](../examples/anti_windup.cir) | [`test_integrator_antiwindup_pulse.cir`](../tests/test_integrator_antiwindup_pulse.cir) | [Resettable integrators](devices/resettable-integrators.md#structure-and-signal-flow) |
| `NG_INT_AW_RISE` | needs verification | Gated/clamped rising-edge reset integrator; `ng_int_rst(mode=1, aw_enable=true)` | `in rst out` | same as above | [`anti_windup.cir`](../examples/anti_windup.cir) | TODO: direct validation needed | [Resettable integrators](devices/resettable-integrators.md#structure-and-signal-flow) |
| `NG_INT_AW_FALL` | needs verification | Gated/clamped falling-edge reset integrator; `ng_int_rst(mode=2, aw_enable=true)` | `in rst out` | same as above | [`anti_windup.cir`](../examples/anti_windup.cir) | TODO: direct validation needed | [Resettable integrators](devices/resettable-integrators.md#structure-and-signal-flow) |
| `NG_INT_MOD` | stable | Modulo integrator; `ng_int_mod` | `in out` | `ic=0 gain=1 modulus=1 lo=-1e12 hi=1e12 limit_range=1e-9` | [`modulo_and_sample.cir`](../examples/modulo_and_sample.cir) | [`test_integrator_modulo.cir`](../tests/test_integrator_modulo.cir) | [Modulo integrator](devices/modulo-integrator.md#structure-and-signal-flow) |
| `NG_SAMPLE_RISE` | stable | Rising-edge sample-and-hold; `ng_sample(edge=1)` | `in trig out` | `ic=0 vth=0.5 vhyst=0` | [`modulo_and_sample.cir`](../examples/modulo_and_sample.cir) | [`test_sample_rise.cir`](../tests/test_sample_rise.cir) | [Sample-and-hold](devices/sample-and-hold.md#structure-and-signal-flow) |
| `NG_SAMPLE_FALL` | stable | Falling-edge sample-and-hold; `ng_sample(edge=2)` | `in trig out` | `ic=0 vth=0.5 vhyst=0` | [`modulo_and_sample.cir`](../examples/modulo_and_sample.cir) | [`test_sample_fall.cir`](../tests/test_sample_fall.cir) | [Sample-and-hold](devices/sample-and-hold.md#structure-and-signal-flow) |
| `NG_DDT` | stable | Derivative wrapper; stock XSPICE `d_dt` | `in out` | `gain=1 out_offset=0 lo=-1e12 hi=1e12 limit_range=1e-9` | [`modulo_and_sample.cir`](../examples/modulo_and_sample.cir) | [`test_derivative.cir`](../tests/test_derivative.cir) | [Derivative](devices/derivative.md#structure) |
| `NG_COMP_SMOOTH_DIFF` | stable | Smooth differential comparator; behavioral source plus stock `slew` | `inp inn out` | `vlow=0 vhigh=1 voffset=0 vsmooth=1m trise=1n tfall=1n` | [`smooth_pwm.cir`](../examples/smooth_pwm.cir) | transfer, dynamic, PWM, equivalence, and smoke tests | [Differential diagram](devices/smooth-comparators.md#differential-structure-and-signal-flow) |
| `NG_COMP_SMOOTH_SE` | stable | Smooth single-ended comparator; threshold source plus differential wrapper | `in out` | `vth=0 vlow=0 vhigh=1 vsmooth=1m trise=1n tfall=1n` | [`smooth_threshold.cir`](../examples/smooth_threshold.cir) | [`test_comparator_single_ended.cir`](../tests/test_comparator_single_ended.cir) | [Single-ended diagram](devices/smooth-comparators.md#single-ended-structure-and-signal-flow) |

## Internal model inventory

| Internal model | Source | Exact ports | Defaults and declared ranges | Public owners |
| --- | --- | --- | --- | --- |
| `ng_int_rst` | [`src/xspice/icm/ngfuncs/ng_int_rst/`](../src/xspice/icm/ngfuncs/ng_int_rst/) | `in rst out` | `mode=1 [0,2]`; `ic=0`; `gain=1`; `vth=0.5`; `vhyst=0 [0,+inf)`; `lo=-1e12`; `hi=1e12`; `limit_range=1e-9 [0,+inf)`; `aw_enable=false` | Six resettable-integrator wrappers |
| `ng_int_mod` | [`src/xspice/icm/ngfuncs/ng_int_mod/`](../src/xspice/icm/ngfuncs/ng_int_mod/) | `in out` | `ic=0`; `gain=1`; `modulus=1 [1e-30,+inf)`; `lo=-1e12`; `hi=1e12`; `limit_range=1e-9 [0,+inf)` | `NG_INT_MOD` |
| `ng_sample` | [`src/xspice/icm/ngfuncs/ng_sample/`](../src/xspice/icm/ngfuncs/ng_sample/) | `in trig out` | `edge=1 [1,2]`; `ic=0`; `vth=0.5`; `vhyst=0 [0,+inf)` | Two sample-and-hold wrappers |

The wrapper library fixes internal selector parameters such as `mode`, `edge`,
and `aw_enable`. Declared custom-model ranges may warn and clamp invalid values
rather than rejecting the model.

## Audit disposition

| Family | Previous duplication or conflict | Completed action | Remaining gap |
| --- | --- | --- | --- |
| Resettable integrators | Repeated across README and three docs; smoothing and AW behavior overstated | Consolidated into one source-based family page and exact signal-flow diagram | AW edge variants and several parameter combinations need direct tests |
| Modulo integrator | Described only as upward reset to `ic` | Replaced with bidirectional remainder-preserving behavior and diagram | Negative direction, nonzero origin, and clamp interaction need tests |
| Sample-and-hold | Trigger equality and time-zero behavior were incomplete | Added exact state/edge semantics and diagram | Hysteresis and initial-high cases need tests |
| Derivative | Ideal derivative equation omitted time-zero, AC, and stock limiting behavior | Added stock-source-qualified behavior and structure diagram | Optional parameters and timestep refinement need tests |
| Smooth comparators | Detailed guide duplicated shorter device reference; diagrams were conceptual | Merged into one family page and updated exact internal names | Invalid parameter behavior remains unverified |

## Known catalog-wide gaps

- Nonzero trigger hysteresis is not directly tested.
- Initial-high trigger behavior is not directly tested.
- Comparator invalid parameter combinations are not validated or rejected by
  the wrappers.
- The custom integrator `limit_range` parameters are accepted but unused.
- The numerical effect of returning an integration partial after a hard clamp
  is `NEEDS_VERIFICATION`.
