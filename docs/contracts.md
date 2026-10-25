# Scope and data contracts

Describes existing behavior at the [reviewed code baseline](status.md#baseline) and explicitly labeled preparation/decision contracts for planned M1 work. A planned artifact is not a newly implemented runtime feature. [Operations](operations.md) owns procedures; [status](status.md) owns task state.

## Scope and interpretation

The task is to arrange exactly three curved cardboard pieces so their combined form agrees with reference images across supplied viewpoints. Do not reinterpret it as a conventional desk, dinosaur decorations, or an assembly with extra structural pieces.

The current family is three continuous, constant-curvature cylindrical strips with thickness. Variable curvature, twisting, cutouts, folds, and arbitrary outlines are not implemented. A single geometry generates every view. Three meshes are enforced in the scene, not inferred from reference photographs. Collision-free placement, joins, material behavior, stability, and fabrication feasibility are not validated; even synthetic pieces may intersect.

Silhouette agreement does not uniquely determine hidden geometry or prove unseen-view agreement. Camera error can mimic geometry error. Color difference and SSIM are not used because appearance varies with texture, lighting, shadows, and style. Landmark reprojection, depth/normal comparison, calibrated reconstruction, automatic photo segmentation, and camera estimation require additional evidence and implementation. They are not current capabilities.

Generic blur/exposure/duplicate checks are technical screening only and never establish a shape match. There are no target acceptance thresholds; comparison returns `not_determined_no_user_thresholds`. A completed command, perfect synthetic score, or passing software test is not owner acceptance.

## Scene format

See [synthetic scene](../examples/synthetic-scene.json) and `validate_scene` in [cardboard.py](../cardboard.py).

| Field | Existing interpretation |
| --- | --- |
| `schema_version` | `1` |
| `units` | Descriptive metadata; consistent geometry/camera units are the caller's responsibility |
| `segments` | Integer 8–256, default 48; use consistent tessellation for comparisons |
| `pieces` | Exactly three objects; list order assigns visible IDs 1, 2, 3 |
| `length`, `width`, `thickness` | Positive finite numbers; length is center-surface arc length |
| `bend_degrees` | Finite signed bend, absolute value 1–330 degrees |
| `rotation_degrees` | Finite `[x, y, z]` degrees, applied X, then Y, then Z |
| `translation` | Finite world `[x, y, z]` after rotation |
| `cameras` | Nonempty list of explicit cameras |

Locally a strip bends in XZ, spans Y across its width, and has thickness along the surface normal. Radius is `length / abs(bend_radians)`; thickness must be less than twice that radius. Each generated piece is a closed connected mesh. Piece objects reject fields outside the listed dimensions, bend, rotation, and translation. Arbitrary demo dimensions are not target requirements.

## Camera format

Every camera has unique `id` (letters, digits, underscore, hyphen), finite three-vectors `eye`, `target`, `up`, and `image_size: [width, height]` with integer dimensions 32–2048. Eye/target/up must define a nondegenerate frame.

`projection` is `orthographic` with positive finite `vertical_span`, or `perspective` with finite `fov_y_degrees` from 1–170. The vertical span uses scene units. Unknown camera fields are rejected. No lens distortion or antialiasing is modeled. The renderer rejects geometry at/behind its near plane (`1e-6` depth); it does not clip crossing triangles into a valid result. Out-of-frame vertices and visible pixel counts per piece are reported.

Comparison requires exactly the reference camera IDs and camera definitions, independent of list order. No missing or additional camera definitions, independently fitted per-view cameras, automatic image alignment, rescaling, cropping, or warping are applied. A single reference is allowed but leaves substantial 3D ambiguity. Additional presentation views can be rendered separately.

## Reference format

The [reference template](../references.template.json) intentionally has no usable views until populated. `schema_version` is `1`; `views` is nonempty for comparison. Each view needs `id`, `camera`, and `mask`; its ID must match its camera ID. Reference view IDs are unique. Mask paths resolve relative to the manifest or may be absolute. Optional `reference_state` describes provenance; the pipeline does not independently verify that description.

Masks use Pillow mode `1` or `L` and values 0, 1, or 255; nonzero is foreground. The pixel budget is 4,194,304. Dimensions must exactly match the camera image size. The assembly mask must contain foreground before and after applying ignored regions; no photograph segmentation is performed.

Optional `ignore_mask` excludes nonzero pixels. Optional `piece_masks` maps string IDs `"1"`, `"2"`, `"3"` to manually corresponding visible-piece masks. They match dimensions, remain inside the assembly silhouette, and do not overlap. An empty part mask means fully occluded; omitted IDs are not scored. Part masks need not cover the complete assembly silhouette. These labels do not establish hidden geometry.

`extract_alpha_mask.py` requires an actual alpha channel and a nonempty thresholded foreground, with threshold 1–255 (default 128) and the same pixel budget. It does not validate that alpha represents the intended object. Choose masks and camera interpretations from real evidence; record uncertainty rather than fabricate them.

## Reference preparation bundle

This is the artifact contract for planned M1 work. It is maintained alongside the existing runtime inputs; no new loader, calibration tool, or validator is implemented by this document. Keep local image assets under `inputs/<target>/<revision>/` and runs under `runs/`; both are ignored by Git. Commit compact evidence summaries when appropriate, with source hashes and a usable location for supporting assets. A hash alone does not let another developer reproduce a run.

The bundle contains unchanged source images, prepared masks, runtime reference manifests, a base scene/bounds, and one `preparation-notes.json` sidecar. The sidecar is for review/provenance and is not read by the current programs. Do not add uncertainty or role fields to camera objects, which reject unknown fields.

Record bundle revision, target identifier, date, and these entries for each supplied image:

| Entry | Required meaning |
| --- | --- |
| `view_id`, source location/hash, target grouping | Stable view identity and which assembly/version it depicts |
| Disposition and reason | Scoreable, unresolved, excluded, or an alternative target; preserve reasons for every omission |
| Original/prepared dimensions and transform | EXIF orientation, crop, resize, and any lens correction applied; unchanged raw image remains available |
| Mask/ignore/part paths and review notes | Mask provenance, treatment of shadows/background/occlusion, correspondence basis for any piece labels |
| Projection basis and camera revision | Known calibration versus inferred projection, coordinate/scale convention, estimation method, and supporting landmarks/metadata |
| Uncertainty and unresolved assumptions | Evidence-backed ranges where available; otherwise explicitly unknown, not invented precision |
| Fit/check role and rationale | Assignment made before fitting, or why an independent check view is unavailable |

Separate runtime manifests may select fit views, withheld check views, and all scoreable views. Each manifest must satisfy the existing reference format. The scene passed to each comparison must contain exactly that manifest's camera definitions; when exporting a scene for a subset, change only its camera list and preserve the three pieces and tessellation. This packaging is currently manual, not a supported split/export command.

Freeze source/mask hashes, camera revisions, view assignments, settings, and geometry bounds before comparing candidates. A changed mask, crop, camera, or split creates a new experiment revision. Unresolved images remain in the inventory and cannot silently become evidence of successful agreement.

## Geometry suitability decision

For M1-4, record one of these dispositions with images/metrics and the considered alternatives. These are development decisions; no new acceptance threshold is introduced.

| Observation | Disposition and next step |
| --- | --- |
| Independently checked projections work; reference preparation is credible; residuals respond to changes within justified bounds | Proceed with the current family and document the baseline |
| Misalignment is consistent with uncertain crop, pose, lens, or mask boundaries | Investigate preparation; revise/freeze inputs, then rerun comparison before expanding geometry |
| Different plausible camera or mask choices imply incompatible shape conclusions | Insufficient evidence; record ambiguity and identify the specific additional view/landmark needed |
| Credible views show required variable curvature, twist, outline/cutout, or other structure that cylindrical strips cannot represent | Propose the smallest necessary family extension while preserving exactly three pieces; name affected code and independent tests |
| Only evidence is a weak score or failure of one random search | Inconclusive; inspect coverage, bounds, initialization, resolution, and uncertainty before declaring the family inadequate |

A family-extension proposal needs the observed unsupported feature, views supporting it, reasons calibration/mask errors do not explain it, a parameterization sketch, any schema implications, and tests for mesh continuity/piece count and projected behavior. It is not an instruction to add supports or silently change the task. If physical constraints remain unknown, keep them unknown rather than treating intersecting meshes as a valid construction.

## Measurements and ranking

See `silhouette_metrics` and `evaluate_batch` in [compare.py](../compare.py).

| Measurement | Definition and limitation |
| --- | --- |
| IoU / Dice | Foreground overlap in comparable pixels; masks must share dimensions |
| `foreground_area_ratio` | Candidate/reference foreground area; no spatial agreement guarantee |
| `boundary_f1` | Full-raster contour tolerance matching; default 2 px, configurable 0–10 through comparison CLI |
| `sampled_symmetric_contour_distance_diagonal` | Average of directed mean contour distances divided by image diagonal |
| `sampled_contour_p95_diagonal` | Maximum of the two directed 95th percentiles divided by diagonal; not exact Hausdorff distance |
| `piece_scores` | The same metrics for supplied corresponding visible-piece masks; separate from ranking |

Distances deterministically subsample each contour to at most 1,024 points by default. The Python batch API permits caps 32–4,096; there is no contour-cap CLI option. Distance results are null when either comparable contour is empty. Assembly references cannot be empty; part comparisons permit emptiness: both empty gives IoU/Dice/boundary F1 1, only one empty gives overlap/F1 0, and an empty reference gives null area ratio.

Contours are extracted before applying the valid-pixel mask so ignored cuts do not create artificial edges. Scores remain dependent on mask and camera quality and raster resolution. Record settings with comparisons.

Every candidate is evaluated across every declared view; a view error invalidates that candidate's comparison rather than silently averaging fewer views. Successfully evaluated candidates rank by descending worst-view IoU, then descending mean-view IoU, then candidate path. Weakest-view ties use view ID. Per-piece scores do not enter ranking. There is no priority-view weighting or user acceptance threshold implemented.

## Search bounds

[search.py](../search.py) samples only geometry fields using explicit `[lower, upper]` finite bounds. Supported paths are `pieces.0/1/2.length`, `.width`, `.thickness`, `.bend_degrees`, `.translation.0/1/2`, and `.rotation_degrees.0/1/2`. Indices in parameter paths are 0-based, unlike visible piece IDs.

Bounds are nonempty and ordered. Cameras remain unchanged. The base is included plus 1–10,000 additional candidates (CLI default 20); random seed defaults to 0. Invalid sampled geometries are retried, failing after more than `count * 50` attempts. This is reproducible uniform random sampling within bounds, not a guarantee of the global optimum. [Example bounds](../examples/bounds.synthetic.json) are synthetic only.

## Bounded review

Comparison previews select the top four ranked candidates by default; `--review-limit` permits 0–12. Each overlay contains up to eight weakest supplied views by ascending IoU, then view ID. Every reference view is still scored. The queue lists selected IDs and omitted-view counts. Overlay colors: red reference-only, cyan candidate-only, gray overlap, yellow ignored.

Local scripts make no network/model calls. Review caps bound supplied previews, not a measured token savings percentage or batch acceptance. Optional model review can start with summary, queue, and selected overlays, then open original references only for specific uncertainty.

## Reproducibility and provenance

Reproducibility assumes unchanged scene, references, paths, settings, and library versions. Comparison preserves scene hashes and masks/cameras in its reports; search records bounds and seed. The render manifest's legacy `geometry_sha256` field actually hashes the entire sorted scene JSON, including cameras/metadata, via `scene_hash`; it is not a geometry-only digest. This documentation records the existing behavior without renaming a runtime field.

Reports may contain absolute paths. Reference state is declared provenance, not proof of supplied image authenticity or target acceptance. Generated artifacts stay local under ignored run directories; commands and artifact names are owned by [operations](operations.md).
