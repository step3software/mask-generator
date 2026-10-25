"""SYNTHETIC ONLY: arbitrary three-strip geometry, not a reconstruction of user references."""
import argparse
import copy
from pathlib import Path

import numpy as np
from PIL import Image

from cardboard import render_scene, write_json
from compare import evaluate_batch


def synthetic_scene():
    cameras = []
    for ident, eye in [("front", [0, -8, 3]), ("side", [8, 0, 3]),
                       ("oblique", [6, -7, 5]), ("high", [1, -2, 9])]:
        cameras.append({"id": ident, "eye": eye, "target": [0, 0, .5], "up": [0, 0, 1],
                        "projection": "orthographic", "vertical_span": 5,
                        "image_size": [256, 256]})
    return {"schema_version": 1, "synthetic": True, "units": "arbitrary_demo_units",
            "description": "SYNTHETIC TEST FIXTURE; no user reference geometry or camera is implied.",
            "segments": 32, "pieces": [
                {"length": 3, "width": .9, "thickness": .055, "bend_degrees": 125,
                 "rotation_degrees": [0, 0, 0], "translation": [0, -.6, 0]},
                {"length": 2.3, "width": .75, "thickness": .055, "bend_degrees": -85,
                 "rotation_degrees": [25, 0, 80], "translation": [.25, .45, .6]},
                {"length": 2.1, "width": .7, "thickness": .055, "bend_degrees": 95,
                 "rotation_degrees": [0, 65, -35], "translation": [-.65, .35, .9]},
            ], "cameras": cameras}


def build_demo(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    base = synthetic_scene()
    render_scene(base, output / "synthetic-reference-renders")
    views = []
    for camera in base["cameras"]:
        ident = camera["id"]
        ids_path = output / "synthetic-reference-renders" / f"{ident}.ids.png"
        with Image.open(ids_path) as image:
            labels = np.asarray(image)
        parts = {}
        for i in (1, 2, 3):
            name = f"synthetic-reference-renders/{ident}.piece-{i}.png"
            Image.fromarray((labels == i).astype(np.uint8) * 255).save(output / name)
            parts[str(i)] = name
        views.append({"id": ident, "camera": camera,
                      "mask": f"synthetic-reference-renders/{ident}.mask.png", "piece_masks": parts})
    references = {"schema_version": 1, "reference_state": "synthetic_self_consistency_test_only",
                  "description": "Not user references. Generated from the exact-match synthetic candidate.",
                  "views": views}
    write_json(output / "references.synthetic.json", references)
    candidates = output / "candidates"
    candidates.mkdir()
    write_json(candidates / "exact.synthetic.json", base)
    slight = copy.deepcopy(base)
    slight["pieces"][1]["bend_degrees"] = -60
    write_json(candidates / "perturbed.synthetic.json", slight)
    wrong = copy.deepcopy(base)
    wrong["pieces"][0]["translation"][0] += .8
    wrong["pieces"][2]["rotation_degrees"][1] -= 45
    write_json(candidates / "wrong.synthetic.json", wrong)
    write_json(output / "bounds.synthetic.json", {"pieces.1.bend_degrees": [-115, -50]})
    summary = evaluate_batch(sorted(candidates.glob("*.json")), output / "references.synthetic.json", output / "report", 3)
    (output / "SYNTHETIC_ONLY.txt").write_text(
        "All geometry, dimensions, masks, and cameras here are arbitrary test fixtures.\n"
        "The exact candidate generated the reference masks; IoU=1 verifies consistency only.\n"
        "These images do not claim to match the user's absent references.\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        build_demo(args.output)
        print((Path(args.output) / "report" / "summary.txt").read_text(), end="")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Cannot build synthetic demo: {error}\n")
