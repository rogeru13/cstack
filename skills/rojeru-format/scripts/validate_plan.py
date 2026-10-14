#!/usr/bin/env python3
"""Validate a rojeru edit-plan contract. Does not render or judge the edit."""
import argparse
from fractions import Fraction
import json
import math
import re
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

    def normalized(text):
        return " ".join(text.split()).casefold()
    def lowercase_display(text):
        # Contextual divine-name usage still requires editorial review.
        text = re.sub(r"\b(?:God|Jesus|Christ|Lord|Holy Spirit)\b", "", text)
        return text == text.lower()

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
        require(title.get("font") == "Inter" and title.get("position") == "center", "Title must be centered Inter")
        require(title.get("text", "").endswith("."), "Title must end in a period")
        require(lowercase_display(title.get("text", "")), "Title must be lowercase except sacred names")
        require(title.get("name") == "rojeru" and title.get("name_font") == "Inter", "Name must be rojeru in Inter")
        require(title.get("name_position") == "below-title", "Name must sit below the title")
        a, b = title.get("name_size"), title.get("size")
        require(isinstance(a, (int, float)) and isinstance(b, (int, float)) and 0 < a < b and math.isfinite(b), "Name must be smaller than the title")
        dialogue = plan["dialogue"]
        require(bool(dialogue), "Dialogue intervals are required")
        dialogue_end = 0
        for i, item in enumerate(dialogue):
            if not interval(item):
                errors.append(f"Dialogue {i}: invalid interval"); continue
            expected_start = body_start if dialogue_end == hook_end else dialogue_end
            require(item["start_frame"] == expected_start, f"Dialogue {i}: unintended gap or overlap")
            dialogue_end = item["end_frame"]
            require(item.get("volume_db") == 10, f"Dialogue {i}: volume must be +10 dB absolute")
            require(item["end_frame"] <= end, f"Dialogue {i}: extends beyond the edit")
            require(item["end_frame"] <= hook_end or item["start_frame"] >= body_start, f"Dialogue {i}: speech crosses the protected pause")
        require(any(d.get("start_frame") == body_start for d in dialogue), "Body speech must start at body_start_frame")
        require(any(d.get("end_frame") == hook_end for d in dialogue), "Hook dialogue must end at hook_end_frame")

        sentences = plan["sentences"]
        seen, previous_end = {}, 0
        sentence_order = []
        hook_cues = []
        captions = plan["captions"]
        require(bool(captions), "Captions are required")
        for i, cue in enumerate(captions):
            prefix = f"Caption {i}"
            if not interval(cue):
                errors.append(f"{prefix}: invalid interval"); continue
            require(cue["start_frame"] >= previous_end and cue["end_frame"] <= end, f"{prefix}: overlap or out of bounds")
            previous_end = cue["end_frame"]
            sid = cue.get("sentence_id")
            require(isinstance(sid, str) and sid in sentences, f"{prefix}: valid sentence_id is required")
            if isinstance(sid, str):
                if not sentence_order or sentence_order[-1] != sid:
                    require(sid not in sentence_order, f"{prefix}: sentence cues must stay consecutive")
                    sentence_order.append(sid)
            lines = cue.get("lines", [])
            valid_lines = (isinstance(lines, list) and len(lines) == 1 and
                           isinstance(lines[0], str) and bool(lines[0].strip()) and
                           len(lines[0].splitlines()) == 1)
            require(valid_lines, f"{prefix}: must show exactly one nonempty line")
            if valid_lines:
                require(len(lines[0].split()) <= 6, f"{prefix}: at most six words")
                require(lowercase_display(lines[0]), f"{prefix}: lowercase except sacred names")
                if isinstance(sid, str):
                    seen.setdefault(sid, []).append(lines[0])
            require(cue.get("font") == "Inter", f"{prefix}: captions must use Inter")
            if cue["end_frame"] <= hook_end:
                hook_cues.append(cue)
                require(cue.get("position") == "center" and cue.get("color", "").upper() == "#FFE32D", "Hook captions must be centered #FFE32D")
            else:
                require(cue["start_frame"] >= body_start and cue.get("position") == "bottom" and
                        cue.get("color", "").upper() == "#FFFFFF", f"{prefix}: body captions must be white/bottom after the pause")
            if inter_font and valid_lines:
                from PIL import ImageFont
                size, max_width = cue.get("size"), cue.get("max_width")
                if not isinstance(size, int) or size <= 0 or not isinstance(max_width, (int, float)) or not 0 < max_width <= width:
                    errors.append(f"{prefix}: provide positive pixel size and max_width within the canvas"); continue
                font = ImageFont.truetype(str(inter_font), size)
                require("inter" in font.getname()[0].lower(), "Provided caption font must actually be Inter")
                require(all(font.getlength(line) <= max_width for line in lines), f"{prefix}: text exceeds measured width; split into shorter one-line cues")
        require(set(sentences) == set(seen), "Every planned sentence needs caption coverage")
        for sid, text in sentences.items():
            require(normalized(" ".join(seen.get(sid, []))) == normalized(text),
                    f"Sentence {sid}: captions must preserve every word and punctuation in order")
        require(bool(hook_cues) and hook_cues[0]["start_frame"] == 0 and hook_cues[-1]["end_frame"] == hook_end,
                "Hook cues must span the first sentence")
        require(all(a["end_frame"] == b["start_frame"] for a, b in zip(hook_cues, hook_cues[1:])),
                "Hook cues must have continuous coverage")
        require(len({c.get("sentence_id") for c in hook_cues}) == 1, "Hook is the first complete sentence")

        broll = plan["broll"]
        require(bool(broll), "B-roll is required")
        ordered = []
        identities = {"asset_id": set(), "source_id": set(), "source_hash": set()}
        rejected = set(plan["rejected_source_ids"])
        for i, clip in enumerate(broll):
            if not interval(clip): errors.append(f"B-roll {i}: invalid interval"); continue
            require(hook_end <= clip["start_frame"] < end and clip["end_frame"] <= end, f"B-roll {i}: out of bounds")
            require(bool(clip.get("asset_id")) and bool(clip.get("relevance")), f"B-roll {i}: catalog identity and relevance are required")
            require(bool(clip.get("source_id")), f"B-roll {i}: canonical source_id is required")
            require(clip.get("source_id") not in rejected, f"B-roll {i}: rejected source")
            for key, used in identities.items():
                identity = clip.get(key)
                if identity:
                    require(identity not in used, f"B-roll {i}: repeated {key}")
                    used.add(identity)
            ordered.append(clip)
        require(any(c.get("start_frame") == hook_end and c.get("end_frame", 0) > body_start for c in broll),
                "The same first B-roll must start at hook end and continue into body speech")
        opening = next((c for c in broll if c.get("start_frame") == hook_end), None)
        if opening:
            require(title.get("end_frame", 0) <= opening.get("end_frame", 0), "Hook title must clear by the end of the opening B-roll")
        ordered.sort(key=lambda c: c["start_frame"])
        require(bool(ordered) and ordered[0]["start_frame"] == hook_end, "First B-roll must start at hook end")
        for first, second in zip(ordered, ordered[1:]):
            gap = second["start_frame"] - first["end_frame"]
            require(round(2 * fps) <= gap <= round(3 * fps),
                    "B-roll inserts need 2–3 seconds of talking head between previous end and next start")
        if not inter_font:
            warnings.append("Font widths not measured; pass --inter-font and per-cue size/max_width for measured one-line layout")
        warnings.append("A valid plan does not prove silence trimming, actual gain, resolved identities, visible talking-head gaps, title clearance or preserved grades. Inspect the native timeline. Export only when authorized.")
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
