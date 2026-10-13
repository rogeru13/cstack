#!/usr/bin/env python3
"""Validate a rojeru edit-plan contract. Does not render or judge the edit."""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path


def validate(plan, inter_font=None):
    errors, warnings = [], []
    def require(condition, message):
        if not condition:
            errors.append(message)
    def frame(value):
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0
    def interval(item):
        return frame(item.get("start_frame")) and frame(item.get("end_frame")) and item["end_frame"] > item["start_frame"]

    try:
        width, height = plan["width"], plan["height"]
        require(isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0 and width * 3 == height * 4,
                "Canvas must be positive integer dimensions in 4:3")
        fps = Fraction(str(plan["fps"]))
        require(fps > 0, "FPS must be positive")
        end, hook_end, body_start = plan["end_frame"], plan["hook_end_frame"], plan["body_start_frame"]
        if not all(frame(n) for n in (end, hook_end, body_start)) or not 0 < hook_end < body_start < end or fps <= 0:
            raise ValueError("Require ordered integer hook_end < body_start < end and positive FPS")
        pause = round(2 * fps)
        require(body_start - hook_end == pause, "Hook speech pause must be two seconds rounded once to the timeline FPS")
        title = plan["title"]
        require(interval(title) and title.get("start_frame") == hook_end and body_start <= title.get("end_frame", 0) <= end,
                "Title must cover the protected hook pause; it may continue over resumed speech")
        require(bool(title.get("text", "").strip()), "Title text is required")
        require(title.get("font") == "Helvetica" and title.get("position") == "center", "Title must be centered Helvetica")
        require(title.get("name") == "rojeru" and title.get("name_font") == "Inter", "Name must be rojeru in Inter")
        require(title.get("name_position") == "below-title", "Name must sit below the title")
        a, b = title.get("name_size"), title.get("size")
        require(isinstance(a, (int, float)) and isinstance(b, (int, float)) and 0 < a < b and math.isfinite(b), "Name must be smaller than the title")
        dialogue = plan["dialogue"]
        require(bool(dialogue), "Dialogue intervals are required")
        for i, item in enumerate(dialogue):
            if not interval(item):
                errors.append(f"Dialogue {i}: invalid interval"); continue
            require(item["end_frame"] <= end, f"Dialogue {i}: extends beyond the edit")
            require(item["end_frame"] <= hook_end or item["start_frame"] >= body_start, f"Dialogue {i}: speech crosses the protected pause")
        require(any(d.get("start_frame") == body_start for d in dialogue), "Body speech must start at body_start_frame")
        require(any(d.get("end_frame") == hook_end for d in dialogue), "Hook dialogue must end at hook_end_frame")

        sentences = plan["sentences"]
        seen, previous_end = set(), 0
        captions = plan["captions"]
        require(bool(captions), "Captions are required")
        for i, cue in enumerate(captions):
            prefix = f"Caption {i}"
            if not interval(cue):
                errors.append(f"{prefix}: invalid interval"); continue
            require(cue["start_frame"] >= previous_end and cue["end_frame"] <= end, f"{prefix}: overlap or out of bounds")
            previous_end = cue["end_frame"]
            sid = cue.get("sentence_id")
            require(isinstance(sid, str) and sid in sentences and sid not in seen, f"{prefix}: each full sentence needs its own unique cue")
            if isinstance(sid, str): seen.add(sid)
            text = sentences.get(sid, "") if isinstance(sid, str) else ""
            require(bool(text) and text.rstrip(' \"\u201d\u2019\'')[-1:] in (".", "!", "?", "…"), f"{prefix}: sentence needs terminal punctuation")
            lines = cue.get("lines", [])
            valid_lines = isinstance(lines, list) and 1 <= len(lines) <= 2 and all(isinstance(line, str) and line.strip() for line in lines)
            require(valid_lines, f"{prefix}: must show one or two nonempty lines")
            if valid_lines:
                require(" ".join(" ".join(lines).split()) == " ".join(text.split()), f"{prefix}: lines must contain the complete sentence, without omissions or merged sentences")
            require(cue.get("font") == "Inter", f"{prefix}: sentence captions must use Inter")
            if i == 0:
                require(cue["start_frame"] == 0 and cue["end_frame"] == hook_end, "First sentence cue must cover the hook")
                require(cue.get("position") == "center" and cue.get("color", "").upper() == "#FFE32D", "Hook captions must be centered #FFE32D")
            else:
                require(cue["start_frame"] >= body_start and cue.get("position") == "bottom", f"{prefix}: body captions must be bottom-positioned after the pause")
            if inter_font and valid_lines:
                from PIL import ImageFont
                size, max_width = cue.get("size"), cue.get("max_width")
                if not isinstance(size, int) or size <= 0 or not isinstance(max_width, (int, float)) or not 0 < max_width <= width:
                    errors.append(f"{prefix}: provide positive pixel size and max_width within the canvas"); continue
                font = ImageFont.truetype(str(inter_font), size)
                require("inter" in font.getname()[0].lower(), "Provided caption font must actually be Inter")
                require(all(font.getlength(line) <= max_width for line in lines), f"{prefix}: text exceeds its measured width; rebreak or resolve the long-sentence exception")
        require(set(sentences) == seen, "Every planned sentence needs one complete caption cue")

        broll = plan["broll"]
        require(bool(broll), "B-roll is required")
        starts = []
        for i, clip in enumerate(broll):
            if not interval(clip): errors.append(f"B-roll {i}: invalid interval"); continue
            require(hook_end <= clip["start_frame"] < end and clip["end_frame"] <= end, f"B-roll {i}: out of bounds")
            require(bool(clip.get("asset_id")) and bool(clip.get("relevance")), f"B-roll {i}: catalog identity and relevance are required")
            starts.append(clip["start_frame"])
        require(any(c.get("start_frame") == hook_end and c.get("end_frame", 0) > body_start for c in broll),
                "The same first B-roll must start at hook end and continue into body speech")
        opening = next((c for c in broll if c.get("start_frame") == hook_end), None)
        if opening:
            require(title.get("end_frame", 0) <= opening.get("end_frame", 0), "Hook title must clear by the end of the opening B-roll")
        starts = sorted(set(starts))
        require(bool(starts) and starts[0] == hook_end, "First B-roll must start at hook end")
        cadence = math.ceil(3 * fps)
        if starts:
            body_changes = [body_start] + [s for s in starts if s > body_start] + [end]
            require(all(b - a <= cadence for a, b in zip(body_changes, body_changes[1:])), "Body B-roll changes have a gap longer than three seconds")
        if not inter_font:
            warnings.append("Font widths not measured; pass --inter-font and per-cue size/max_width before rendering")
        warnings.append("A valid plan does not prove removed stutters, real media availability, relevant B-roll, correct Resolve styling, or the final export. Inspect those separately.")
    except (AttributeError, KeyError, TypeError, ValueError, ZeroDivisionError, OSError, ImportError) as exc:
        errors.append(f"Invalid/incomplete plan or font environment: {exc}")
    return {"valid": not errors, "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--inter-font", type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.plan.read_text()), args.inter_font)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Could not read plan: {exc}\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
