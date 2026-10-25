# Development-readiness update — 2026-10-25

## Scope and baseline

The user requested updating the documentation after a review found it sufficient for operating the prototype but incomplete for directing the next development stage. This update starts from documentation commit [f75a27595b86d8f0e12b30473f5abf09063eae7d](https://github.com/step3software/mask-generator/commit/f75a27595b86d8f0e12b30473f5abf09063eae7d) on the existing documentation PR. The application baseline remains [d5db405402e3ae9a8b6265e65185f847fe6dbc88](https://github.com/step3software/mask-generator/commit/d5db405402e3ae9a8b6265e65185f847fe6dbc88).

Work now uses a normal Git checkout under the user's designated projects directory. Initial branch/HEAD and a clean working tree were verified. Earlier exported snapshots are not the development workspace. The original [consolidation record](documentation-review-2026-10-25.md) remains historical evidence for its original scope and checks.

## Changes

- Added M1 to the existing status ledger: ordered tasks, dependencies, named deliverables, and completion checks for a reproducible baseline fit.
- Added a reference-preparation procedure and provenance-sidecar contract. Masks, camera hypotheses, uncertainty, exclusions, and fit/check assignments have explicit handling without implying new automation exists.
- Added evidence-based geometry-family decision criteria, including the distinction between failed search, calibration/mask uncertainty, and unsupported geometry.
- Added an independent validation and fitting protocol, including analytic/external projection expectations, frozen check views, sensitivity assessment, reproducibility, and measured performance evidence.
- Updated agent/index/implementation routing to distinguish planned work from existing capabilities. No target thresholds or physical acceptance claims are fabricated.

These changes define future work; they do not implement calibration, masking, split management, sensitivity automation, independent fixtures, or actual target fitting. The absence of real references remains recorded in status. No application code changes or application-test reruns are part of this documentation-only update.

## Verification

Review-time checks covered 10 Markdown files, 105 relative links, all 11 existing README anchors, the six M1 task identifiers, six CLI help commands, Git diff whitespace, and Markdown-only change scope. Checks passed. The final PR diff is checked against its actual base. This is documentation validation, not evidence that the planned milestone has been executed. Application suites were not rerun for this documentation-only change.
