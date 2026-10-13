# Exact rojeru format

Source of authority: Roger's direct instructions, 2026-10-13. Display name confirmed
as **rojeru**, without an underscore. Earlier sampled exports are evidence of particular
edits, not authority to replace these rules.

| Element | Contract |
| --- | --- |
| Speech | Remove accidental repeated sentences, stutters, silence and dead space. Preserve complete delivery and meaning. |
| Canvas | 4:3. Do not switch to 9:16 because the destination is a social platform. |
| First spoken sentence | Inter captions, centered on screen, color **#FFE32D**. |
| Hook exit | After that sentence, cut picture to B-roll and retain two seconds with no speech. |
| Title pause | Title centered in Helvetica; **rojeru** below in smaller Inter. |
| Speech return | Resume narration while the same B-roll is still playing. |
| Body captions | Inter, bottom position, full sentences with punctuation. Each sentence begins a fresh cue; never more than two displayed lines. |
| Other typography | Helvetica for titles, labels, graphic emphasis. |
| Body picture | Add/change relevant B-roll every three seconds. |

## Priority and unresolved choices

The two-second hook pause is intentional storytelling and overrides the general removal
of silence. Three-second B-roll cadence does not move the first cut earlier than the
first sentence's end. Keep the first insert through the pause and into resumed speech.

A sentence cue may occupy one or two lines. Never show a previous sentence's tail beside
the start of the next sentence. A full sentence too long for two readable lines is an
explicit layout exception to resolve; this skill does not silently change to word chunks.

The user did not set universal font sizes/weights, body-caption color, title color,
music tracks/levels, transition effects, playback-speed multipliers, or a color LUT.
Measure those from the selected accepted reference or preserve the current project.
Treat any fallback as a project choice, not a new permanent default. Keep captions clear
of important faces and subjects while honoring the requested center/bottom placement.

## Hook timeline

Let `H` be the exclusive end frame of the first spoken sentence and `P` be two seconds
rounded once to the timeline timebase. The body begins at `H + P`.

- Before `H`: first-sentence centered yellow Inter captions over the opening picture.
- `[H, H+P)`: B-roll plays, title/name centered, no dialogue.
- At `H+P`: body speech and bottom sentence captions begin. The supplied references
  hold the title/name over this return; default to clearing them with the opening insert.
- After `H+P`: the first B-roll continues visibly before the next shot. Do not cut back
  to the speaker on the exact narration-return frame.

Count the three-second body cadence from the narration return, then between B-roll
starts. The protected opening insert may span the two-second pause plus up to three
seconds of resumed narration. Do not shorten it to satisfy a cadence measured across
the intentional pause. A project can use a shorter hold while keeping visible overlap.

Use integer timeline frames and rational FPS. Do not independently round every layer
from floating-point seconds. Retiming must ripple picture, text, title and audio together.
