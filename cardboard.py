"""Exactly three developable, constant-curvature strips and deterministic CPU rendering."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def finite(value, label, length=None):
    array = np.asarray(value, dtype=float)
    if (length is not None and array.shape != (length,)) or not np.all(np.isfinite(array)):
        raise ValueError(f"Invalid finite value/vector: {label}")
    return array


def rotation(degrees):
    x, y, z = np.radians(finite(degrees, "rotation_degrees", 3))
    rx = np.array([[1, 0, 0], [0, np.cos(x), -np.sin(x)], [0, np.sin(x), np.cos(x)]])
    ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    rz = np.array([[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]])
    return rz @ ry @ rx


def validate_scene(scene):
    if not isinstance(scene, dict) or scene.get("schema_version") != 1:
        raise ValueError("Expected scene schema_version 1")
    pieces = scene.get("pieces")
    if not isinstance(pieces, list) or len(pieces) != 3:
        raise ValueError("Exactly three pieces are required")
    segments = scene.get("segments", 48)
    if type(segments) is not int or not 8 <= segments <= 256:
        raise ValueError("segments must be an integer from 8 to 256")
    for index, piece in enumerate(pieces):
        if not isinstance(piece, dict) or set(piece) - {"length", "width", "thickness", "bend_degrees", "rotation_degrees", "translation"}:
            raise ValueError("Piece fields must be the supported dimensions, bend, rotation, and translation")
        for key in ("length", "width", "thickness", "bend_degrees"):
            value = piece.get(key)
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"Piece {index + 1}: {key} must be a finite number")
        if min(piece["length"], piece["width"], piece["thickness"]) <= 0:
            raise ValueError("All piece dimensions must be positive")
        if not 1 <= abs(piece["bend_degrees"]) <= 330:
            raise ValueError("Absolute bend must be between 1 and 330 degrees")
        radius = piece["length"] / abs(math.radians(piece["bend_degrees"]))
        if piece["thickness"] >= 2 * radius:
            raise ValueError("Thickness must be less than twice the bend radius")
        finite(piece.get("rotation_degrees"), "rotation_degrees", 3)
        finite(piece.get("translation"), "translation", 3)
    cameras = scene.get("cameras")
    if not isinstance(cameras, list) or not cameras:
        raise ValueError("At least one explicit camera is required")
    ids = []
    for camera in cameras:
        if not isinstance(camera, dict) or set(camera) - {"id", "eye", "target", "up", "projection", "image_size", "vertical_span", "fov_y_degrees"}:
            raise ValueError("Camera contains unsupported fields")
        ident = camera.get("id")
        if not isinstance(ident, str) or not ident or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in ident):
            raise ValueError("Camera IDs must use letters, digits, underscore, or hyphen")
        ids.append(ident)
        size = camera.get("image_size")
        if not isinstance(size, list) or len(size) != 2 or any(type(v) is not int or not 32 <= v <= 2048 for v in size):
            raise ValueError("image_size must be [width, height], each from 32 to 2048")
        eye, target, up = (finite(camera.get(k), k, 3) for k in ("eye", "target", "up"))
        forward = target - eye
        if np.linalg.norm(forward) < 1e-9 or np.linalg.norm(np.cross(forward, up)) < 1e-9:
            raise ValueError("Camera eye/target/up do not define a valid frame")
        mode = camera.get("projection")
        if mode not in ("orthographic", "perspective"):
            raise ValueError("projection must be orthographic or perspective")
        key = "vertical_span" if mode == "orthographic" else "fov_y_degrees"
        value = camera.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"Camera needs a positive {key}")
        if mode == "perspective" and not 1 <= value <= 170:
            raise ValueError("Perspective fov_y_degrees must be between 1 and 170")
    if len(set(ids)) != len(ids):
        raise ValueError("Camera IDs must be unique")
    return scene


def piece_mesh(piece, segments):
    """Arc length lies along XZ; width along Y; thickness along the arc normal."""
    angle = math.radians(piece["bend_degrees"])
    radius = piece["length"] / abs(angle)
    sign = 1 if angle > 0 else -1
    theta = np.linspace(-abs(angle) / 2, abs(angle) / 2, segments + 1)
    vertices = []
    for t in theta:
        for side in (-1, 1):
            r = radius + side * piece["thickness"] / 2
            for width_side in (-1, 1):
                vertices.append([r * np.sin(t), width_side * piece["width"] / 2,
                                 sign * (radius - r * np.cos(t))])
    faces = []
    def quad(a, b, c, d):
        faces.extend([(a, b, c), (a, c, d)])
    for i in range(segments):
        a, b = 4 * i, 4 * (i + 1)
        quad(a, b, b + 1, a + 1)
        quad(a + 2, a + 3, b + 3, b + 2)
        quad(a, a + 2, b + 2, b)
        quad(a + 1, b + 1, b + 3, a + 3)
    quad(0, 1, 3, 2)
    a = 4 * segments
    quad(a, a + 2, a + 3, a + 1)
    vertices = np.asarray(vertices) @ rotation(piece["rotation_degrees"]).T
    vertices += finite(piece["translation"], "translation", 3)
    if not np.all(np.isfinite(vertices)):
        raise ValueError("Geometry overflow; use a consistent, smaller coordinate scale")
    return vertices, np.asarray(faces, dtype=int)


def camera_frame(camera):
    eye = finite(camera["eye"], "eye", 3)
    forward = finite(camera["target"], "target", 3) - eye
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, finite(camera["up"], "up", 3))
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    return eye, np.stack([right, up, forward], axis=1)


def render(scene, camera):
    width, height = camera["image_size"]
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    labels = np.zeros((height, width), dtype=np.uint8)
    depth_buffer = np.full((height, width), np.inf)
    eye, frame = camera_frame(camera)
    light = np.array([0.3, -0.4, 0.85])
    light /= np.linalg.norm(light)
    near = 1e-6
    perspective = camera["projection"] == "perspective"
    scale = (height / (2 * np.tan(np.radians(camera["fov_y_degrees"]) / 2))
             if perspective else height / camera["vertical_span"])
    clipped_vertices = 0
    for piece_id, piece in enumerate(scene["pieces"], 1):
        world, faces = piece_mesh(piece, scene.get("segments", 48))
        coordinates = (world - eye) @ frame
        z = coordinates[:, 2]
        if np.any(z <= near):
            raise ValueError(f"Geometry reaches/straddles camera near plane in {camera['id']}; move camera")
        xy = coordinates[:, :2] * scale
        if perspective:
            xy /= z[:, None]
        if not np.all(np.isfinite(xy)):
            raise ValueError("Projection overflow; check camera and geometry scale")
        xy[:, 0] += width / 2
        xy[:, 1] = height / 2 - xy[:, 1]
        clipped_vertices += int(np.count_nonzero((xy[:, 0] < 0) | (xy[:, 0] > width)
                                                | (xy[:, 1] < 0) | (xy[:, 1] > height)))
        for face in faces:
            triangle = xy[face]
            x0 = max(0, int(np.floor(triangle[:, 0].min())))
            x1 = min(width - 1, int(np.ceil(triangle[:, 0].max())))
            y0 = max(0, int(np.floor(triangle[:, 1].min())))
            y1 = min(height - 1, int(np.ceil(triangle[:, 1].max())))
            if x0 > x1 or y0 > y1:
                continue
            a, b, c = triangle
            denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(denominator) < 1e-10:
                continue
            yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
            xx, yy = xx + .5, yy + .5
            u = ((b[1] - c[1]) * (xx - c[0]) + (c[0] - b[0]) * (yy - c[1])) / denominator
            v = ((c[1] - a[1]) * (xx - c[0]) + (a[0] - c[0]) * (yy - c[1])) / denominator
            w = 1 - u - v
            inside = (u >= -1e-9) & (v >= -1e-9) & (w >= -1e-9)
            zs = z[face]
            if perspective:
                local_depth = 1 / np.maximum(u / zs[0] + v / zs[1] + w / zs[2], 1e-20)
            else:
                local_depth = u * zs[0] + v * zs[1] + w * zs[2]
            current = depth_buffer[y0:y1 + 1, x0:x1 + 1]
            update = inside & (local_depth < current)
            normal = np.cross(world[face[1]] - world[face[0]], world[face[2]] - world[face[0]])
            norm = np.linalg.norm(normal)
            intensity = .55 + .45 * abs(np.dot(normal / max(norm, 1e-20), light))
            color = np.rint(np.array([181, 139, 86]) * intensity).astype(np.uint8)
            rgba[y0:y1 + 1, x0:x1 + 1][update] = [*color, 255]
            labels[y0:y1 + 1, x0:x1 + 1][update] = piece_id
            current[update] = local_depth[update]
    diagnostics = {"out_of_frame_vertices": clipped_vertices,
                   "visible_piece_pixels": {str(i): int(np.sum(labels == i)) for i in (1, 2, 3)}}
    return rgba, labels, diagnostics


def scene_hash(scene):
    return hashlib.sha256(json.dumps(scene, sort_keys=True, allow_nan=False).encode()).hexdigest()


def render_scene(scene, output):
    validate_scene(scene)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    views = []
    for camera in scene["cameras"]:
        rgba, labels, diagnostic = render(scene, camera)
        ident = camera["id"]
        Image.fromarray(rgba).save(output / f"{ident}.png")
        Image.fromarray((labels > 0).astype(np.uint8) * 255).save(output / f"{ident}.mask.png")
        Image.fromarray(labels).save(output / f"{ident}.ids.png")
        views.append({"id": ident, "camera": camera, **diagnostic})
    write_json(output / "scene.used.json", scene)
    write_json(output / "render_manifest.json", {
        "schema_version": 1, "geometry_sha256": scene_hash(scene), "piece_count": 3,
        "synthetic": scene.get("synthetic", False), "views": views,
        "limitations": "Constant-curvature strips only. No manufacturing/collision validation. No antialiasing."})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        render_scene(read_json(args.scene), args.output)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"Cannot render scene: {error}\n")
