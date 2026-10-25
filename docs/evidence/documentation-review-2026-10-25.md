# Documentation review — 2026-10-25

## Baseline and scope

Target: `step3software/mask-generator`, `main` at [d5db405402e3ae9a8b6265e65185f847fe6dbc88](https://github.com/step3software/mask-generator/commit/d5db405402e3ae9a8b6265e65185f847fe6dbc88), tree `3172fa9db3c2f23cb96052cfffd821defac5e55e`. GitHub API inspection found 16 tracked files and no open PRs on 2026-10-25. No outstanding-PR documentation was incorporated.

Guidance: [Documentation review and consolidation](https://github.com/Wisteria-Psychological-Services/project-management-orchestration/blob/main/docs/agent-workflows/documentation-consolidation.md), read for this user-requested review. That workflow supplies review guidance, not imported portfolio lifecycle rules or new implementation authorization.

The local review source was an exported repository snapshot, not a Git checkout. All 16 tracked text files matched remote Git blob hashes after Windows line-ending normalization before edits; therefore no local tracked-content changes were overwritten. Existing generated caches/runs were excluded. Branch, HEAD, and open-PR state were verified remotely; no claim of a local `git status` result is made.

No AGENTS.md, documentation index, status ledger, requirement IDs, decision register, documentation checks, or CI workflow existed at this baseline. The root README and generic-screening README were the only Markdown documentation.

## Findings and disposition

- The 11 KB root README mixed scope, schemas, operational commands, implementation claims, current missing inputs, and validation. It now routes to single owners: contracts, operations, implementation map, and status.
- Added a concise agent entry point and task-based documentation index. Neither is a second specification or status ledger.
- Retained the root README's existing H2 headings so existing section anchors continue to resolve. No pre-existing identifiers or historical evidence were removed. No archive copy was committed because it would create a competing specification; the baseline commit preserves provenance.
- Distinguished implemented/published capabilities from prior test observations, proposed documentation, unavailable target evidence, physical validation, and user acceptance.
- Clarified that all supplied views are scored; four is the default candidate preview count and eight is the per-overlay view cap, not a reference-angle limit.
- Documented the existing render `geometry_sha256` naming mismatch: it hashes the entire scene. Runtime behavior and field names are unchanged.
- Preserved the optional generic tool's narrow scope and linked it to the active pipeline without treating its heuristics as shape acceptance.

## Coverage

| Coverage | Files |
| --- | --- |
| Read substantively | Root README; generic-screening README; cardboard.py; compare.py; search.py; extract_alpha_mask.py; demo.py; tests/test_geometry.py |
| Inspected selectively | tools/generic_screening/evaluate.py and its test definitions; requirements.txt; references.template.json; synthetic scene/bounds examples; .gitignore |
| Inventoried | All 16 tracked baseline files; no other tracked files existed |
| Excluded | Generated caches/runs; absent real references; unavailable physical-build/acceptance evidence |

This was a documentation review with targeted implementation verification, not an exhaustive code/security audit or performance study.

## Validation and limitations

An ad hoc local documentation check validates relative file links and heading anchors, preserves old root README anchors, verifies source/test navigation, compares changed-file scope against baseline, and checks documented CLI options against existing `--help` output. It is a review-time check under the workspace scratch directory, not a repository-provided checker or added application test.

The final diff is reviewed for unintended changes in scope, authorization, or acceptance. Only Markdown files are proposed. Existing application tests are not rerun for documentation-only changes; prior test counts stay attached to the baseline rather than presented as new results. No claim of external-link crawler coverage, exhaustive malformed-input handling, arbitrary-camera correctness, target reconstruction, installation verification, or acceptance is made.

Observed check results: nine Markdown files, 86 relative links, all 11 previous README heading anchors preserved, six existing CLI help commands checked, all 12 geometry-test names mapped, and no runtime-file changes. The two modified existing files are the root README and generic-screening README; seven Markdown files are new. Checks reported no errors. The root README changed from 1,491 words to 217; specifications were relocated rather than discarded.

Delivery uses one documentation branch and one reviewable PR. Main is not updated by this review and other PRs are not merged or closed. [Status](../status.md) remains the current ledger after this dated record.
