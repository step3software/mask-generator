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
| Real target fitting | Not performed; target reference images have not been supplied to this project | Inputs below |
| Physical build validation | Not implemented | No collision, join, material/stability, or fabrication proof |
| User target acceptance | Not determined | No target tolerances or acceptance evidence supplied |

## Outstanding inputs

The project needs actual reference images and identification of which depict the same assembly. Use all useful supplied angles; there is no fixed four-angle requirement or eight-angle evaluation cap. The four cameras in the demo are arbitrary; eight is only a per-overlay preview cap.

Target comparison additionally needs foreground masks and a shared camera interpretation, or preparation work from supplied images. Known viewpoints, lens/crop metadata, landmarks, and a dimension help where available. Automatic masking of opaque photographs and camera calibration are not implemented. Do not ask the owner to invent numerical cameras; estimates can be prepared later from evidence and labeled uncertain.

Physical dimensions, thickness, permitted bends/cuts/joins/contact, intersection constraints, acceptance tolerances, and any priority views remain unspecified. Absolute scale is unnecessary for relative silhouette experimentation but necessary for physical scale/fabrication claims. No default dimensions or acceptance rules should be inferred from synthetic fixtures.

The next target-specific step is to inventory supplied references, establish correspondence and masks/cameras, and determine whether the cylindrical-strip family is expressive enough. Missing target evidence does not block unrelated documentation, synthetic tests, or already authorized software work.

## Evidence

- Initial publication recorded 12 geometry tests plus 9 generic-screening tests passing against the application content in the baseline above. These are prior local execution results from the project session, not a hosted CI run, installation certification, or target acceptance. Suites have not been rerun for this documentation-only change.
- [Documentation review, 2026-10-25](evidence/documentation-review-2026-10-25.md): baseline, coverage, consolidation, and checks. Read only when auditing the reorganization.

When implementation or available target inputs change, update this ledger and link exact-ref evidence. Keep command details, scope rules, and chronological investigation notes out of this ledger.
