import copy
import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from collections import Counter

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cardboard import piece_mesh, read_json, render, render_scene, validate_scene, write_json
from compare import compare_scene, evaluate_batch, load_mask, load_references, silhouette_metrics
from demo import synthetic_scene
from extract_alpha_mask import main as extract_alpha
from search import make_candidates


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("IMAGE_EVAL_TEST_TMP"))
        self.root = Path(self.tmp.name)
        self.scene = synthetic_scene()
        self.scene["segments"] = 16
        self.scene["cameras"] = self.scene["cameras"][:2]
        for c in self.scene["cameras"]:
            c["image_size"] = [96, 96]

    def tearDown(self):
        self.tmp.cleanup()

    def references(self):
        render_scene(self.scene, self.root / "reference")
        manifest = {"schema_version": 1, "reference_state": "synthetic_test", "views": [
            {"id": c["id"], "camera": c, "mask": f"reference/{c['id']}.mask.png"}
            for c in self.scene["cameras"]]}
        path = self.root / "references.json"
        write_json(path, manifest)
        return path

    def test_piece_count_and_invalid_geometry(self):
        for count in (0, 2, 4):
            scene = copy.deepcopy(self.scene)
            scene["pieces"] = (scene["pieces"] * 2)[:count]
            with self.assertRaises(ValueError):
                validate_scene(scene)
        for key, value in [("length", -1), ("thickness", 20), ("bend_degrees", 0)]:
            scene = copy.deepcopy(self.scene)
            scene["pieces"][0][key] = value
            with self.assertRaises(ValueError):
                validate_scene(scene)

    def test_each_piece_is_closed_connected_mesh(self):
        for piece in self.scene["pieces"]:
            vertices, faces = piece_mesh(piece, 32)
            edges = Counter(tuple(sorted((int(a), int(b)))) for face in faces
                            for a, b in zip(face, np.roll(face, -1)))
            self.assertEqual(set(edges.values()), {2})
            self.assertEqual(len(vertices) - len(edges) + len(faces), 2)
            adjacency = {i: set() for i in range(len(vertices))}
            for a, b in edges:
                adjacency[a].add(b)
                adjacency[b].add(a)
            reached, todo = set(), [0]
            while todo:
                point = todo.pop()
                if point not in reached:
                    reached.add(point)
                    todo.extend(adjacency[point] - reached)
            self.assertEqual(len(reached), len(vertices))

    def test_identity_shift_and_ignore_regions(self):
        reference = np.zeros((64, 64), bool)
        reference[12:45, 14:43] = True
        exact = silhouette_metrics(reference, reference)
        self.assertEqual(exact["iou"], 1)
        self.assertEqual(exact["boundary_f1"], 1)
        self.assertEqual(exact["sampled_symmetric_contour_distance_diagonal"], 0)
        candidate = np.roll(reference, 5, axis=1)
        shifted = silhouette_metrics(candidate, reference)
        self.assertLess(shifted["iou"], 1)
        self.assertGreater(shifted["sampled_symmetric_contour_distance_diagonal"], 0)
        candidate = reference.copy()
        candidate[0, 0] = True
        valid = np.ones_like(reference)
        valid[:3, :3] = False
        self.assertEqual(silhouette_metrics(candidate, reference, valid)["iou"], 1)

    def test_hidden_piece_and_empty_candidate_metrics(self):
        mask = np.zeros((32, 32), bool)
        mask[5:10, 5:10] = True
        empty = np.zeros_like(mask)
        self.assertEqual(silhouette_metrics(empty, mask)["iou"], 0)
        self.assertEqual(silhouette_metrics(empty, empty, allow_empty=True)["iou"], 1)
        self.assertEqual(silhouette_metrics(mask, empty, allow_empty=True)["iou"], 0)
        with self.assertRaises(ValueError):
            silhouette_metrics(mask, empty)

    def test_reject_camera_drift_and_missing_views(self):
        _, refs = load_references(self.references())
        drift = copy.deepcopy(self.scene)
        drift["cameras"][0]["eye"][0] += 1
        with self.assertRaises(ValueError):
            compare_scene(drift, refs)
        drift = copy.deepcopy(self.scene)
        drift["cameras"].pop()
        with self.assertRaises(ValueError):
            compare_scene(drift, refs)

    def test_masks_are_explicit_and_size_checked(self):
        Image.new("RGB", (32, 32), "white").save(self.root / "photo.png")
        with self.assertRaises(ValueError):
            load_mask(self.root / "photo.png")
        Image.new("L", (32, 32), 128).save(self.root / "gray.png")
        with self.assertRaises(ValueError):
            load_mask(self.root / "gray.png")
        with self.assertRaises(ValueError):
            silhouette_metrics(np.ones((32, 32), bool), np.ones((64, 64), bool))

    def test_depth_buffer_hides_coincident_back_pieces(self):
        scene = copy.deepcopy(self.scene)
        scene["pieces"] = [copy.deepcopy(scene["pieces"][0]) for _ in range(3)]
        for i, piece in enumerate(scene["pieces"]):
            piece["translation"] = [0, i * 2, 0]
        camera = scene["cameras"][0] | {"eye": [0, -10, .5], "target": [0, 0, .5]}
        _, labels, diagnostic = render(scene, camera)
        self.assertTrue(np.any(labels == 1))
        self.assertFalse(np.any(labels == 2))
        self.assertFalse(np.any(labels == 3))
        self.assertEqual(diagnostic["visible_piece_pixels"]["2"], 0)

    def test_perspective_and_near_plane(self):
        camera = self.scene["cameras"][0] | {"projection": "perspective", "fov_y_degrees": 40}
        validate_scene(self.scene | {"cameras": [camera]})
        a, labels, _ = render(self.scene, camera)
        self.assertTrue(labels.any())
        self.assertTrue(np.array_equal(a, render(self.scene, camera)[0]))
        camera = camera | {"eye": [0, 0, 0], "target": [0, 1, 0]}
        with self.assertRaises(ValueError):
            render(self.scene, camera)

    def test_geometry_only_seeded_search(self):
        bounds = {"pieces.1.bend_degrees": [-110, -50], "pieces.0.translation.0": [-.3, .3]}
        a, b = make_candidates(self.scene, bounds, 5, 11), make_candidates(self.scene, bounds, 5, 11)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 6)
        self.assertTrue(all(s["cameras"] == self.scene["cameras"] for s in a))
        with self.assertRaises(ValueError):
            make_candidates(self.scene, {"cameras.0.eye.0": [-1, 1]}, 2, 0)

    def test_batch_ranks_exact_before_wrong_and_reports_invalid_candidate(self):
        references = self.references()
        write_json(self.root / "exact.json", self.scene)
        wrong = copy.deepcopy(self.scene)
        wrong["pieces"][0]["translation"][0] += .8
        write_json(self.root / "wrong.json", wrong)
        write_json(self.root / "invalid.json", {"pieces": []})
        summary = evaluate_batch([self.root / f"{name}.json" for name in ("exact", "wrong", "invalid")],
                                 references, self.root / "report", review_limit=1)
        self.assertEqual(summary["evaluated_count"], 2)
        self.assertEqual(summary["error_count"], 1)
        self.assertEqual(summary["best"]["worst_view_iou"], 1)
        self.assertTrue(summary["best"]["candidate"].endswith("exact.json"))
        queue = read_json(self.root / "report" / "review_queue.json")
        self.assertEqual(len(queue["items"]), 1)
        self.assertTrue((self.root / "report" / "review-01.png").exists())
        self.assertEqual(summary["model_calls"], 0)

    def test_alpha_mask_helper(self):
        image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        image.paste((180, 130, 70, 255), (8, 8, 24, 24))
        image.save(self.root / "alpha.png")
        with contextlib.redirect_stdout(io.StringIO()):
            extract_alpha([str(self.root / "alpha.png"), "--output", str(self.root / "mask.png")])
        self.assertEqual(int(load_mask(self.root / "mask.png").sum()), 256)

    def test_preview_cap_still_scores_every_reference_view(self):
        camera = self.scene["cameras"][0]
        self.scene["segments"] = 8
        self.scene["cameras"] = [camera | {"id": f"view-{n}", "image_size": [32, 32]}
                                 for n in range(9)]
        references = self.references()
        path = self.root / "candidate.json"
        write_json(path, self.scene)
        summary = evaluate_batch([path], references, self.root / "report", review_limit=1)
        queue = read_json(self.root / "report" / "review_queue.json")["items"][0]
        self.assertEqual(summary["reference_views"], 9)
        self.assertEqual(len(queue["selected_view_ids"]), 8)
        self.assertEqual(queue["omitted_view_count"], 1)


if __name__ == "__main__":
    unittest.main()
