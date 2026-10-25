# Implementation map

Use [contracts](contracts.md) for semantics and [operations](operations.md) for commands. This map routes work to existing code; it does not propose another pipeline.

| Responsibility | Existing implementation | Existing tests |
| --- | --- | --- |
| Validate scene and cameras; build closed strips | [cardboard.py](../cardboard.py): `validate_scene`, `piece_mesh`, `rotation` | [test_geometry.py](../tests/test_geometry.py): `test_piece_count_and_invalid_geometry`, `test_each_piece_is_closed_connected_mesh` |
| Project and rasterize with depth/visible IDs | [cardboard.py](../cardboard.py): `camera_frame`, `render`, `render_scene` | `test_depth_buffer_hides_coincident_back_pieces`, `test_perspective_and_near_plane` |
| Load explicit masks/references; enforce shared rig | [compare.py](../compare.py): `load_mask`, `load_references`, `compare_scene` | `test_masks_are_explicit_and_size_checked`, `test_reject_camera_drift_and_missing_views` |
| Compute silhouette, ignored-region, contour, and part metrics | [compare.py](../compare.py): `silhouette_metrics`, `boundary`, `distances` | `test_identity_shift_and_ignore_regions`, `test_hidden_piece_and_empty_candidate_metrics` |
| Rank candidates and bound review previews | [compare.py](../compare.py): `evaluate_batch`, `save_overlay` | `test_batch_ranks_exact_before_wrong_and_reports_invalid_candidate`, `test_preview_cap_still_scores_every_reference_view` |
| Seeded geometry-only sampling | [search.py](../search.py): `parameter_target`, `make_candidates`, `main` | `test_geometry_only_seeded_search` |
| Extract alpha foreground | [extract_alpha_mask.py](../extract_alpha_mask.py): `main` | `test_alpha_mask_helper` |
| Generate arbitrary synthetic fixtures | [demo.py](../demo.py): `synthetic_scene`, `build_demo`; [examples](../examples/synthetic-scene.json) | Fixtures used by geometry tests; demo command is a separate smoke check |
| Optional generic image triage | [evaluate.py](../tools/generic_screening/evaluate.py) | Separate [test_pipeline.py](../tools/generic_screening/tests/test_pipeline.py), nine tests |

The geometry suite contains twelve tests at the reviewed baseline. This mapping describes inspected coverage, not a fresh test run or exhaustive guarantees. See [status evidence](status.md#evidence) for recorded executions.

Data flow: scene plus camera rig produces projections; references plus projections produce measurements; batch measurements produce rank and bounded overlays. Search creates candidate scenes and reuses the same comparison pipeline. The generic tool is independent and cannot set shape-match acceptance.
