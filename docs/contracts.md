# Scope and data contracts

Describes existing behavior at the [reviewed code baseline](status.md#baseline), not a new implementation authorization. [Operations](operations.md) owns commands; [status](status.md) owns current progress.

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
