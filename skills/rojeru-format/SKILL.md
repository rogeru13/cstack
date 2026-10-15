---
name: rojeru-format
description: >-
  Edit Roger's personal videos in DaVinci Resolve with cleaned speech, a 4:3 canvas,
  one-line captions of at most six words, yellow centered hook captions, an Inter
  title pause, and unique B-roll separated by talking-head coverage. Use for rojeru,
  rojeru_, Roger's usual editing format, or updates from his reference videos.
---

# Rojeru format

Roger's current direct instructions override older references. Before editing, read
[the exact contract](references/format.md) and `~/.rojeru-format/profile.md`.
These are the entry points for both creative preferences and local tool lessons.
Keep private media paths, titles, project values, catalogs and evidence in that profile
or project notes, not this public skill.

## Route the work

- Editing: use video-edit for source recovery, transcription and native Resolve work,
  with this format and [edit plan](references/edit-plan.md).
- References: use [reference analysis](references/reference-analysis.md). A sampled
  older export does not replace today's caption or pacing instructions.
- B-roll: use the profile's local index and [B-roll workflow](references/broll.md).
- Grading: use colorgrade only when needed. Text or timing revisions preserve the
  accepted grade, working/output transforms, crop and framing.

## Edit in Resolve

Work in the accepted native timeline. Inspect the active project/timeline before
mutating it. Keep Resolve open; never quit, restart or close the user's timeline to
recover scripting access. A native Workspace > Scripts Utility Lua script is a
working fallback when the console is inaccessible. Inspect supported API methods first.

Trim speech using audio evidence, including both edges of every retained clip.
Remove silent handles, restarts and accidental repetitions without clipping consonants
or breaths needed for delivery. Ripple linked picture/audio to close unintended gaps.
Set dialogue clip Volume to +10 dB absolute, never add another 10 dB on every pass.
Preserve the two-second intentional title pause; music may continue through it.

Use 4:3 and retain the existing resolution/FPS. For the requested fill, use Resolve's
Scale full frame with crop; do not add unintended transform zoom. Preserve deliberate
existing reframing. Use integer frames and rational FPS for all layers.

The first complete spoken sentence determines the hook end. Its captions are centered
Inter #FFE32D, split into speech-timed phrases of at most six words on exactly one line.
Then cut to one B-roll insert and hold a centered Inter title during the two-second
speech pause. Title ends in a period; smaller `rojeru` is centered directly beneath,
with visible clearance below descending letters. Resume speech over that same insert.
Default to clearing title/name with the opening insert unless instructed otherwise.
Body captions are white Inter at the bottom, one line and at most six words. Preserve
all spoken words across cues. Use lowercase including sentence starts and `i`, except
sacred names such as God, Jesus, Christ, Lord and Holy Spirit when used as divine names.
Font size, exact coordinates and weight remain project choices. Check phone readability.
Six words is a ceiling, not a target. Balance visible width and reading effort across
neighboring cues; a five-word phrase can still be too heavy. Before splitting a dense
cue again, inspect whether its leading words fit naturally in the preceding shorter
cue. Move the boundary to the new phrase onset using speech evidence, preserving all
words and the one-line limit. Read neighboring captions from the timeline or saved
transcript yourself rather than asking Roger to repeat information already available.

Leave 2–3 seconds of visible talking-head footage between the end of one B-roll insert
and the next start, including the opening. This is continuous dialogue with camera
coverage, never an empty timeline gap. Never reuse a B-roll source in one timeline,
even with different in/out points or renamed/hash-identical copies. Filter rejected
footage before selection and after rescans; rejection affects indexes, not originals.

## Caption implementation and verification

Use native transparent titles, keeping all picture/audio independently editable.
Do not place camera-source carrier clips above the original edit. In-place text/layout
updates are preferable to rebuilding an accepted timeline. Before applying a batch,
check a representative native title's output and saved composition. If a title fails,
disable the failing layer immediately to reveal the accepted picture.

Run the [plan validator](references/edit-plan.md) for mechanical layout/pacing errors.
Compare protected picture/audio timing and properties before/after caption-only edits.
Check rendered viewer text, grade/framing and title/name clearance at final display size.
Confirm changes survive save and re-selection through Resolve's API/UI without restarting.
A successful SetInput/SaveProject proves a data operation, not visible typography.
If screenshots are stale or playback is unavailable, report that limit rather than
claiming visual or listening verification. A valid manifest is intent, not proof.

## Delivery boundary

Save the native project and caption sidecars. Do not export/render videos, including
review copies, until Roger explicitly asks. Changing export settings or saving a preset
is not permission to render. Inspect authorized settings and queued jobs separately:
existing queue jobs may retain old settings. Verify or create a fresh job when requested.
Phone/Instagram compatibility remains unconfirmed until tested; a saved preset alone
does not establish it. Check exports only when an export has been authorized.
