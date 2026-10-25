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

## Validation

For relevant application changes, the existing suites are:

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s tools/generic_screening/tests -v
```

If the system temporary directory is restricted, set `IMAGE_EVAL_TEST_TMP` to an existing writable scratch directory. Choose suites appropriate to the change. Documentation-only changes generally need link/anchor, command-option, claim, and final-diff review rather than rerunning application suites. There is no repository-provided documentation checker or CI workflow at the reviewed baseline.

Evidence belongs under `docs/evidence/` when useful, linked from [the status ledger](status.md#evidence). Record exact code ref, environment, commands actually run, outcomes, and limitations; distinguish observed test results from inspected test definitions. An older ref's passing tests are not automatically evidence for changed application code.
