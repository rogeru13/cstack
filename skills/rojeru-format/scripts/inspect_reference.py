#!/usr/bin/env python3
"""Extract timestamped reference frames without changing the movie. Requires Pillow and FFmpeg."""
import argparse
import json
import math
from pathlib import Path
import subprocess


def run(args, timeout=90):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:])
    return result.stdout


def inspect(source, output, times=None, count=12, width=400):
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError("Pillow is missing in this Python environment; use an existing environment with Pillow or install it in an isolated environment") from exc

    source = Path(source).resolve(strict=True)
    if not 2 <= count <= 60 or not 160 <= width <= 1920:
        raise ValueError("count must be 2–60; width must be 160–1920")
    metadata = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(source)]))
    video = next((s for s in metadata["streams"] if s["codec_type"] == "video"), None)
    if video is None:
        raise ValueError("No video stream; this may be an audio-only export despite its filename")
    duration = float(video.get("duration") or metadata["format"]["duration"])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("A finite positive duration is required")
    # Sample inside the clip, including its opening and ending; never seek to EOF.
    times = list(times) if times is not None else [duration * (0.005 + 0.985 * i / (count - 1)) for i in range(count)]
    if not times or len(times) > 60 or any(not math.isfinite(t) or t < 0 or t >= duration for t in times):
        raise ValueError("Provide 1–60 finite timestamps inside the clip")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    frames = []
    for i, t in enumerate(times):
        path = output / f"frame-{i:03d}.png"
        run(["ffmpeg", "-v", "error", "-nostdin", "-threads", "2", "-ss", f"{t:.6f}", "-i", str(source),
             "-map", "0:v:0", "-frames:v", "1", "-vf", f"scale={width}:-2,setsar=1", str(path)])
        if not path.is_file():
            raise RuntimeError(f"No frame decoded at {t:.3f}s")
        frames.append({"requested_seconds": t, "file": path.name})
    images = [Image.open(output / f["file"]).convert("RGB") for f in frames]
    cell_h = max(im.height for im in images) + 30
    columns = min(4, len(images))
    board = Image.new("RGB", (columns * width, math.ceil(len(images) / columns) * cell_h), "#171717")
    draw = ImageDraw.Draw(board)
    for i, (frame, im) in enumerate(zip(frames, images)):
        x, y = (i % columns) * width, (i // columns) * cell_h
        board.paste(im, (x, y))
        draw.text((x + 8, y + cell_h - 23), f"{frame['requested_seconds']:.3f} s", fill="white")
    board.save(output / "contact-sheet.jpg", quality=92)
    report = {"source": str(source), "duration_seconds": duration, "video": video,
              "frames": frames, "limitations": [
                  "Frames are samples, not proof of full playback, listening, exact cut boundaries, or user acceptance.",
                  "FFmpeg autorotation is enabled. The contact sheet forces square pixels; consult source SAR for unusual media.",
                  "No creative grade, HDR tone map, or camera-log transform is applied. HDR/log previews are not color references.",
                  "Requested seek times identify neighborhoods; use frame-index/timebase checks for exact edit timing."]}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New directory; existing evidence is never overwritten")
    parser.add_argument("--times", help="Comma-separated seconds, for example 0.1,1,3,6,12")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--width", type=int, default=400)
    args = parser.parse_args()
    try:
        times = [float(t) for t in args.times.split(",")] if args.times else None
        report = inspect(args.source, args.output, times, args.count, args.width)
    except (ValueError, RuntimeError, OSError, StopIteration, KeyError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"Reference inspection failed: {exc}\n")
    print(json.dumps({"output": str(args.output.resolve()), "duration": report["duration_seconds"], "frames": len(report["frames"])}))


if __name__ == "__main__":
    main()
