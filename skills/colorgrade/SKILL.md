---
name: colorgrade
description: >-
  Color-correct, shot-match, and creatively grade video in DaVinci Resolve. Use for
  camera-log or HDR normalization, skin-tone and exposure problems, matching a reference,
  preserving or revising an existing node grade, LUT checks, and checking export color.
  General cutting, captions, and sound remain with video-edit.
---

# Colorgrade

Deliver a deliberate, repeatable look on the actual export, with the input transform,
creative choices, and output transform accounted for. Technical correctness and taste
are separate: a warm, dark reference is not automatically an exposure error.

Read `~/.colorgrade/profile.md` when present. It holds camera/profile evidence, accepted
looks, monitoring/output preferences, and local tool paths. The current brief and live
project take precedence. When working with video-edit or rojeru-format, those skills own
the edit; this skill owns color only. Preserve cuts, framing, captions, and sound.

## Establish the transform and the baseline

1. Inspect the active Resolve project/timeline, grade versions, clip/group/timeline nodes,
   shared nodes, LUTs, adjustment clips, color-management settings, and output settings.
   Read [Resolve operations](references/resolve.md) before mutations.
2. Probe a representative source and the last accepted export:
   `python3 SKILL_DIR/scripts/color_audit.py probe FILE`.
   Verify camera gamut/gamma from recording settings, camera metadata/sidecars, or the
   user's evidence. A Sony filename, flat appearance, or `bt709` container tag does not
   establish S-Log3, S-Gamut3.Cine, or a baked-in conversion.
3. State the path: source encoding → working space → look → output display space,
   identifying which stages the project already performs. Use its existing RCM, ACES,
   or explicit CST/LUT workflow unless changing it is part of the task. Do not stack
   another log-to-display or HDR-to-SDR transform on normalized media.
4. Save a baseline project/grade and use a new local grade version or duplicated timeline.
   Check remote/shared grades before touching them: duplicating a timeline alone does
   not isolate a shared grade. Preserve the user's node tree, paid LUT paths and effects.
   If the input encoding is unresolved, inspect and propose candidates on a test copy;
   do not bake a guessed conversion into a deliverable.

For input/output decisions, HDR, scopes, and matching, read
[the grading procedure](references/grading.md). For optional libraries or DCTL work,
read [sources and tools](references/sources.md); no extra package is required for
ordinary Resolve grading.

## Build and compare the look

- Define the reference's observable properties: light direction, contrast, skin hue,
  shadow density, highlight roll-off, palette, texture, and saturation. Separate lighting
  and set design from effects a grade can reproduce. Use a matched shot where possible.
- Normalize and balance first, then match exposures/white balance across comparable
  shots. Build the look in separate, named nodes appropriate to the established working
  space. Keep brand graphics, screen recordings and captions out of a camera-log chain.
- Use waveform, RGB parade, and vectorscope alongside the image. Isolate skin when
  evaluating it; the skin-tone indicator is a hue guide, not a requirement to push every
  face to one hue or brightness. Whole-frame averages are not white-balance targets.
- Work on one representative shot and one difficult shot before propagating. A fixed
  creative look can be shared; exposure/WB/masks often need per-shot adjustments.
- Review the opening, adjacent cuts, brightest skin/highlights, darkest useful detail,
  and motion through any tracking/NR/halation. Match the accepted atmosphere; don't
  flatten low-key lighting merely to fill the waveform. Check at delivery size too.

Use existing native controls, a verified LUT/PowerGrade, or a tested tool. Do not
invent Resolve APIs for arbitrary primary wheels, CST parameters, or OFX controls.
An MCP success response is not proof that the image changed.

## Verify and deliver

Render a short representative native sample before a long final encode. Compare the
same source frame before/after and the encoded export under the same view transform.
Verify dimensions, FPS, range and color tags, clipping/banding, shot consistency, and
the real target-player appearance when accessible. Investigate a viewer/gamma mismatch
before changing the grade. Tagging a file is not a color transform.

For a **verified display-referred SDR Rec.709** export, collect reproducible diagnostic
stills and scopes:

```sh
python3 SKILL_DIR/scripts/color_audit.py scopes EXPORT --times 1,8,15 \
  --confirmed-sdr709 --output NEW_QA_DIRECTORY
python3 SKILL_DIR/scripts/color_audit.py cube LOOK.cube
```

The helper refuses HDR/conflicting primaries and never applies a transform. Its scopes
are 8-bit diagnostics, not HDR mastering measurements; LUT checks establish file
structure, not correct color science or a good look. Use Resolve's full-precision
scopes for grading decisions. For HDR retain the intended HDR mastering workflow.

Deliver the export and native grade/project as requested, with a short record of the
transform path, look/version, shot exceptions, before/after evidence, checks that ran,
and open limitations. Do not substitute a flattened export for an editable grade.
For color-only changes, verify picture/timing and reuse unchanged audio evidence.
Store a newly accepted personal look in the profile or local asset library, including
its required input space. Never infer approval solely from a successful render.
