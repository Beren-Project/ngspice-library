# Codex handoff

## Current baseline

Current documentation baseline commit:

```text
5f87eb1 docs: reorganize ngspice device docs and validation guides
```

The documentation reorganization is complete. Do not redo it.

## Completed work

* Reorganized documentation into a concise README, task-oriented docs index, device catalog, usage guide, architecture guide, development guide, validation guide, troubleshooting guide, model-authoring guide, device-family pages, ADRs, and `AGENTS.md`.
* Documented all 12 public `.subckt` wrappers and 3 internal XSPICE models.
* Added or updated 12 Mermaid diagrams.
* Added signal-flow diagrams where useful for model behavior.
* Updated examples to cover every public wrapper.
* Added documentation governance and source-precedence rules in `AGENTS.md`.
* Recorded remaining validation gaps in `docs/validation-guide.md`.

## Validation already passed

The documentation pass already passed:

```sh
make check-stock
NGFUNCS_CM=build/ngfuncs.cm scripts/run_ngspice_tests.sh
make test-report
git diff --check
```

Also passed:

* all five examples
* all 12 Mermaid renders
* Markdown links and anchors
* report completeness: 12 decks, 12 logs, 12/12 passed

## Remaining validation gaps

The known remaining validation gaps are documented in `docs/validation-guide.md`.

Current important gaps:

* Direct regression tests for `NG_INT_AW_RISE` and `NG_INT_AW_FALL`
* Trigger hysteresis and initial-high trigger behavior
* Negative/nonzero-origin modulo behavior and clamp interaction
* Optional `NG_DDT` parameters and AC behavior
* Invalid comparator parameter combinations
* Reset `ic` outside limits
* Numerical effects of custom hard-clamp partial derivatives

## Source precedence

Use this precedence for all future technical work:

1. `.subckt` wrappers in `lib/ngfuncs.lib` define the public interface.
2. `ifspec.ifs` defines XSPICE interface, defaults, and ranges.
3. `cfunc.mod` defines custom-model behavior.
4. Tests and examples establish validation status.
5. Documentation is lowest priority.

## Do not modify without explicit approval

Do not modify these paths unless explicitly approved:

* `lib/**`
* `src/**`
* `build/**`
* `scripts/**`
* `Makefile`

For test-coverage work, prefer adding or updating files under:

* `tests/**`
* `docs/validation-guide.md`
* relevant `docs/devices/*.md` status/validation notes only if validation status changes

## Recommended next task

Add focused regression tests for:

* `NG_INT_AW_RISE`
* `NG_INT_AW_FALL`

Suggested workflow for the next Codex session:

1. Read `AGENTS.md`.
2. Read `docs/HANDOFF.md`.
3. Read `docs/validation-guide.md`.
4. Inspect existing regression deck style under `tests/`.
5. Inspect examples for anti-windup reset variants.
6. Propose a small test plan before editing.
7. Add focused regression decks for `NG_INT_AW_RISE` and `NG_INT_AW_FALL`.
8. Run the regression tests.
9. If the tests pass, update validation status/docs from `needs verification` to `stable` only where justified.
10. Remove `docs/HANDOFF.md` before the final commit unless explicitly told to keep it.

## First prompt for the next session

```text
Read `AGENTS.md`, `docs/HANDOFF.md`, and `docs/validation-guide.md` first.

Do not redo the documentation reorganization.

Current baseline commit:
5f87eb1 docs: reorganize ngspice device docs and validation guides

Task:
Add focused regression tests for `NG_INT_AW_RISE` and `NG_INT_AW_FALL`.

Before editing:
- inspect existing regression deck style under `tests/`
- inspect anti-windup examples
- inspect the relevant wrapper definitions and XSPICE model behavior
- propose a small test plan

Do not modify `lib/**`, `src/**`, `build/**`, `scripts/**`, or `Makefile` unless explicitly approved.

After tests are added:
- run the relevant tests
- run the full regression command if practical
- update docs only if validation status changes
- remove `docs/HANDOFF.md` before committing unless I tell you to keep it
```
