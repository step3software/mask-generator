# Project status

This is the single current progress/input ledger. Contracts and procedures live in their [own documents](README.md); dated observations live in [evidence](#evidence).

## Baseline

Reviewed repository: `step3software/mask-generator`, `main` at [d5db405402e3ae9a8b6265e65185f847fe6dbc88](https://github.com/step3software/mask-generator/commit/d5db405402e3ae9a8b6265e65185f847fe6dbc88), checked 2026-10-25. Application capabilities below are implemented and published in that baseline. This documentation reorganization is proposed on its own PR until merged; publishing documentation does not mark a target match accepted.

| Area | State | Evidence or continuation |
| --- | --- | --- |
| Three-piece geometry and consistent orthographic/perspective views | Implemented and published | [Implementation/test map](implementation.md) |
| Multiview silhouette/contour comparison and bounded previews | Implemented and published | [Contracts](contracts.md#measurements-and-ranking) |
| Geometry-only seeded random search | Implemented baseline sampler; no global-optimum claim | [Search contract](contracts.md#search-bounds) |
| Generic screening | Optional separate implementation | [Tool guide](../tools/generic_screening/README.md) |
| Real target fitting | Not performed; local candidate images are available but applicability and preparation are unverified | Inputs below |
| Physical build validation | Not implemented | No collision, join, material/stability, or fabrication proof |
| User target acceptance | Not determined | No target tolerances or acceptance evidence supplied |

## Outstanding inputs

Ten untracked image files were discovered locally in `references/ducky/` during checkout synchronization on 2026-10-25. Their visual contents, source provenance, intended target, and view relationships have not been reviewed; they were not uploaded with the documentation. M1-2 should inventory these candidate assets and establish applicability before treating them as target evidence. A fresh clone does not contain them and needs an actual source location from the owner.

Identify which supplied images depict the same target and use all useful supplied angles. There is no fixed four-angle requirement or eight-angle evaluation cap. The four cameras in the demo are arbitrary; eight is only a per-overlay preview cap.

Target comparison additionally needs foreground masks and a shared camera interpretation, or preparation work from supplied images. Known viewpoints, lens/crop metadata, landmarks, and a dimension help where available. Automatic masking of opaque photographs and camera calibration are not implemented. Do not ask the owner to invent numerical cameras; estimates can be prepared later from evidence and labeled uncertain.

Physical dimensions, thickness, permitted bends/cuts/joins/contact, intersection constraints, acceptance tolerances, and any priority views remain unspecified. Absolute scale is unnecessary for relative silhouette experimentation but necessary for physical scale/fabrication claims. No default dimensions or acceptance rules should be inferred from synthetic fixtures.

The next target-specific work is defined by milestone M1 below. Missing target evidence does not block unrelated documentation, synthetic tests, or already authorized software work.

## M1 — Reproducible baseline fit

Outcome: another developer can reproduce a baseline comparison of one three-piece geometry against the supplied target views, inspect its weakest views, and see the remaining uncertainty. This is a development milestone, not a claim that the resulting shape is acceptable or physically buildable. The following tasks are planned; none are marked completed by this documentation update.

| Task | Dependencies and current state | Deliverable | Completion check |
| --- | --- | --- | --- |
| M1-1 Independent validation baseline | Can be developed without target images; not implemented | Independent projection/metric fixtures and an evidence record following the [benchmark protocol](operations.md#benchmark-protocol) | Expected results come from analytic calculations or separately produced evidence; negative cases fail as expected; numerical tolerances have a recorded basis |
| M1-2 Reference intake | Local candidate images available; applicability unverified | Versioned source inventory and view grouping in the [reference preparation bundle](contracts.md#reference-preparation-bundle) | Every supplied image is included, grouped as an alternative target, or excluded with a reason; no view is silently discarded |
| M1-3 Masks and camera interpretation | M1-2; not started | Reviewed masks, explicit camera revisions, uncertainty notes, and fit/check view assignments | [Preparation procedure](operations.md#reference-preparation-procedure) completed; scoreable views satisfy the runtime reference format; unresolved views are identified explicitly |
| M1-4 Geometry suitability decision | M1-3 plus reliable projection evidence from M1-1; not started | A three-piece base scene, justified bounds, and a geometry-fit decision in the experiment record | Apply [geometry decision criteria](contracts.md#geometry-suitability-decision); choose proceed, investigate calibration/masks, insufficient evidence, or propose a family extension with specific evidence |
| M1-5 Baseline fitting experiment | M1-4 permits fitting; not started | Frozen inputs/settings, baseline and searched candidate results, selected scene, and measured runtime | Existing commands produce reports without unaccounted candidate errors; selection uses fit views only; every scoreable view appears in final reporting |
| M1-6 Independent-view and uncertainty assessment | M1-5; not started | Held-out results where possible, sensitivity results, and a reproducible evidence package | Follow [benchmark protocol](operations.md#benchmark-protocol); repeat the recorded run; report regressions and untested properties; attach acceptance questions without inventing thresholds |

Task status, dependencies, and evidence links belong in this table. Procedures live in operations and artifact/decision definitions in contracts; avoid adding a second milestone ledger.

M1 is complete when its evidence package contains the source inventory, preparation notes, frozen manifests, geometry decision, base/bounds/selected scene, exact commands/ref/dependency versions, reports, and the validation results above. An unavailable holdout must be explained and the result labeled in-sample only. Unknown scale or physical constraints remain explicit limitations. If camera evidence cannot support meaningful comparison or the geometry family is inadequate, record that disposition and the precise next work; do not mark M1 complete merely because the investigation ended.

Target acceptance remains a separate unresolved decision. Any proposed acceptance criteria must distinguish visual agreement on supplied views, behavior on withheld views, and physical construction claims. The owner can resolve target-specific tolerances after reviewing baseline errors and preparation uncertainty.

## Evidence

- Initial publication recorded 12 geometry tests plus 9 generic-screening tests passing against the application content in the baseline above. These are prior local execution results from the project session, not a hosted CI run, installation certification, or target acceptance. Suites have not been rerun for this documentation-only change.
- [Documentation review, 2026-10-25](evidence/documentation-review-2026-10-25.md): baseline, coverage, consolidation, and checks. Read only when auditing the reorganization.
- [Development-readiness update, 2026-10-25](evidence/development-readiness-2026-10-25.md): milestone, preparation workflow, geometry decision, and validation-plan changes. These are documented plans, not implemented capabilities.

When implementation or available target inputs change, update this ledger and link exact-ref evidence. Keep command details, scope rules, and chronological investigation notes out of this ledger.
