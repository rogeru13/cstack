# Exact rojeru format

Authority: Roger's direct corrections through 2026-10-14. Display name is **rojeru**.
Current requests override this contract; older sampled exports do not override it.
Read the local profile for references, rejected assets and project-specific settings.

| Element | Contract |
| --- | --- |
| Speech | Trim silence at both clip edges, repetitions and stutters while preserving complete speech. Close unintended linked timeline gaps. |
| Dialogue volume | Inspector Volume +10.0 dB absolute, not cumulative. |
| Canvas | 4:3, existing resolution/timebase; Scale full frame with crop without accidental additional zoom. Preserve accepted reframing. |
| All text | Lowercase, including sentence starts and `i`, except sacred names such as God and Jesus. |
| Hook captions | Centered Inter #FFE32D; one line, at most six words per speech-timed cue. |
| Hook exit | Cut to one B-roll insert after the first complete sentence; retain two seconds without dialogue. |
| Title | Centered Inter, ends in a period; smaller Inter `rojeru` directly below with no descender overlap. |
| Speech return | Resume narration over the same opening B-roll; default to holding title/name until that insert ends. |
| Body captions | White Inter at bottom; one line, at most six words; preserve all words across cues. |
| B-roll spacing | 2–3 seconds of visible talking head between consecutive inserts, including after the opening. Continuous dialogue, no empty gaps. |
| B-roll identity | Never repeat a source within one timeline; renamed copies, different ranges and hash-identical media count as repeats. Exclude rejected assets. |
| Revisions | Preserve grade, crop, scaling, audio and existing cuts unless specifically requested. Native transparent titles only. |
| Delivery | Keep Resolve open. Save natively. No video renders/exports until explicitly requested. |

## Timing and layout

Let `H` be the exclusive first-sentence end and `P` two seconds rounded once to rational
FPS. Body begins at `H + P`. Before `H`, split the hook into short centered yellow cues.
`[H,H+P)` has B-roll/title and no dialogue. At `H+P`, white bottom captions and speech
resume over that same insert. The first insert must extend beyond the narration return.
After it ends, show the talking head for 2–3 seconds before the next insert. Measure
spacing end-to-start, never start-to-start. Ending talking-head footage need not be
shortened merely to force another insert. Retiming must ripple dependent layers together.

One sentence may span multiple cues. Preserve its words, order and punctuation across
those cues. Split further if a six-word cue would wrap; never make a second line.
Lowercase display is a deliberate style, so transcription may retain original casing.
Sacred-name capitalization is contextual; do not capitalize an ordinary use of a word
like `spirit` just because it also occurs in a religious name.

No universal exact font size, weight, title/name gap, bottom coordinate, music, LUT,
transition or speed is established. Preserve accepted project values or use the chosen
reference. Inspect actual displayed glyphs, safe margins and descender clearance.
The intentional title pause is the exception to speech-gap removal.
