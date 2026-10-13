#!/usr/bin/env python3
"""Read-only media metadata, confirmed SDR scope extraction, and basic .cube integrity checks."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shlex
import subprocess


def run(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=90)
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:])
    return result.stdout


def probe(path):
    path = Path(path).resolve(strict=True)
    data = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
    video = next((s for s in data["streams"] if s.get("codec_type") == "video"), None)
    if video is None:
        raise ValueError("No video stream")
    warnings = ["Container tags do not prove the camera picture profile, LUT history, or current Resolve transforms."]
    if video.get("color_transfer") in ("smpte2084", "arib-std-b67"):
        warnings.append("HDR transfer detected. Do not judge SDR exposure from an unconverted preview.")
    if any(video.get(k) in (None, "unknown", "unspecified") for k in ("color_space", "color_transfer", "color_primaries", "color_range")):
        warnings.append("Color tags are incomplete; verify the input encoding and range before transforming.")
    return {"source": str(path), "video": video, "format": data["format"], "warnings": warnings}


def scopes(path, output, times, confirmed_sdr709=False):
    report = probe(path)
    if not confirmed_sdr709:
        raise ValueError("Scopes require --confirmed-sdr709 after independently verifying a display-referred Rec.709 source/export")
    v = report["video"]
    if v.get("color_transfer") in ("smpte2084", "arib-std-b67") or v.get("color_primaries", "bt709") not in ("bt709", "unknown", "unspecified"):
        raise ValueError("Tags conflict with SDR Rec.709. Supply a verified normalized export instead of overriding them.")
    duration = float(v.get("duration") or report["format"]["duration"])
    if not times or len(times) > 20 or not math.isfinite(duration) or any(not math.isfinite(t) or t < 0 or t >= duration for t in times):
        raise ValueError("Provide 1–20 finite timestamps within the video duration")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    filters = {
        "frame": "scale=960:-2,setsar=1",
        "rgb-parade": "format=gbrp,waveform=display=parade:components=7:graticule=green:scale=digital,scale=960:320,setsar=1",
        "vectorscope": "format=yuv444p,vectorscope=mode=color2:graticule=color:colorspace=709,scale=640:640",
    }
    report["samples"] = []
    for i, t in enumerate(times):
        files = {}
        for name, vf in filters.items():
            dest = output / f"{i:02d}-{name}.png"
            run(["ffmpeg", "-v", "error", "-nostdin", "-threads", "2", "-ss", f"{t:.6f}", "-i", report["source"],
                 "-map", "0:v:0", "-an", "-frames:v", "1", "-vf", vf, str(dest)])
            if not dest.is_file():
                raise RuntimeError(f"No {name} frame at {t}s")
            files[name] = dest.name
        report["samples"].append({"requested_seconds": t, "files": files})
    report["scope_interpretation"] = {
        "source_confirmation": "Caller verified display-referred SDR Rec.709; no camera transform or LUT is applied by this script.",
        "rgb_parade": "Decoded 8-bit RGB digital scale, not a legal-range YUV or HDR mastering measurement.",
        "vectorscope": "8-bit YUV Rec.709 diagnostic; inspect Resolve scopes and full precision for final decisions.",
        "limits": "Single frames do not prove temporal consistency, clipping across a shot, skin isolation, or perceived quality."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def audit_cube(path):
    path = Path(path).resolve(strict=True)
    size = None
    kind = None
    domain = {"DOMAIN_MIN": [0.0] * 3, "DOMAIN_MAX": [1.0] * 3}
    seen = set()
    rows = 0
    out_of_unit = 0
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        parts = shlex.split(line, comments=True)
        if not parts:
            continue
        key = parts[0]
        if key == "TITLE":
            continue
        if key in ("LUT_1D_SIZE", "LUT_3D_SIZE"):
            if size is not None or len(parts) != 2:
                raise ValueError("Duplicate or combined LUT sizes are not supported by this validator")
            size = int(parts[1]); kind = key
            if size < 2 or size > (256 if kind == "LUT_3D_SIZE" else 65536):
                raise ValueError("Unsupported LUT size")
            continue
        if key in domain:
            if key in seen or len(parts) != 4:
                raise ValueError(f"Malformed or duplicate {key}")
            domain[key] = [float(v) for v in parts[1:]]; seen.add(key)
            continue
        if len(parts) != 3:
            raise ValueError(f"Unsupported directive or invalid RGB row on line {number}")
        values = [float(v) for v in parts]
        if not all(math.isfinite(v) for v in values):
            raise ValueError(f"Non-finite RGB value on line {number}")
        rows += 1
        out_of_unit += int(any(v < 0 or v > 1 for v in values))
    if size is None:
        raise ValueError("Missing LUT size")
    if not all(math.isfinite(v) for values in domain.values() for v in values) or any(a >= b for a, b in zip(domain["DOMAIN_MIN"], domain["DOMAIN_MAX"])):
        raise ValueError("Invalid LUT domain")
    expected = size ** 3 if kind == "LUT_3D_SIZE" else size
    if rows != expected:
        raise ValueError(f"Expected {expected} RGB rows, found {rows}")
    return {"file": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "kind": kind,
            "size": size, "rows": rows, "domain": domain, "rows_outside_unit_interval": out_of_unit,
            "limits": "Structural validation only. Out-of-range outputs can be intentional. Input/output color spaces, interpolation, appearance, and rights still need verification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("probe", "cube", "scopes"):
        cmd = sub.add_parser(name)
        cmd.add_argument("source", type=Path)
        if name == "scopes":
            cmd.add_argument("--output", type=Path, required=True)
            cmd.add_argument("--times", required=True, help="Comma-separated seconds")
            cmd.add_argument("--confirmed-sdr709", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "probe": result = probe(args.source)
        elif args.command == "cube": result = audit_cube(args.source)
        else: result = scopes(args.source, args.output, [float(t) for t in args.times.split(",")], args.confirmed_sdr709)
    except (ValueError, RuntimeError, OSError, KeyError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"Color audit failed: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
