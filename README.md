# Mask Generator

Three curved cardboard pieces: multiview generation and evaluation.

Generate views of one **exactly three-piece** parameterized cardboard assembly and compare its projections against supplied reference masks. This is the active project. The earlier generic image checks are optional screening and do not establish a shape match.

**No actual user reference images are present in this workspace.** All geometry, dimensions, and cameras in the included demo are arbitrary synthetic fixtures. No result claims to match the absent target.

## Available now

- Exactly three continuous curved-strip meshes, each with length, width, thickness, signed bend, rotation, and translation. No additional supports or structural pieces.
- Deterministic CPU rendering with depth buffering, orthographic/perspective cameras, RGBA images, foreground masks, visible piece IDs, and geometry/camera provenance.
- Comparison against every supplied view, with one geometry and a fixed shared camera rig. No independent camera adjustment, image warping, centering, or rescaling to conceal discrepancies.
- Silhouette and contour measurements, optional visible per-piece comparisons, ignored regions, batch ranking, and bounded review overlays. No model calls.
- Seeded geometry-only random search within explicit user-supplied bounds. This is a baseline search, not a solved reconstruction or global optimization system.

## Run the synthetic demonstration

Requires Python 3.10+, NumPy, and Pillow. From this folder:

```powershell
python -m pip install -r requirements.txt
python demo.py --output runs\demo-001
```

The demo generates three candidates and four reference views under `runs/demo-001`. Its unchanged candidate scores IoU 1.0 because it generated the reference masks; this tests consistency only. The altered candidates rank lower. Generated overlays use red for reference-only, cyan for candidate-only, gray for overlap, and yellow for ignored pixels. Generated runs are not committed.

Every command requires a new output directory. Source images and prior runs are preserved.

## Inputs still needed

1. **The actual reference images**, including all available viewing angles, preferably at original resolution. None are available here.
2. **Which images depict the same target assembly**, if there are alternative versions.
3. **Foreground masks and a camera interpretation**, or source images from which to prepare/estimate them. Automatic photograph segmentation and camera calibration are not implemented. Known viewpoints, lens/crop information, landmarks, and a known dimension help when available. You need not invent numeric cameras yourself; they can be estimated later from actual references, with uncertainty recorded.
4. **Any known physical constraints**: cardboard dimensions/thickness, permitted bend types, cuts, joins, contact, or intersection rules. These are unspecified. Absolute dimensions are unnecessary for relative silhouette experiments but are needed for physical scale or fabrication claims.

Acceptance tolerances and priority views are also unspecified. Reports rank candidates without declaring them acceptable. Extra presentation angles can be rendered separately once geometry is established; only views with references can receive a target-match score.

## Scene and camera schema

`examples/synthetic-scene.json` demonstrates the format. Its numbers are synthetic, not target estimates.

| Field | Meaning |
| --- | --- |
| `schema_version` | `1` |
| `units` | Descriptive unit label; keep cameras and geometry at the same scale |
| `segments` | Longitudinal tessellation, 8–256; keep fixed for comparison |
| `pieces` | Exactly three objects, ordered as visible-label IDs 1, 2, 3 |
| `length`, `width`, `thickness` | Positive dimensions; length is center-surface arc length |
| `bend_degrees` | Signed constant-curvature bend, magnitude 1–330 degrees |
| `rotation_degrees` | `[x, y, z]` degrees, applied X then Y then Z |
| `translation` | World `[x, y, z]` after rotation |
| `cameras` | Explicit camera rig for required reference views |

Locally the strip bends in XZ and extends across Y. Thickness follows the curved surface normal. Radius is `length / abs(bend_radians)`. Each piece is a closed connected mesh. This initial family supports cylindrical bends; variable curvature, twisting, cutouts, folds, and arbitrary outlines are not implemented. Reference evidence may require extending it. Three meshes does not prove a collision-free, joinable, or stable assembly. Synthetic pieces may intersect.

Each camera needs `id`, `eye`, `target`, `up`, `image_size: [width, height]`, and `projection`. Orthographic cameras use `vertical_span` in world units; perspective cameras use `fov_y_degrees`. Image dimensions must be 32–2048. No lens distortion or antialiasing is modeled. Geometry on/behind the camera plane is rejected. Out-of-frame vertices and visible pixels per piece are reported.

```powershell
python cardboard.py your-scene.json --output runs\render-001
```

Per-view outputs: `<id>.png` (RGBA), `<id>.mask.png` (foreground), `<id>.ids.png` (0 background, IDs 1/2/3). Manifests preserve the exact scene and camera settings. All views derive from the same geometry.

## References and batch comparison

Copy `references.template.json` and supply a nonempty `views` list. Each view has `id`, `camera`, and `mask`. Camera/view IDs must match. Foreground masks are grayscale PNGs with 0 background and 1 or 255 foreground, at exactly the camera image dimensions. Paths are relative to the reference manifest or absolute. The synthetic manifest illustrates structure, not actual calibration.

