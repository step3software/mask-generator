"""Compare the same three-piece geometry against every declared reference view."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from cardboard import read_json, render, scene_hash, validate_scene, write_json


def load_mask(path):
    with Image.open(path) as image:
        if image.width * image.height > 4_194_304:
            raise ValueError(f"Mask exceeds 2048x2048 pixel budget: {path}")
        if image.mode not in ("1", "L"):
            raise ValueError(f"Mask must be binary grayscale, not a photograph: {path}")
        pixels = np.asarray(image.convert("L"))
    if not set(np.unique(pixels)).issubset({0, 1, 255}):
        raise ValueError(f"Mask values must be 0/1/255: {path}")
    return pixels > 0


def mask_hash(mask):
    return hashlib.sha256(str(mask.shape).encode() + mask.tobytes()).hexdigest()


def erode(mask):
    padded = np.pad(mask, 1)
    result = np.ones_like(mask)
    for dy in range(3):
        for dx in range(3):
            result &= padded[dy:dy + mask.shape[0], dx:dx + mask.shape[1]]
    return result


def boundary(mask):
    return mask & ~erode(mask)


def distances(a, b, point_cap=1024):
    """Bounded deterministic contour sampling; distances in pixels, not physical units."""
    if len(a) > point_cap:
        a = a[np.linspace(0, len(a) - 1, point_cap, dtype=int)]
    if len(b) > point_cap:
        b = b[np.linspace(0, len(b) - 1, point_cap, dtype=int)]
    if len(a) == 0 or len(b) == 0:
        return None, None
    ab = []
    ba = np.full(len(b), np.inf)
    for start in range(0, len(a), 128):
        delta = a[start:start + 128, None, :].astype(float) - b[None, :, :]
        squared = np.sum(delta * delta, axis=2)
        ab.extend(np.sqrt(squared.min(axis=1)))
        ba = np.minimum(ba, squared.min(axis=0))
    return np.asarray(ab), np.sqrt(ba)


def silhouette_metrics(candidate, reference, valid=None, tolerance_px=2, point_cap=1024, allow_empty=False):
    if candidate.shape != reference.shape:
        raise ValueError("Candidate/reference dimensions differ; no automatic alignment or resizing")
    valid = np.ones_like(reference) if valid is None else valid
    if valid.shape != reference.shape or not valid.any():
        raise ValueError("Ignore mask dimensions differ, or no comparable pixels remain")
    a, b = candidate & valid, reference & valid
    if not b.any() and not allow_empty:
        raise ValueError("Reference has no foreground in the comparable region")
    intersection = int(np.count_nonzero(a & b))
    union = int(np.count_nonzero(a | b))
    area_a, area_b = int(a.sum()), int(b.sum())
    # Compute contours before masking so ignored pixels do not create artificial shape edges.
    contour_a, contour_b = boundary(candidate) & valid, boundary(reference) & valid
    coords_a, coords_b = np.argwhere(contour_a), np.argwhere(contour_b)
    ab, ba = distances(coords_a, coords_b, point_cap)
    if ab is None:
        chamfer = p95 = None
    else:
        diagonal = float(np.hypot(*candidate.shape))
        chamfer = float((ab.mean() + ba.mean()) / (2 * diagonal))
        p95 = float(max(np.percentile(ab, 95), np.percentile(ba, 95)) / diagonal)
    # Exact tolerance matching over full raster contours; unlike distances, not sampled.
    radius = int(np.ceil(tolerance_px))
    dilated_a, dilated_b = np.zeros_like(a), np.zeros_like(b)
    padded_a, padded_b = np.pad(contour_a, radius), np.pad(contour_b, radius)
    height, width = a.shape
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy <= tolerance_px * tolerance_px:
                y, x = radius + dy, radius + dx
                dilated_a |= padded_a[y:y + height, x:x + width]
                dilated_b |= padded_b[y:y + height, x:x + width]
    precision = float(np.count_nonzero(contour_a & dilated_b) / max(1, len(coords_a)))
    recall = float(np.count_nonzero(contour_b & dilated_a) / max(1, len(coords_b)))
    return {
        "iou": intersection / union if union else 1.0,
        "dice": 2 * intersection / (area_a + area_b) if area_a + area_b else 1.0,
        "foreground_area_ratio": area_a / area_b if area_b else None,
        "boundary_f1": (2 * precision * recall / (precision + recall) if precision + recall
                        else (1.0 if len(coords_a) == len(coords_b) == 0 else 0.0)),
        "boundary_tolerance_px": tolerance_px,
        "sampled_symmetric_contour_distance_diagonal": chamfer,
        "sampled_contour_p95_diagonal": p95,
        "contour_point_cap_per_side": point_cap,
        "contour_points_before_sampling": [len(coords_a), len(coords_b)],
        "compared_pixel_fraction": float(valid.mean()),
    }


def load_references(path):
    path = Path(path).resolve()
    manifest = read_json(path)
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("Expected reference schema_version 1")
    views = manifest.get("views")
    if not isinstance(views, list) or not views:
        raise ValueError("Supply at least one real reference view, foreground mask, and explicit camera")
    loaded = []
    for view in views:
        camera = view["camera"]
        if view["id"] != camera["id"]:
            raise ValueError("View ID must match its camera ID")
        mask_path = (path.parent / view["mask"]).resolve()
        mask = load_mask(mask_path)
        if mask.shape != tuple(reversed(camera["image_size"])):
            raise ValueError("Reference mask size must match the explicit camera image_size")
        if not mask.any():
            raise ValueError("Reference silhouette must contain foreground")
        valid = np.ones_like(mask)
        if view.get("ignore_mask"):
            ignore = load_mask(path.parent / view["ignore_mask"])
            if ignore.shape != mask.shape:
                raise ValueError("Ignore mask must match reference dimensions")
            valid = ~ignore
        parts = {}
        for ident, name in view.get("piece_masks", {}).items():
            if ident not in ("1", "2", "3"):
                raise ValueError("piece_masks keys must be 1, 2, or 3, matching candidate piece order")
            part = load_mask(path.parent / name)
            if part.shape != mask.shape or np.any(part & ~mask):
                raise ValueError("Piece masks must match dimensions and be inside the reference silhouette")
            if any(np.any(part & existing) for existing in parts.values()):
                raise ValueError("Visible piece masks must not overlap")
            parts[ident] = part
        if not np.any(mask & valid):
            raise ValueError("No reference foreground remains after ignoring pixels")
        loaded.append({"id": view["id"], "camera": camera, "mask": mask,
                       "valid": valid, "parts": parts,
                       "mask_sha256": mask_hash(mask), "valid_sha256": mask_hash(valid),
                       "part_mask_sha256": {i: mask_hash(m) for i, m in parts.items()}})
    ids = [v["id"] for v in loaded]
    if len(ids) != len(set(ids)):
        raise ValueError("Reference view IDs must be unique")
    return manifest, loaded


def compare_scene(scene, references, tolerance_px=2, point_cap=1024):
    validate_scene(scene)
    expected = {r["id"]: r["camera"] for r in references}
    actual = {c["id"]: c for c in scene["cameras"]}
    if actual != expected:
        raise ValueError("All candidates must use exactly the reference camera rig; independent camera fitting is disabled")
    views, previews = [], []
    for reference in references:
        rgba, labels, diagnostics = render(scene, reference["camera"])
        mask = labels > 0
        scores = silhouette_metrics(mask, reference["mask"], reference["valid"], tolerance_px, point_cap)
        parts = {ident: silhouette_metrics(labels == int(ident), part, reference["valid"], tolerance_px, point_cap, allow_empty=True)
                 for ident, part in reference["parts"].items()}
        views.append({"id": reference["id"], **scores, "piece_scores": parts, **diagnostics})
        previews.append((reference, rgba, mask))
    result = {
        "scene_sha256": scene_hash(scene), "piece_count": 3, "views_evaluated": len(views),
        "worst_view_iou": min(v["iou"] for v in views),
        "mean_view_iou": float(np.mean([v["iou"] for v in views])),
        "worst_view_id": min(views, key=lambda v: (v["iou"], v["id"]))["id"],
        "views": views, "acceptance_status": "not_determined_no_user_thresholds",
    }
    return result, previews


def save_overlay(previews, path):
    """Reference-only red, candidate-only cyan, overlap neutral; no photographic claim."""
    tile_width, tile_height = 256, 286
    columns = min(4, len(previews))
    sheet = Image.new("RGB", (columns * tile_width, ((len(previews) + columns - 1) // columns) * tile_height), "white")
    draw = ImageDraw.Draw(sheet)
    for i, (reference, _, candidate) in enumerate(previews):
        target = reference["mask"]
        overlay = np.full((*target.shape, 3), 245, dtype=np.uint8)
        overlay[target & candidate] = [110, 110, 110]
        overlay[target & ~candidate] = [225, 70, 65]
        overlay[candidate & ~target] = [40, 180, 205]
        overlay[~reference["valid"]] = [255, 215, 130]
        image = Image.fromarray(overlay)
        image.thumbnail((256, 256))
        x, y = i % columns * tile_width, i // columns * tile_height
        sheet.paste(image, (x + (256 - image.width) // 2, y))
        draw.text((x + 5, y + 260), reference["id"], fill="black")
    sheet.save(path)


def evaluate_batch(candidates, reference_path, output, review_limit=4, tolerance_px=2, point_cap=1024):
    if not 0 <= review_limit <= 12 or not 0 <= tolerance_px <= 10 or not 32 <= point_cap <= 4096:
        raise ValueError("review_limit must be 0..12, tolerance 0..10, and point_cap 32..4096")
    manifest, references = load_references(reference_path)
    paths = sorted({Path(p).resolve() for p in candidates}, key=str)
    if not paths:
        raise ValueError("No candidate scene files supplied")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for path in paths:
        try:
            scene = read_json(path)
            result, _ = compare_scene(scene, references, tolerance_px, point_cap)
            result.update(candidate=str(path), status="evaluated")
        except (OSError, ValueError, KeyError, TypeError) as error:
            result = {"candidate": str(path), "status": "error", "error": str(error)[:400]}
        results.append(result)
    ranked = sorted((r for r in results if r["status"] == "evaluated"),
                    key=lambda r: (-r["worst_view_iou"], -r["mean_view_iou"], r["candidate"]))
    for rank, row in enumerate(ranked, 1):
        row["rank"] = rank
    with (output / "metrics.jsonl").open("w", encoding="utf-8") as stream:
        for row in results:
            stream.write(json.dumps(row, allow_nan=False) + "\n")
    with (output / "ranking.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        fields = ["rank", "candidate", "worst_view_iou", "mean_view_iou", "worst_view_id", "acceptance_status"]
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(ranked)
    queue = []
    # Top candidates, bounded by count; include all supplied reference views in each overlay.
    for number, result in enumerate(ranked[:review_limit], 1):
        scene = read_json(result["candidate"])
        if scene_hash(scene) != result["scene_sha256"]:
            raise ValueError("Candidate scene changed during batch; rerun")
        _, previews = compare_scene(scene, references, tolerance_px, point_cap)
        view_scores = {v["id"]: v["iou"] for v in result["views"]}
        previews = sorted(previews, key=lambda p: (view_scores[p[0]["id"]], p[0]["id"]))[:8]
        name = f"review-{number:02d}.png"
        save_overlay(previews, output / name)
        queue.append({"rank": result["rank"], "overlay": name, "candidate": result["candidate"],
                      "worst_view_iou": result["worst_view_iou"], "worst_view_id": result["worst_view_id"],
                      "selected_view_ids": [p[0]["id"] for p in previews],
                      "omitted_view_count": len(references) - len(previews)})
    provenance = [{"id": r["id"], "camera": r["camera"], "mask_sha256": r["mask_sha256"],
                   "valid_sha256": r["valid_sha256"], "part_mask_sha256": r["part_mask_sha256"]} for r in references]
    write_json(output / "references.used.json", {"reference_manifest_path": str(Path(reference_path).resolve()),
               "manifest": manifest, "loaded_provenance": provenance})
    write_json(output / "review_queue.json", {"items": queue,
        "instructions": "Red = reference only; cyan = candidate only; gray = overlap; yellow = ignored. "
        "Review geometric discrepancies and uncertainty only; scores are not acceptance. "
        "Request original reference images for appearance/physical construction judgments."})
    summary = {
        "pipeline_version": "three-piece-1.0.0",
        "candidate_count": len(results), "evaluated_count": len(ranked),
        "error_count": len(results) - len(ranked), "reference_views": len(references),
        "reference_state": manifest.get("reference_state", "user_supplied_not_independently_verified"),
        "ranking_rule": "descending worst-view IoU, then mean-view IoU; no acceptance threshold",
        "best": ({k: ranked[0][k] for k in ("candidate", "worst_view_iou", "mean_view_iou", "worst_view_id")}
                 if ranked else None),
        "review_selected": len(queue), "model_calls": 0,
        "error_examples": [{"candidate": r["candidate"], "error": r["error"]}
                           for r in results if r["status"] == "error"][:5],
        "settings": {"boundary_tolerance_px": tolerance_px, "contour_point_cap": point_cap},
        "limitations": ["Agreement is limited to supplied views and masks, with cameras fixed as supplied.",
            "Silhouettes do not uniquely determine hidden geometry or prove piece count in photographs.",
            "Three pieces are enforced in the parameterization, not inferred from input images.",
            "Constant-curvature strips may not span the target shape; no collision/manufacturing proof.",
            "Contour distances are sampled; threshold acceptance remains unset."]}
    write_json(output / "summary.json", summary)
    best = summary["best"]
    text = (f"Candidates: {len(results)} | evaluated: {len(ranked)} | errors: {summary['error_count']}\n"
            f"Required views per candidate: {len(references)} | model calls: 0\n"
            f"Reference state: {summary['reference_state']}\n")
    if best:
        text += (f"Best worst-view IoU: {best['worst_view_iou']:.6f} | mean IoU: {best['mean_view_iou']:.6f} "
                 f"| weakest view: {best['worst_view_id']}\n")
    text += f"Review overlays: {len(queue)} | acceptance: not determined\n"
    (output / "summary.txt").write_text(text, encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates", nargs="+", help="Scene JSON files; use --candidate-dir for folders")
    parser.add_argument("--candidate-dir", action="store_true", help="Expand supplied directories to *.json")
    parser.add_argument("--references", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--review-limit", type=int, default=4)
    parser.add_argument("--boundary-tolerance-px", type=float, default=2)
    args = parser.parse_args(argv)
    candidates = [p for value in args.candidates for p in
                  (sorted(Path(value).glob("*.json")) if args.candidate_dir else [Path(value)])]
    try:
        summary = evaluate_batch(candidates, args.references, args.output, args.review_limit, args.boundary_tolerance_px)
        print((Path(args.output) / "summary.txt").read_text(), end="")
        return 1 if summary["error_count"] else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Cannot compare batch: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
