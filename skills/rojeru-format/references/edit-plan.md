# A small, checkable edit plan

Keep this beside the project. Intervals are start-inclusive/end-exclusive integer frames;
FPS may be rational, such as `24000/1001`. Private source paths remain local.
This illustrative schema is not a fixed creative template:

```json
{
  "width": 1440,
  "height": 1080,
  "fps": "24/1",
  "end_frame": 360,
  "hook_end_frame": 72,
  "body_start_frame": 120,
  "title": {
    "text": "a fresh start.",
    "font": "Inter",
    "position": "center",
    "size": 84,
    "name": "rojeru",
    "name_font": "Inter",
    "name_size": 36,
    "name_position": "below-title",
    "start_frame": 72,
    "end_frame": 144
  },
  "dialogue": [
    {
      "start_frame": 0,
      "end_frame": 72,
      "volume_db": 10
    },
    {
      "start_frame": 120,
      "end_frame": 360,
      "volume_db": 10
    }
  ],
  "sentences": {
    "s1": "i tried something new and found hope.",
    "s2": "here is what happened."
  },
  "captions": [
    {
      "sentence_id": "s1",
      "start_frame": 0,
      "end_frame": 36,
      "lines": [
        "i tried something new"
      ],
      "font": "Inter",
      "position": "center",
      "color": "#FFE32D",
      "size": 64,
      "max_width": 1200
    },
    {
      "sentence_id": "s1",
      "start_frame": 36,
      "end_frame": 72,
      "lines": [
        "and found hope."
      ],
      "font": "Inter",
      "position": "center",
      "color": "#FFE32D",
      "size": 64,
      "max_width": 1200
    },
    {
      "sentence_id": "s2",
      "start_frame": 120,
      "end_frame": 360,
      "lines": [
        "here is what happened."
      ],
      "font": "Inter",
      "position": "bottom",
      "color": "#FFFFFF",
      "size": 52,
      "max_width": 1200
    }
  ],
  "broll": [
    {
      "start_frame": 72,
      "end_frame": 144,
      "asset_id": "chosen-clip-1",
      "source_id": "original-source-1",
      "relevance": "Establishes the place"
    },
    {
      "start_frame": 204,
      "end_frame": 264,
      "asset_id": "chosen-clip-2",
      "source_id": "original-source-2",
      "relevance": "Shows the action"
    }
  ],
  "rejected_source_ids": []
}
```

`sentences` contains checked speech. Multiple consecutive cues may reference one sentence;
together their words and punctuation must match it, ignoring case. Each cue is exactly
one line, at most six words. Hook cues collectively span the first sentence before the
protected pause. Caption starts/ends still need speech alignment checks, not just bounds.

`source_id` is the canonical original-media identity from the index. Resolve aliases and
known duplicate hashes before populating it; add `source_hash` when verified. Reject
repeated asset IDs, source IDs or full hashes. Supply `rejected_source_ids` from the local
rejection ledger after canonicalizing aliases. The validator cannot discover concealed
copies or a missing rejection record. Apply the ledger to catalog selection as well.

B-roll gaps are measured from preceding end to following start, 2–3 seconds rounded to
frames. Those intervals must actually show talking-head footage in Resolve. The opening
insert spans the protected pause and extends into resumed speech. No forced final insert.

Run `python3 SKILL_DIR/scripts/validate_plan.py PLAN.json --inter-font INTER_FONT`.
The validator checks 4:3, pause, title/name, one-line/six-word captions, sentence coverage,
caption overlap, hook/body styling, +10 dB dialogue, unintended dialogue timeline gaps,
B-roll spacing and declared identity/rejection data. Font width measurement needs Pillow.
It does not prove actual waveforms are silence-free, native clips have the declared gain,
all media identities were resolved, or text renders without overlap. Inspect those in
Resolve. Inspect an exported file only after Roger authorizes rendering.
