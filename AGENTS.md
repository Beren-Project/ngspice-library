# Documentation and model governance

This is an ngspice library and model-making project.

## Sources of truth

Use this precedence when technical sources disagree:

1. Public `.subckt` wrappers in `lib/ngfuncs.lib` define the public interface.
2. `ifspec.ifs` defines custom XSPICE ports, defaults, and declared ranges.
3. `cfunc.mod` defines custom model behavior.
4. Tests and examples establish validation status.
5. Documentation is descriptive and must be corrected when it disagrees.

Edit canonical custom-model sources only under `src/xspice/icm/ngfuncs/`.
The copy under `src/ngspice/src/xspice/icm/ngfuncs/` is generated.

## Documentation requirements

- Any new public device or model must update `docs/device-catalog.md`.
- Put device documentation under `docs/devices/`; do not create unrelated
  one-off Markdown files.
- Every device must document exact pin order, parameters, units, defaults,
  enforced ranges, caller requirements, usage, validation status, and
  limitations.
- Every non-trivial model must include a Mermaid structure diagram.
- Add a Mermaid signal-flow diagram when behavioral, control, state, feedback,
  clamp, or protection paths are not obvious.
- Update README only for entry-point information.
- Update all internal links whenever documentation moves.
- Mark uncertain claims as `NEEDS_VERIFICATION`.
- Do not invent behavior not present in wrappers, interfaces, implementation,
  equations, tests, examples, or source comments.
- Add ADRs for durable modeling architecture, library organization, and
  validation methodology decisions.

## Change validation

For documentation and example changes:

```sh
make check-stock
NGFUNCS_CM=build/ngfuncs.cm scripts/run_ngspice_tests.sh
make test-report
```

Batch-run changed examples and render every Mermaid block. Confirm that no
model or library source changed unless the task explicitly authorizes it.
