"""Seeded geometry-only random search within user-supplied bounds; fixed camera rig."""
import argparse
import copy
import math
from pathlib import Path
import random

from cardboard import read_json, validate_scene, write_json
from compare import evaluate_batch


def parameter_target(scene, key):
    parts = key.split(".")
    if len(parts) not in (3, 4) or parts[0] != "pieces" or parts[1] not in ("0", "1", "2"):
        raise ValueError(f"Bounds may only edit pieces.0/1/2 fields: {key}")
    field = parts[2]
    piece = scene["pieces"][int(parts[1])]
    if len(parts) == 3 and field in ("length", "width", "thickness", "bend_degrees"):
        return piece, field
    if len(parts) == 4 and field in ("translation", "rotation_degrees") and parts[3] in ("0", "1", "2"):
        return piece[field], int(parts[3])
    raise ValueError(f"Unsupported parameter path: {key}")


def make_candidates(base, bounds, count, seed):
    validate_scene(base)
    if not isinstance(bounds, dict) or not bounds:
        raise ValueError("Supply nonempty explicit parameter bounds; no target dimensions are assumed")
    if type(count) is not int or not 1 <= count <= 10000:
        raise ValueError("Candidate count must be between 1 and 10000")
    for key, interval in bounds.items():
        parameter_target(base, key)
        if not isinstance(interval, list) or len(interval) != 2 or any(
            type(v) not in (int, float) or not math.isfinite(v) for v in interval
        ) or interval[0] > interval[1]:
            raise ValueError(f"Invalid [lower, upper] bounds: {key}")
    rng = random.Random(seed)
    generated = [copy.deepcopy(base)]
    attempts = 0
    while len(generated) < count + 1:
        attempts += 1
        if attempts > count * 50:
            raise ValueError("Too few valid geometries within supplied bounds; revise bounds")
        scene = copy.deepcopy(base)
        for key in sorted(bounds):
            owner, field = parameter_target(scene, key)
            owner[field] = rng.uniform(*bounds[key])
        try:
            validate_scene(scene)
        except ValueError:
            continue
        generated.append(scene)
    return generated


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_scene")
    parser.add_argument("--bounds", required=True)
    parser.add_argument("--references", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--count", type=int, default=20, help="Random candidates in addition to base")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--review-limit", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        base, bounds = read_json(args.base_scene), read_json(args.bounds)
        scenes = make_candidates(base, bounds, args.count, args.seed)
        output = Path(args.output)
        output.mkdir(parents=True, exist_ok=False)
        folder = output / "candidates"
        folder.mkdir()
        paths = []
        for number, scene in enumerate(scenes):
            path = folder / f"candidate-{number:05d}.json"
            write_json(path, scene)
            paths.append(path)
        write_json(output / "search.used.json", {"seed": args.seed, "random_candidate_count": args.count,
                   "base_included": True, "bounds": bounds,
                   "method": "uniform random sampling; geometry only; cameras unchanged"})
        summary = evaluate_batch(paths, args.references, output / "report", args.review_limit)
        print((output / "report" / "summary.txt").read_text(), end="")
        return 1 if summary["error_count"] else 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, f"Cannot search geometry: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
