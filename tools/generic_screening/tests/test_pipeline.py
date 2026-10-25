import contextlib
import io
import json
import os
from pathlib import Path
import random
import shutil
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evaluate


def pattern(path, size=(600, 600)):
    image = Image.new("RGB", size, "#538659")
    draw = ImageDraw.Draw(image)
    for n in range(0, min(size), 25):
        draw.line((n, 0, size[0] - 1, size[1] - n - 1), fill=(n % 256, 80, 200), width=5)
    image.save(path)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("IMAGE_EVAL_TEST_TMP"))
        self.root = Path(self.tmp.name)
        self.inputs = self.root / "input images"
        self.inputs.mkdir()
        self.cfg = evaluate.load_config()

    def tearDown(self):
        self.tmp.cleanup()

    def test_uniform_transparent_and_corrupt(self):
        Image.new("RGB", (600, 600), "black").save(self.inputs / "dark.png")
        Image.new("RGBA", (600, 600), (255, 0, 0, 0)).save(self.inputs / "alpha.png")
        (self.inputs / "bad.jpg").write_bytes(b"not an image")
        dark = evaluate.analyze(self.inputs / "dark.png", self.cfg)
        self.assertTrue({"near_uniform", "very_dark", "low_detail_proxy"} <= set(dark["flags"]))
        alpha = evaluate.analyze(self.inputs / "alpha.png", self.cfg)
        self.assertIn("no_visible_pixels", alpha["flags"])
        self.assertNotIn("very_dark", alpha["flags"])
        self.assertEqual(evaluate.analyze(self.inputs / "bad.jpg", self.cfg)["technical_status"], "error")

    def test_exif_oriented_dimensions(self):
        exif = Image.Exif()
        exif[274] = 6
        Image.new("RGB", (300, 700), "green").save(self.inputs / "rotated.jpg", exif=exif)
        row = evaluate.analyze(self.inputs / "rotated.jpg", self.cfg)
        self.assertEqual((row["width"], row["height"]), (700, 300))

    def test_limits_and_aspect(self):
        path = self.inputs / "wide.png"
        pattern(path, (600, 300))
        row = evaluate.analyze(path, self.cfg | {"aspect_ratio_range": [0.9, 1.1]})
        self.assertIn("small_dimensions", row["flags"])
        self.assertIn("aspect_ratio_outside_range", row["flags"])
        self.assertEqual(evaluate.analyze(path, self.cfg | {"max_pixels": 100})["flags"], ["pixel_limit"])
        self.assertEqual(evaluate.analyze(path, self.cfg | {"max_file_mb": .000001})["flags"], ["file_size_limit"])

    def test_exact_and_perceptual_duplicates(self):
        first = self.inputs / "a.png"
        pattern(first)
        shutil.copyfile(first, self.inputs / "b.png")
        with Image.open(first) as image:
            image.save(self.inputs / "c.bmp")
        rows = [evaluate.analyze(p, self.cfg) for p in sorted(self.inputs.iterdir())]
        evaluate.annotate_duplicates(rows, self.cfg)
        self.assertEqual(rows[1]["exact_duplicate_of"], str(first))
        self.assertEqual(rows[2]["near_duplicate_candidate_of"], str(first))
        queue = evaluate.select_review(rows, self.cfg)
        self.assertNotIn(str(self.inputs / "b.png"), [q["path"] for q in queue])

    def test_hash_index_matches_brute_force(self):
        rng = random.Random(19)
        values = [rng.getrandbits(64) for _ in range(150)]
        values.extend(v ^ 7 for v in values[:15])
        index = evaluate.HashIndex()
        inserted = []
        for i, value in enumerate(values):
            matches = [(int((v ^ value).bit_count()), p) for v, p in inserted
                       if (v ^ value).bit_count() <= 4]
            self.assertEqual(index.nearest(value, 4), min(matches) if matches else None)
            path = str(i)
            index.add(value, path)
            inserted.append((value, path))

    def test_bounded_deterministic_queue_reserves_unflagged_samples(self):
        rows = [{"path": f"image-{n:03d}", "sha256": str(n), "width": 600, "height": 600,
                 "technical_status": "warn" if n < 20 else "pass",
                 "flags": [f"flag-{n % 5}"] if n < 20 else []} for n in range(25)]
        cfg = self.cfg | {"review_limit": 6, "unflagged_sample_count": 2}
        queue = evaluate.select_review(rows, cfg)
        self.assertEqual(len(queue), 6)
        self.assertEqual(sum(q["selection_reason"] == "unflagged_spot_check" for q in queue), 2)
        self.assertEqual(queue, evaluate.select_review(rows, cfg))
        self.assertEqual(evaluate.select_review(rows, cfg | {"review_limit": 0}), [])

    def test_cli_reports_and_repeatability_and_overwrite_guard(self):
        pattern(self.inputs / "normal.png")
        (self.inputs / "corrupt.png").write_bytes(b"broken")
        reports = [self.root / "run 1", self.root / "run 2"]
        for report in reports:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(evaluate.main([str(self.inputs), "--output", str(report)]), 1)
            summary = json.loads((report / "summary.json").read_text())
            self.assertEqual(summary["total_images"], 2)
            self.assertEqual(summary["technical_status_counts"]["error"], 1)
            self.assertEqual(summary["domain_status"], "not_evaluated")
            self.assertTrue((report / "contact_sheet.jpg").exists())
        self.assertEqual((reports[0] / "metrics.jsonl").read_bytes(), (reports[1] / "metrics.jsonl").read_bytes())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(evaluate.main([str(self.inputs), "--output", str(reports[0])]), 2)

    def test_discovery_excludes_reports_and_accepts_explicit_unknown_extension(self):
        pattern(self.inputs / "image.png")
        output = self.inputs / "reports"
        output.mkdir()
        pattern(output / "contact.png")
        self.assertEqual(len(evaluate.discover([str(self.inputs)], output)), 1)
        odd = self.inputs / "unusual.data"
        shutil.copyfile(self.inputs / "image.png", odd)
        self.assertIn(odd, evaluate.discover([str(odd)], self.root / "other"))
        self.assertEqual(evaluate.analyze(odd, self.cfg)["format"], "PNG")

    def test_invalid_configuration(self):
        for config in [{"min_width": True}, {"near_duplicate_distance": 64},
                       {"aspect_ratio_range": [1, 0]}, {"unknown": 1},
                       {"desk_criteria": [" " ]}, {"max_file_mb": float("nan")}]:
            path = self.root / "config.json"
            path.write_text(json.dumps(config))
            with self.assertRaises(ValueError):
                evaluate.load_config(path)


if __name__ == "__main__":
    unittest.main()
