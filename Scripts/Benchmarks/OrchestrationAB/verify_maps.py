"""Independently check benchmark PNG maps at covered UV sample positions."""

import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys
import zlib


ROOT = Path(__file__).resolve().parents[3]
TOLERANCE = 2.0
SETS = {"Body": ([0.10, 0.28, 0.40], [1.0, 0.55, 0.0]),
        "Metal": ([0.35, 0.37, 0.40], [1.0, 0.30, 1.0])}
KINDS = ("BaseColor", "Normal", "ORM")


def png_chunks(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Invalid PNG signature")
    offset = 8
    chunks = []
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("Truncated PNG chunk")
        size, kind = struct.unpack_from(">I4s", data, offset)
        end = offset + size + 12
        if end > len(data):
            raise ValueError("Truncated PNG chunk payload")
        payload = data[offset + 8:end - 4]
        crc = struct.unpack_from(">I", data, end - 4)[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError("PNG chunk CRC mismatch: " + repr(kind))
        chunks.append((kind, payload))
        offset = end
        if kind == b"IEND":
            if payload or offset != len(data):
                raise ValueError("Invalid IEND or trailing PNG bytes")
            break
    if not chunks or chunks[0][0] != b"IHDR" or chunks[-1][0] != b"IEND":
        raise ValueError("PNG must begin with IHDR and end with IEND")
    if sum(kind == b"IHDR" for kind, _ in chunks) != 1:
        raise ValueError("Duplicate IHDR")
    return chunks


def decode_png(data):
    """Decode 8-bit PNG, including Adam7, using only the standard library."""
    chunks = png_chunks(data)
    values = struct.unpack(">IIBBBBB", chunks[0][1])
    info = dict(zip(("width", "height", "bit_depth", "color_type",
                     "compression", "filter", "interlace"), values))
    width, height, depth, color, compression, filtering, interlace = values
    if not (0 < width <= 4096 and 0 < height <= 4096):
        raise ValueError("PNG dimensions outside decoder safety limit (1..4096)")
    if depth != 8 or color not in (0, 2, 3, 4, 6):
        raise ValueError("PNG must have 8-bit grayscale, RGB, palette, GA or RGBA data")
    if compression != 0 or filtering != 0 or interlace not in (0, 1):
        raise ValueError("Unsupported PNG compression/filter/interlace method")
    for kind, _ in chunks:
        if not kind[0] & 32 and kind not in (b"IHDR", b"PLTE", b"IDAT", b"IEND"):
            raise ValueError("Unknown critical PNG chunk: " + repr(kind))
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    palette = next((p for k, p in chunks if k == b"PLTE"), b"")
    transparency = next((p for k, p in chunks if k == b"tRNS"), b"")
    if color == 3 and (not palette or len(palette) % 3 or len(palette) > 768):
        raise ValueError("Missing or invalid indexed PNG palette")
    if transparency and ((color == 0 and len(transparency) != 2) or
                         (color == 2 and len(transparency) != 6) or
                         (color == 3 and len(transparency) > len(palette) // 3) or
                         color in (4, 6)):
        raise ValueError("Invalid PNG transparency chunk")
    transparent_key = (struct.unpack(">H", transparency) if color == 0 else
                       struct.unpack(">HHH", transparency)) if transparency and color in (0, 2) else None
    passes = [(0, 0, 1, 1)] if not interlace else [
        (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
        (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)]
    layout = [(x, y, dx, dy, max(0, (width - x + dx - 1) // dx),
               max(0, (height - y + dy - 1) // dy)) for x, y, dx, dy in passes]
    expected = sum(ph * (pw * channels + 1) for _, _, _, _, pw, ph in layout if pw)
    decompressor = zlib.decompressobj()
    raw = decompressor.decompress(b"".join(p for k, p in chunks if k == b"IDAT"), expected + 1)
    if len(raw) != expected or not decompressor.eof or decompressor.unused_data:
        raise ValueError("PNG decompressed length or zlib stream is invalid")
    rgba, cursor = bytearray(width * height * 4), 0
    for x0, y0, dx, dy, pw, ph in layout:
        if not pw or not ph:
            continue
        previous = bytearray(pw * channels)
        for py in range(ph):
            method = raw[cursor]
            row = bytearray(raw[cursor + 1:cursor + 1 + pw * channels])
            cursor += 1 + pw * channels
            if method > 4:
                raise ValueError("Invalid PNG row filter")
            if method:
                for i in range(len(row)):
                    left = row[i - channels] if i >= channels else 0
                    above = previous[i]
                    corner = previous[i - channels] if i >= channels else 0
                    if method == 1:
                        predictor = left
                    elif method == 2:
                        predictor = above
                    elif method == 3:
                        predictor = (left + above) // 2
                    else:
                        p = left + above - corner
                        distances = (abs(p - left), abs(p - above), abs(p - corner))
                        predictor = (left, above, corner)[distances.index(min(distances))]
                    row[i] = (row[i] + predictor) & 255
            for px in range(pw):
                sample = tuple(row[px * channels:(px + 1) * channels])
                alpha = 0 if transparent_key == sample else 255
                if color == 0:
                    pixel = (*sample * 3, alpha)
                elif color == 2:
                    pixel = (*sample, alpha)
                elif color == 3:
                    index = sample[0]
                    if index * 3 + 3 > len(palette):
                        raise ValueError("PNG palette index outside PLTE")
                    pixel = (*palette[index * 3:index * 3 + 3],
                             transparency[index] if index < len(transparency) else 255)
                elif color == 4:
                    pixel = (sample[0], sample[0], sample[0], sample[1])
                else:
                    pixel = sample
                start = ((y0 + py * dy) * width + x0 + px * dx) * 4
                rgba[start:start + 4] = bytes(pixel)
            previous = row
    return info, rgba


def sample_positions(triangles, width, height):
    """Use centroid-nearest pixel centers with a conservative barycentric margin."""
    pixels = {}
    considered = sorted(triangles, key=lambda t: t["area"], reverse=True)[:32]
    for triangle in considered:
        points = [(u * width, (1 - v) * height) for u, v in triangle["uv"]]
        a, b, c = points
        denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(denominator) < 1e-12:
            continue
        cx, cy = triangle["centroid"][0] * width, (1 - triangle["centroid"][1]) * height
        candidates = [(math.floor(cx) + ox, math.floor(cy) + oy)
                      for ox in range(-2, 3) for oy in range(-2, 3)]
        candidates.sort(key=lambda p: (p[0] + 0.5 - cx) ** 2 + (p[1] + 0.5 - cy) ** 2)
        accepted = 0
        for x, y in candidates:
            if not (0 <= x < width and 0 <= y < height):
                continue
            px, py = x + 0.5, y + 0.5
            wa = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) / denominator
            wb = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / denominator
            if min(wa, wb, 1 - wa - wb) < 0.05:
                continue
            # Reject pixel centers less than one pixel from any UV triangle edge.
            distances = [abs((q[0] - p[0]) * (py - p[1]) - (q[1] - p[1]) * (px - p[0])) /
                         math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in ((a, b), (b, c), (c, a))]
            if min(distances) < 1.0:
                continue
            pixels.setdefault((x, y), triangle["polygon_index"])
            accepted += 1
            if accepted == 5:
                break
    return [{"x": x, "y": y, "polygon_index": polygon} for (x, y), polygon in pixels.items()]


def read_uv(path, run_id):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("run_id") != run_id or not data.get("uv_layer"):
        raise ValueError("UV data run_id mismatch or missing uv_layer")
    groups = {name: [] for name in SETS}
    for triangle in data["triangles"]:
        name = triangle["material_name"]
        matches = [key for key in SETS if name in (f"M_{run_id}_{key}", f"{run_id}_{key}")]
        uv, centroid, area = triangle["uv"], triangle["centroid"], triangle["area"]
        if len(matches) != 1 or len(uv) != 3 or any(len(p) != 2 for p in uv) or len(centroid) != 2:
            raise ValueError("UV data contains an invalid material or triangle")
        if not math.isfinite(area) or area <= 0 or any(not math.isfinite(v) or not -1e-6 <= v <= 1 + 1e-6 for p in uv for v in p):
            raise ValueError("UV data contains nonfinite/out-of-range coordinates or invalid area")
        computed = [sum(p[i] for p in uv) / 3 for i in range(2)]
        if any(not math.isfinite(centroid[i]) or abs(centroid[i] - computed[i]) > 1e-7 for i in range(2)):
            raise ValueError("UV centroid does not match triangle coordinates")
        groups[matches[0]].append(triangle)
    if any(not triangles for triangles in groups.values()):
        raise ValueError("UV data must contain triangles for both material sets")
    return groups


def check_map(path, material, kind, triangles):
    result = {"path": path.relative_to(ROOT).as_posix(), "material": material,
              "kind": kind, "errors": []}
    try:
        result["file_bytes"] = path.stat().st_size
        if result["file_bytes"] > 32 * 1024 * 1024:
            raise ValueError("PNG exceeds 32 MiB safety limit")
        data = path.read_bytes()
        result["sha256"] = hashlib.sha256(data).hexdigest()
        chunks = png_chunks(data)
        values = struct.unpack(">IIBBBBB", chunks[0][1])
        result["ihdr"] = dict(zip(("width", "height", "bit_depth", "color_type", "compression", "filter", "interlace"), values))
        if values[:3] != (1024, 1024, 8):
            raise ValueError("Required PNG dimensions/depth are 1024x1024, 8-bit")
        info, pixels = decode_png(data)
        positions = sample_positions(triangles, info["width"], info["height"])
        eligible, excluded = [], 0
        for position in positions:
            start = (position["y"] * info["width"] + position["x"]) * 4
            pixel = pixels[start:start + 4]
            if pixel[3] != 255:
                excluded += 1
                continue
            eligible.append(pixel[:3])
        result.update(candidate_sample_count=len(positions), sample_count=len(eligible),
                      alpha_excluded_count=excluded, sample_positions=positions)
        if not eligible:
            raise ValueError("No opaque, safely covered UV sample pixels")
        base, orm = SETS[material]
        expected = {"BaseColor": base, "Normal": [0.5, 0.5, 1.0], "ORM": orm}[kind]
        result["channels"] = {}
        for channel, target in enumerate(expected):
            actual = [sample[channel] for sample in eligible]
            error = max(abs(value - target * 255) for value in actual)
            label = "RGB"[channel]
            result["channels"][label] = {"expected_8bit": target * 255, "min": min(actual),
                                         "max": max(actual), "max_absolute_error_8bit": error}
            if error > TOLERANCE + 1e-9:
                result["errors"].append(f"{label} differs from expected by {error:.4f}/255 (limit 2/255)")
    except (OSError, ValueError, KeyError, TypeError, IndexError, struct.error, zlib.error) as exc:
        result["errors"].append(f"{type(exc).__name__}: {exc}")
    result["passed"] = not result["errors"]
    return result


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("BenchA", "BenchB"):
        print("Usage: python verify_maps.py BenchA|BenchB", file=sys.stderr)
        return 1
    run_id = sys.argv[1]
    directory = ROOT / "Assets/Textures/SmokeTest/Painter/OrchestrationAB" / run_id
    output = ROOT / "Saved/AgentSetup/OrchestrationAB/Independent" / run_id
    uv_path = output / "uv-data.json"
    report = {"run_id": run_id, "texture_directory": directory.relative_to(ROOT).as_posix(),
              "uv_data": uv_path.relative_to(ROOT).as_posix(), "errors": [], "maps": [],
              "sampling": {"largest_triangles_per_material": 32, "pixels_per_triangle": 5,
                           "barycentric_min": 0.05, "edge_margin_pixels": 1, "required_alpha": 255,
                           "tolerance_8bit": TOLERANCE, "scope": "Selected UV interiors, not exhaustive texels"}}
    paths = sorted(p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() == ".png")
    report["png_file_count"] = len(paths)
    if len(paths) != 6:
        report["errors"].append(f"Expected exactly six PNG files; found {len(paths)}")
    groups = None
    try:
        groups = read_uv(uv_path, run_id)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        report["errors"].append(f"UV data: {type(exc).__name__}: {exc}")
    identified = {}
    for path in paths:
        matches = re.findall(rf"(?<![A-Za-z0-9])(?:M_)?{run_id}_(Body|Metal)(?![A-Za-z0-9])", path.stem)
        suffix = re.search(r"(?:^|[_ .-])(BaseColor|Normal|OcclusionRoughnessMetallic|ORM)$", path.stem)
        if len(matches) != 1 or not suffix:
            report["errors"].append(f"Unrecognized or ambiguous PNG name: {path.name}")
            continue
        kind = "ORM" if suffix[1] == "OcclusionRoughnessMetallic" else suffix[1]
        identified.setdefault((matches[0], kind), []).append(path)
    for material in SETS:
        for kind in KINDS:
            matches = identified.get((material, kind), [])
            if len(matches) != 1:
                report["errors"].append(f"{material}/{kind}: expected one matching PNG; found {len(matches)}")
            elif groups is not None:
                result = check_map(matches[0], material, kind, groups[material])
                report["maps"].append(result)
                if not result["passed"]:
                    report["errors"].append(f"{material}/{kind}: " + "; ".join(result["errors"]))
    report["passed"] = not report["errors"] and len(report["maps"]) == 6
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "maps-verification.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": run_id, "passed": report["passed"], "maps_checked": len(report["maps"]),
                      "errors": report["errors"], "report": report_path.relative_to(ROOT).as_posix()}, separators=(",", ":")))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
