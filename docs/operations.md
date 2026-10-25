# Operations

Run commands from the repository root with Python 3.10+. [requirements.txt](../requirements.txt) owns dependency ranges (NumPy and Pillow). [Contracts](contracts.md) owns input formats and semantics; [status](status.md) records unresolved target inputs.

## Install and run the demo

```powershell
python -m pip install -r requirements.txt
python demo.py --output runs/demo-001
```

Use a new output path on every run. Existing output directories are refused, not overwritten. A failing run may leave partial artifacts; do not interpret them as a completed evaluation.

The demo produces three candidates, four arbitrary cameras, synthetic masks, and comparison reports under `runs/demo-001`. The unchanged candidate scores IoU 1 because it generated the references. This checks software consistency, not a real target match. Generated runs are ignored by Git.

## Prepare references and compare

Identify reference images of the same assembly, prepare foreground masks, and establish cameras in a shared coordinate system. Camera estimation and ordinary-photograph segmentation are not implemented. Use the [reference contract](contracts.md#reference-format), [template](../references.template.json), and generated `runs/demo-001/references.synthetic.json` as a structural example only.

For images with meaningful alpha:

```powershell
python extract_alpha_mask.py transparent-reference.png --output reference-mask.png
```

The alpha output file must not already exist; create its parent folder first. This helper does not derive masks from an opaque photograph.

Compare a directory of candidate scene JSON files:

```powershell
python compare.py your-candidates --candidate-dir --references your-references.json --output runs/comparison-001 --review-limit 4
```

Alternatively supply explicit scene JSON paths and omit `--candidate-dir`. Directory expansion selects top-level `*.json` only. Candidate files must use the exact reference camera rig. `--boundary-tolerance-px` changes the diagnostic tolerance, not target acceptance.

## Reference preparation procedure

This procedure defines planned M1-2/M1-3 work. It combines manual preparation with the existing loaders; no automatic segmentation or camera-calibration feature is implied. Its deliverable is the [reference preparation bundle](contracts.md#reference-preparation-bundle).

1. Inventory every supplied image. Preserve original bytes, hash them, assign stable IDs, and group images of the same assembly. Identify duplicate viewpoints, alternatives, obstructions, and missing metadata. Record an inclusion or exclusion reason for each image; do not discard a difficult angle because its score is poor.
2. Establish coordinates and image transformations. Pick and record a world axis/origin convention and known or arbitrary relative units. Preserve raw images; record EXIF orientation, crop, resize, and any lens correction used in prepared copies. Prepared image/mask dimensions must satisfy the current camera limits. Changes to crop/resize require corresponding camera interpretation changes; the comparator will not compensate automatically.
3. Prepare foreground masks. Use meaningful alpha where present or a documented manual masking method for photographs. Inspect the mask over its source image, separating cardboard from cast shadows and background. Mark genuinely ambiguous pixels with an ignore mask and explain them. Add piece masks only where correspondence is defensible. Confirm sizes, nonempty comparable foreground, mask values, and non-overlapping visible labels against the reference contract.
4. Establish an initial camera interpretation. Prefer supplied calibration or measured landmarks. Where unavailable, record the evidence for perspective versus orthographic projection and a manual estimate using identifiable edges/landmarks and a common coordinate frame. Distinguish inferred values from known ones. If the geometry/camera relationship remains ambiguous, retain explicitly labeled hypotheses; do not present a unique calibrated solution. An initial camera hypothesis enables an exploratory run, not a claim of accurate calibration.
5. Review camera plausibility before ranking geometry. Check known landmarks or independently defined projection fixtures where possible. Record disagreement, unknown scale, and uncertainty. Do not improve apparent fit by giving different candidates independently tuned camera rigs. Compare separate frozen camera hypotheses as separately labeled experiments. If no interpretation supports a meaningful comparison, mark the view unresolved and identify what evidence is missing.
6. Assign fit and check views before fitting. Where sufficient distinct views exist, reserve at least one informative angle from parameter selection. Do not use near-duplicate images as independent validation. With too few usable views, mark validation as in-sample only and explain what remains unconstrained. No particular number of references is required by the software.
7. Freeze the bundle revision. Populate the runtime manifests and preparation sidecar. Validate with existing parsing/comparison paths and a provisional three-piece base scene, inspecting all reported errors. Treat the resulting scores as a baseline, not success criteria. Route persistent geometric discrepancies through the [geometry decision](contracts.md#geometry-suitability-decision).

Uncertainty notes can remain qualitative until evidence supports numeric ranges. Do not manufacture tight tolerances, camera accuracy, dimensions, or piece correspondence to complete the bundle.

## Search and render

```powershell
python search.py your-base-scene.json --bounds your-bounds.json --references your-references.json --output runs/search-001 --count 50 --seed 7
python cardboard.py your-scene.json --output runs/render-001
```

Provide actual [geometry bounds](contracts.md#search-bounds); synthetic example bounds do not constrain the target. Search writes sampled scenes in `candidates/`, search settings in `search.used.json`, and comparison output in `report/`. Rendering writes RGBA `<id>.png`, binary `<id>.mask.png`, and visible-piece labels `<id>.ids.png`, plus `scene.used.json` and `render_manifest.json`.

## Read the reports

| Artifact | Use |
| --- | --- |
| `summary.txt` | Compact counts, reference state, best worst/mean IoU, weakest view |
| `summary.json` | Settings, limitations, bounded error examples, model-call count |
| `ranking.csv` | Ordering of evaluated candidates; invalid candidates are omitted |
| `metrics.jsonl` | Full per-candidate/per-view/per-piece results and candidate errors |
| `references.used.json` | Reference manifest path, cameras, and mask/valid-region/part hashes |
| `review_queue.json` | Selected candidates, overlay files, selected/omitted views |
| `review-NN.png` | Bounded disagreement overlay; inspect originals for fine details |

Use [metric semantics](contracts.md#measurements-and-ranking) before interpreting rank or scores. Set `--review-limit 0` to suppress overlays; every view is still evaluated. Selected previews are optional review inputs, not acceptance evidence for unreviewed details.

Comparison and search return 0 after completion without candidate errors, 1 when reports contain candidate errors, and 2 for handled input/configuration/output errors. Rendering, demo, and alpha extraction return 0 on success and 2 for handled failures. A 0 exit code is not target acceptance; unexpected exceptions may still raise a traceback. Inspect the summary and completed artifacts, not the exit code alone.

## Benchmark protocol

This is the planned validation approach for M1-1/M1-5/M1-6. The existing tests remain useful for software behavior; the independent checks and experiment artifacts below are not yet implemented or performed. Task state belongs in [M1](status.md#m1--reproducible-baseline-fit).

### Independent software checks

- Establish expected projections independently of `render`: use hand-calculated projections of known points and simple faces, or externally produced fixtures with their generator/settings recorded. Cover both projection modes, orientation/scale, and front/back occlusion. Re-rendering the same scene to make its reference is not the independent check.
- Verify metrics on analytically defined masks: identical, disjoint, partially overlapping, known translated boundaries, ignored regions, and empty visible pieces. State expected overlap or distance values and the pixel/raster basis of any tolerances before implementation changes are tested.
- For any geometry-family extension, retain exactly three connected pieces and add independent projection checks for the newly supported feature. Existing mesh/occlusion tests alone do not establish real-shape reconstruction accuracy.

### Fit, freeze, and check

1. Record code commit, Python/NumPy/Pillow versions, platform, source/mask hashes, camera revisions, split, tessellation, metric settings, base scene, bounds, seed, candidate count, commands, and run directories. Record wall time and candidate/render counts to establish an actual performance baseline; no runtime or token target has been specified.
2. Evaluate the base scene and search on fit views only. Include the base in the candidate ranking. Record the selected candidate and per-view metrics, including unsuccessful candidates and weakest-view overlays. Geometry selection follows the existing worst-view/mean-IoU ranking; do not silently replace it with a new composite score.
3. Freeze the selected pieces before evaluating check views. Prepare a scene with the same geometry/tessellation and only the check manifest's cameras; the current comparator requires an exact camera-set match. Run comparison separately on check views and all scoreable views. If check results are used to revise geometry, relabel that experiment as no longer independent and record the new split or validation limitation.
4. Assess preparation sensitivity. Where defensible ranges exist, repeat evaluation under recorded camera or mask variations and report how metrics/rank change. Do not select whichever preparation makes a candidate look best. If uncertainty is unknown or alternatives are untested, state that explicitly and avoid claiming a robust match.
5. Repeat the recorded experiment to check reproducibility. Compare candidate order, scores, and selected geometry under the same environment/settings. Explain any discrepancies and retain inputs that allow investigation; identical image bytes across unpinned library/platform versions are not promised.
6. Produce a compact evidence record linking the full local artifacts and source-access instructions. Include independent software-check results, base-versus-selected results for every scoreable view, holdout or in-sample designation, sensitivity observations, known geometric limitations, and physical properties not evaluated.

### Completion and target acceptance

Use [M1's completion checks](status.md#m1--reproducible-baseline-fit) to decide whether the baseline investigation is reproducible. Do not demand an invented IoU cutoff or claim acceptance because the search finished. Proposed target thresholds should be justified using baseline residuals, preparation uncertainty, and intended use, then recorded as unresolved or owner-confirmed in status. Physical construction requirements need separate evidence if requested.

## Validation

For relevant application changes, the existing suites are:

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s tools/generic_screening/tests -v
```

If the system temporary directory is restricted, set `IMAGE_EVAL_TEST_TMP` to an existing writable scratch directory. Choose suites appropriate to the change. Documentation-only changes generally need link/anchor, command-option, claim, and final-diff review rather than rerunning application suites. There is no repository-provided documentation checker or CI workflow at the reviewed baseline.

Evidence belongs under `docs/evidence/` when useful, linked from [the status ledger](status.md#evidence). Record exact code ref, environment, commands actually run, outcomes, and limitations; distinguish observed test results from inspected test definitions. An older ref's passing tests are not automatically evidence for changed application code.
