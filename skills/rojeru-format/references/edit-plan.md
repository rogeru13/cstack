# A small, checkable edit plan

Keep the plan beside the project. All timeline intervals are start-inclusive,
end-exclusive integer frames; FPS may be a rational string such as `24000/1001`.
Source in/out points belong in the cutlist/visual manifest; do not confuse them with
these timeline coordinates. Keep original source paths and media private.

This 15-second example illustrates the schema, not a required duration or script:

```json
{
  "width": 1440, "height": 1080, "fps": "24/1", "end_frame": 360,
  "hook_end_frame": 72, "body_start_frame": 120,
  "title": {"text": "A fresh start", "font": "Helvetica", "position": "center",
    "size": 84, "name": "rojeru", "name_font": "Inter", "name_size": 36,
    "name_position": "below-title", "start_frame": 72, "end_frame": 144},
  "dialogue": [{"start_frame": 0, "end_frame": 72}, {"start_frame": 120, "end_frame": 360}],
  "sentences": {"s1": "I tried something new.", "s2": "Here is what happened."},
  "captions": [
    {"sentence_id": "s1", "start_frame": 0, "end_frame": 72,
      "lines": ["I tried something new."], "font": "Inter", "position": "center",
      "color": "#FFE32D", "size": 64, "max_width": 1200},
    {"sentence_id": "s2", "start_frame": 120, "end_frame": 360,
      "lines": ["Here is what happened."], "font": "Inter", "position": "bottom",
      "color": "#FFFFFF", "size": 52, "max_width": 1200}
  ],
  "broll": [
    {"start_frame": 72, "end_frame": 144, "asset_id": "chosen-clip-1", "relevance": "Establishes the new place"},
    {"start_frame": 144, "end_frame": 216, "asset_id": "chosen-clip-2", "relevance": "Shows the action being described"},
    {"start_frame": 216, "end_frame": 288, "asset_id": "chosen-clip-3", "relevance": "Shows the consequence"},
    {"start_frame": 288, "end_frame": 360, "asset_id": "chosen-clip-4", "relevance": "Pays off the final line"}
  ]
}
```

Typeface size, weight, body color and margins above are illustrative project choices.
Choose them from the selected reference, test at the final display size, and preserve
the user's corrections. `size` and `max_width` are pixels in the delivery canvas.

Keep each caption's complete sentence in `sentences`; its displayed lines must contain
all those words with punctuation. Never use this manifest to claim that a line was
spoken; checked transcription supplies that evidence. The validator checks one cue per
sentence. It flags long-sentence overflow instead of silently switching to fragments.

The title must cover the complete pause and may continue through the opening B-roll,
as in the supplied references. The body cadence begins at `body_start_frame`; its
first B-roll change is due within three seconds of speech resuming, then every three
seconds. This permits the intentional opening hold without weakening the body cadence.

`validate_plan.py` rejects the wrong canvas, pause duration, title/name, hook color,
font assignment, caption overlap/line count/omitted text, B-roll start cadence, and
the opening insert's continuity across the speech return. Body inserts may alternate
with talking-head footage; the validator does not require wall-to-wall B-roll.
With an actual Inter font it also measures line width. Pillow is needed only for that
measurement. Resolve Text+ rendering still needs visual inspection, because tracking,
shadows, transformations and safe zones are not represented by simple glyph widths.

Check the real output separately: actual speech gaps, repeated takes, source frames,
audio joins, effective displayed lines, hook pause and overlap, crop, end frame, and
full decode. A manifest is intent; the export is the evidence.
