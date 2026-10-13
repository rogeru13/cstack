---
name: rojeru-format
description: >-
  Edit Roger's videos in the rojeru format in DaVinci Resolve: cleaned speech, centered
  yellow first-sentence captions, a two-second title pause over B-roll, bottom sentence
  captions, Inter/Helvetica typography, B-roll every three seconds, and a 4:3 canvas.
  Use when asked for rojeru, rojeru_, Roger's usual editing format, or to learn/update
  that format from his reference videos.
---

# Rojeru format

This is Roger's personal editing contract, defined directly by him. Read
[the exact format](references/format.md) before editing. It overrides generic
video-edit defaults for framing, captions, pacing, and B-roll. Do not infer different
defaults from older experiments or replace this format with a generic social reel.

Read `~/.rojeru-format/profile.md`: source folders, accepted references, local B-roll
catalog, tools and current refinements. Keep source files, contact sheets, filenames
revealing private projects, and personal reference records outside this public skill.
The reusable format itself belongs here; the current user brief overrides it.

## Route the work

- **Make/revise a video:** use video-edit for source recovery, transcription, Resolve
  assembly and export. Apply this skill's format and [edit plan](references/edit-plan.md).
- **Learn a reference:** use [reference analysis](references/reference-analysis.md).
  Extract evidence; don't silently change the user's explicit format.
- **Find B-roll:** use the profile's local catalog and [B-roll workflow](references/broll.md).
  Query before searching arbitrary directories or downloading stock.
- **Grade:** use colorgrade when available, preserving the current native grade and
  source/working/output transform. With no grade change requested, maintain the accepted look.

These companion skills are in this fork's sibling directories. Read only the relevant
ones. If unavailable, perform this contract through available tools and name any missing
capability; never claim a native editable result from a flattened movie.

## Build the speech and hook

Recover the latest accepted native timeline and brief first. Transcribe once and select
complete, fluent takes. Remove accidental repeated sentences, restarts, stutters, long
gaps, and dead space. Preserve meaning, complete consonants, natural breaths, and the
speaker's delivery. Examine both sides of every join; a transcript can hide a repetition.

Mark the end of the first complete spoken sentence in timeline frames. It anchors the
hook transition, title, two-second intentional pause, and resumed body speech. This pause
is protected from silence trimming. Cut picture to B-roll at the first sentence's end;
show a centered Helvetica title with **rojeru** beneath in smaller Inter; hold two seconds
without speech. Resume speech over that same B-roll before changing the shot. Music may
continue through the pause when the brief includes it. In the supplied references,
the title/name remain on the opening B-roll after speech resumes; use that hold through
the opening insert unless the current brief specifies another exit. Keep body captions
separate and readable beneath it.

## Captions and coverage

Caption the first sentence in centered Inter, exactly **#FFE32D**. Then use bottom Inter
captions, complete sentences with punctuation, no more than two displayed lines, with
each new sentence starting a fresh cue. Helvetica is for titles, labels and deliberate
graphic emphasis; it does not replace the Inter sentence-caption layer.

Lay out text using the actual font and output width, not a character count. If a complete
sentence will not fit two readable lines, flag it before rendering. Rebreak the lines or
adjust within the project's readable type-size range; do not silently omit words, shrink
to illegibility, or split it into phrase captions. A clause-by-clause exception or rewritten
spoken delivery needs a user decision. Preserve checked sentence data and an SRT sidecar.

Plan a relevant B-roll change every three seconds in the body, plus the protected hook
insert. Use genuine footage from the local catalog, checked against the sentence and
available source duration. Log source in/out, visible timeline interval, relevance,
crop and catalog ID. Avoid fabricating facts about people shown in illustrative footage.
Do not stretch a short clip, invent footage, or repeat an unrelated shot merely to hit
the cadence; find a suitable shot or report the specific coverage gap.

## Resolve assembly and proof

Build in **4:3**, retaining the established resolution and FPS. For a new project with no
other resolution specified, 1440×1080 is a supported local starting point; the ratio is
the rule, not a mandatory pixel size. Keep camera, B-roll, captions, title/name, dialogue,
music and SFX independently editable. Use Text+/native text for editable typography;
PNG captions are rendered layers, not editable text. Protect camera grades from title,
caption, or audio-only rebuilds.

Keep a small [edit-plan manifest](references/edit-plan.md) and validate it before rendering:

```sh
python3 SKILL_DIR/scripts/validate_plan.py edit-plan.json --inter-font /path/to/Inter.otf
```

The validator checks timing and layout contracts, not fluency, relevance, or taste.
Inspect the actual exported hook, title pause, resumed speech/B-roll overlap, every cut,
the longest captions, and the ending. Check consecutive frames around transitions and
listen when supported. Verify 4:3 geometry, exact output version, full decode, color and
audio separately. Record which checks actually ran and any accepted exception.

Deliver the current export, native editable project, caption sidecar, brief change list,
and unresolved issues. Keep the user's footage, music, paid LUTs and local evidence out
of the public fork. Improve the format from explicit corrections and accepted examples;
use Reflect/RSI for a requested workflow review or bounded comparison.
