# Troubleshooting

## Missing `build/ngfuncs.cm`

Build the custom library:

```sh
make build-cm
```

Stock-only `NG_DDT` and comparator circuits do not need this artifact.

## Unknown custom code model

Ensure the netlist executes:

```spice
.control
pre_codemodel build/ngfuncs.cm
.endc
```

before parsing custom model instances, and include `lib/ngfuncs.lib`.

## Timestep too small near a trigger edge

Use finite source rise/fall times consistent with the `.tran` timestep. Very
fast edges can cause convergence failure or be skipped entirely.

## Reset output is unexpected

Reset assigns `ic`, not the reset-pin voltage. The current implementation
assigns `ic` directly and does not clamp it to `lo` or `hi`.

## Edge does not fire at time zero

Reset and sample models initialize trigger state at time zero without creating
an edge. A trigger that begins high therefore does not produce an initial
rising-edge action.

## Exact threshold is unstable with zero hysteresis

The current Schmitt helper uses `>=` to enter high and `>` to remain high.
Behavior at exactly `vth` with `vhyst=0` is `NEEDS_VERIFICATION`. Avoid holding
the trigger exactly at threshold.

## Test passes but waveform is absent

Inspect the generated report deck and log under `tests/output/report/`.
Ensure the source deck contains detectable node voltages and a `run` command.

## Report claims all tests passed but count is low

The report generator can omit a deck that raises an exception. Compare source
deck and generated log counts as described in the
[validation guide](validation-guide.md).