Optional `ignore_mask` excludes white pixels. Optional `piece_masks` maps `"1"`, `"2"`, `"3"` to manually corresponding visible piece masks; they must be disjoint and inside the assembly silhouette. An explicitly empty mask means fully occluded. Unlabeled photographs alone cannot establish hidden pieces or correspondence.

For a meaningful existing alpha channel:

```powershell
python extract_alpha_mask.py transparent-reference.png --output reference-mask.png
```

This helper does not segment ordinary photographs. Background removal and camera estimation remain preparation steps once actual images are supplied.

```powershell
python compare.py your-candidates --candidate-dir --references your-references.json --output runs\comparison-001 --review-limit 4
```

Candidate scene cameras must equal the shared reference rig. Every declared reference view is required for every candidate. Camera error can mimic geometry error, so establish uncertain cameras before interpreting scores. A single reference can be compared but leaves substantial 3D ambiguity.

## Supported comparison measures

| Measure | Supports | Limits |
| --- | --- | --- |
| Silhouette IoU / Dice | Projected overlap at a supplied camera | Requires reliable masks/registration; hidden shape ambiguous |
| Boundary F1 | Contour agreement within pixel tolerance | Default 2 px is diagnostic, not an acceptance rule |
| Symmetric contour distance | Mean separation divided by image diagonal | Deterministically sampled, up to 1,024 points per contour |
| Contour p95 distance | 95th-percentile normalized separation | Sampled diagnostic, not exact Hausdorff distance |
| Foreground area ratio | Relative projected area | Does not establish spatial agreement |
| Visible piece-mask metrics | Agreement of corresponding visible pieces | Needs labels; cannot inspect hidden surfaces |
| Worst-view / mean IoU | Joint multiview fit of one geometry | Limited to supplied views and the geometry family |

Ranking favors highest **worst-view IoU**, then mean IoU. Per-piece scores are separate from ranking. No composite acceptance score or target threshold is invented. Blur and duplicate detection never establish a shape match.

Raw color difference and SSIM are absent: texture, lighting, shadows, and style may vary independently of geometry. Keypoint reprojection, depth/normal agreement, and calibrated 3D reconstruction require corresponding landmarks, depth maps, calibration, or other evidence. Silhouette agreement alone cannot prove unseen-view agreement, physical piece count in a photograph, fabrication feasibility, or unique geometry.

## Search within explicit bounds

```powershell
python search.py your-base-scene.json --bounds your-bounds.json --references your-references.json --output runs\search-001 --count 50 --seed 7
```

Bounds map parameter paths to `[lower, upper]`. Supported examples are `pieces.0.bend_degrees`, `pieces.1.translation.2`, and `pieces.2.rotation_degrees.0` (0-based indices). No actual target bounds are supplied. The demo bounds apply only to the arbitrary synthetic example.

The base is included as a baseline. Seeded uniform sampling creates additional geometries, preserving cameras. Invalid combinations are rejected with bounded retries. High-dimensional fitting will need tighter constraints and a more efficient optimizer after real references arrive.

## Compact reports and low-token review

`summary.txt` gives counts, reference state, best worst/mean IoU, and weakest view. `ranking.csv` gives ordering; `metrics.jsonl` keeps complete per-view/per-piece results locally. `references.used.json` preserves cameras and mask hashes. `review_queue.json` lists selected overlays and omitted views.

Default visual review is capped at **4 candidates × 8 weakest supplied views**. All supplied views are scored; the cap affects previews only. Lower `--review-limit` or set it to zero to omit previews. Start optional model review with the summary, queue, and selected overlays, opening original references for specific uncertainty. Bounded review does not certify a batch. No network/model calls occur and no particular token savings percentage is claimed.

Comparison/search exit codes: `0` = completed without candidate errors; `1` = reports include invalid candidates; `2` = input/configuration/output failure. Completion does not mean target acceptance. Repeatability assumes unchanged inputs, paths, settings, and library versions. Search records its bounds and seed.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests cover exactly three pieces, closed connected meshes, identical/shifted silhouettes, ignored regions, hidden pieces, depth-buffer occlusion, perspective rendering, camera-plane rejection, fixed camera rigs, explicit masks, deterministic search, exact-before-wrong ranking, invalid-candidate reports, review caps, and alpha-mask extraction. If needed, set `IMAGE_EVAL_TEST_TMP` to a writable scratch folder.

These tests establish software behavior on synthetic fixtures. Actual target matching awaits the references and prepared masks/cameras.

## Optional generic screening

The earlier local image-quality and duplicate checks are in `tools/generic_screening`. They do not establish a reference-shape match. Run their tests separately with `python -m unittest discover -s tools/generic_screening/tests -v`.
