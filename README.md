# cstack — Roger's fork

Personal fork of [goodnight000/cstack](https://github.com/goodnight000/cstack),
with Roger's Resolve format, a color-grading workflow, and one maintained skill set
shared by Claude Code and Codex. The upstream skills remain available below.

## Skills

| Skill | What it does |
| --- | --- |
| [rojeru-format](skills/rojeru-format/SKILL.md) | Roger's 4:3 format: cleaned speech, yellow centered hook, two-second title pause, sentence captions, Inter/Helvetica, and B-roll cadence. Includes a private local SSD catalog and edit-plan checks. |
| [colorgrade](skills/colorgrade/SKILL.md) | Resolve color management, shot matching, reference looks, existing-grade preservation, LUT integrity, and export diagnostics. |
| [reflect](skills/reflect/SKILL.md) | Reviews outcomes and efficiency, shows findings before asking for feedback, and proposes improvements for approval. Works with completed, incomplete, and unsuccessful sessions. |
| [rsi](skills/rsi/SKILL.md) | Tests changes to agent skills, instructions, tools, and working processes against the current version, with bounded runs and evidence for keeping or rejecting each change. |
| [video-edit](skills/video-edit/SKILL.md) | Edits talking-head videos, reels, demos, and screen recordings. Covers audio recovery, take selection, supporting visuals, Resolve revisions, captions, and final-export checks. |
| [animated-video](skills/animated-video/SKILL.md) | Makes animated videos in code with Remotion, in 2D or 3D: explainers, character stories, motion graphics, kinetic type, and animated infographics. Directs the story or explainer, picks a visual style from side-by-side style frames, gets a key-frame board approved, times everything from the voiceover, holds every shot to a finish bar, animates in parallel with sound cued to picture events, and reviews renders by frames and audio measurements. |
| [video-script](skills/video-script/SKILL.md) | Brainstorms short-form video ideas and writes scripts from the creator's own analytics: who has a stake, a hook that lands in 3 seconds, a second sentence that keeps viewers, and proof on screen. Also turns posted-video insights into lessons, with a script that reads retention curves from screenshots. |
| [asset-library](skills/asset-library/SKILL.md) | Keeps one local library of reusable footage, images, music, sound effects, characters, animation code and 3D sets across projects. Agents search it before sourcing or building, register reusable things as versioned bundles as soon as they work, and record which version each delivered cut used. |

Each skill lives in its own directory under `skills/` and can be installed separately.

## The video skills together

video-script writes the script and stops. video-edit makes edits of camera footage;
animated-video makes films drawn in code. The deliverable decides which of the two owns the
final timeline: an edit with animated shots is video-edit's, and animated-video builds the
shots to its brief; an animated film is animated-video's, even with one camera insert.
asset-library is shared by both.

For Roger's personal videos, rojeru-format supplies the format and video-edit owns
the editable timeline. Colorgrade handles dedicated grading. The rojeru B-roll catalog
finds original SSD footage; asset-library records assets actually used in projects.

Every one works alone. Without asset-library, video-edit and animated-video keep a manifest
in the project instead of a shared library, and nothing else changes. Install all four to get
reuse across projects.

## Install

Clone the repository:

```sh
git clone https://github.com/rogeru13/cstack.git
cd cstack
python3 scripts/sync_skills.py --apply
python3 scripts/sync_skills.py --check
```

The sync helper links every `skills/*/SKILL.md` folder into `~/.agents/skills` for
Codex and `~/.claude/skills` for Claude Code. Both point at this checkout, including
scripts and references. It backs up conflicting entries and matching legacy Codex
copies under `~/.local/share/cstack/backups/`; it leaves unrelated skills alone.
The default `--check` is read-only. Start a fresh session after installing new skills.
Do not move the checkout without rerunning the helper.

These are the documented local discovery locations for
[Codex](https://learn.chatgpt.com/docs/build-skills) and
[Claude Code](https://code.claude.com/docs/en/skills). This installs local skills;
cloud sessions need their own repository/plugin setup. Sharing instructions does not
give the two agents identical tools, permissions, or editing judgment.

## Use Roger's editing setup

In either agent, ask:

```text
Use rojeru-format and video-edit on [project/source path]. Follow my stored format,
use the business and avoidant references, search my SSD B-roll catalog, and deliver
an editable Resolve project plus a checked export. Preserve the current grade.
```

For dedicated color work:

```text
Use colorgrade to match this footage to my accepted reference. Verify the input
transform, preserve my existing nodes, and check a short native export first.
```

The personal reference paths and evidence live in `~/.rojeru-format/profile.md`;
the searchable footage inventory lives in `~/.rojeru-format/broll`. These are local
data, not files distributed by this repository. Keep the SSD mounted for actual edits.
The [colorgrade sources](skills/colorgrade/references/sources.md) explain the researched
tools and their limits. Skills guide available tools; they do not replace Resolve,
transcription, fonts, footage, or final visual/audio review.

Use video-script before shooting when you need ideas or a script; video-edit and
rojeru-format after shooting; colorgrade for a look; animated-video for a custom
animated insert; asset-library for reuse. After an edit, use reflect to review concrete
corrections. Use rsi when you want to compare a proposed workflow improvement against
the current version. One agent should write the live Resolve timeline at a time.

## Add a skill of your own

Create `skills/my-skill/SKILL.md` with YAML `name` and `description`, followed by the
instructions. Add scripts only for repeatable operations and references for details.
Give it a realistic failure case, run its helpers, then run the sync command again.
Edit the repository copy once; both agents follow it. Keep private paths, media and
project history in a local profile. The personal rojeru format is an intentional
exception to the upstream skills' general-purpose scope.

To pull upstream improvements, keep `upstream` pointed at goodnight000/cstack, fetch
it, and merge `upstream/main` into a branch. Review changes to shared video defaults,
run relevant checks, and retain this fork's explicit format overrides.

## Use Reflect

Ask your agent:

```text
Use the reflect skill to review this session, including the result and any avoidable effort.
Show me the findings and proposed changes before editing reusable instructions.
```

You can also name other threads and a time window when your agent has access to their history. Reflect does not provide its own history connector.

The review separates consequential findings from changes worth adding to reusable guidance. It can report an inefficiency without recommending another rule. It asks for approval before editing instructions and does not authorize publication, memory changes, or resuming the reviewed task.

## Use RSI

```text
Use the rsi skill to test one improvement to this agent workflow.
Reuse our Reflect findings, compare with the current version, and state a bounded
experiment plan. Keep installed instructions unchanged until I approve adoption.
```

RSI uses the project's existing runners and checks. It can reuse Reflect when installed,
or reconstruct the necessary evidence directly. It adds no background service or test
platform. Give it the task, experiment budget, and adoption scope; it preserves those
bounds across the work. A successful local comparison is evidence for the tested scope,
not proof of unlimited recursive improvement.

## Use Video Edit

```text
Use the video-edit skill to edit the footage in this project.
Start from the latest accepted version and the brief. Preserve complete takes,
use supporting visuals that match the spoken claims, and check the actual export.
```

On first use the skill runs `scripts/preflight.py`, which checks for FFmpeg,
Python 3, and [uv](https://docs.astral.sh/uv/), which runs local transcription
(Phonon on Apple silicon, Whisper elsewhere).
It shows the install command for anything missing and runs it only if you agree.
[DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) (free)
is recommended for a native, editable project; without it the skill renders with
FFmpeg. Browser research and publishing need browser tools and your accounts.

With no brief, the skill asks where the video will be posted, how long it should
be, and whether you want music, sound effects, or a hook headline, then follows
its [default short-form style](skills/video-edit/references/style.md). To keep
your own defaults across updates, put them in `~/.video-edit/profile.md`.

Of the bundled [sound effects](skills/video-edit/assets/sfx/README.md), 33 are
CC0 Freesound recordings; the other 28 are not covered by the MIT license and
their sources and unverified rights status are listed in their catalog.

## Use Animated Video

```text
Use the animated-video skill to turn this script into an animated video.
Confirm the format and show me one style frame before building the full piece.
```

For the best results, run it with Claude Opus 5.5 at high or max effort. Short
unnarrated pieces take one agent and a storyboard; longer narrated films use the
full production with parallel animators and a review panel.

The skill needs a shell, Node.js with Remotion, FFmpeg/ffprobe, and Python 3
with faster-whisper for word timings. Voiceover comes from the user or a
separate tool. Music and effects come from the user's files, on-disk samples
such as the video-edit sound library, or sound synthesized in code. The template holds style-neutral
infrastructure only (timing, camera, still and render scripts, synthesis helpers). Optional
parts from past films (a globe with a cable web, an iPhone running iMessage, synthesised sound
effects) sit beside it to copy and restyle. Characters, art direction, and creative defaults are
designed per project or supplied by you.

For photoreal or physically detailed worlds, the skill reads the references for scale,
materials, light and motion, chooses between three.js in Remotion and an optional
[Blender](https://www.blender.org/) render, and gets one moving test shot accepted before the
full build. For the three.js route it starts from a tested realism kit in `templates/parts/`:
sky and sun with environment lighting and haze, shadows that hold still under a moving camera,
seeded grass, trees and stone, frame-driven wind, and cause-driven weathering. A runnable outdoor
example shot ([examples/realistic-3d](examples/realistic-3d/README.md)) renders at under half a
second per 720p frame and checks that re-rendered frames are identical. It is a detailed 3D
starting point that still reads as CGI, not photographic quality.

Asked by video-edit (or by you) for a single animated or 3D shot inside a camera edit, it skips
the story steps, works to the edit's frames and returns the clip with its sound events.

## Use Asset Library

```text
Use the asset-library skill to set up a library for my video projects.
Before sourcing anything for this edit, search it, and register what we build as soon as it works.
```

The library is one SQLite database plus your files, under one folder you choose, driven by
`scripts/library.py` (Python 3, FFmpeg for probing and previews). There is no server. Media is
versioned by content hash; characters, code and 3D sets are snapshotted as bundles with their
files, dependencies, an example, a preview and a validation command, so a cut recorded with a
version can always find what it used. At delivery the producing skill declares which library
entries the cut selected, and the check fails until each has a use for that cut and version;
whether an asset was worth keeping stays your call. Put the library's location and
your reuse rules in `~/.asset-library/profile.md`.

## Use Video Script

```text
Use the video-script skill to brainstorm ideas for my next video.
Rank them by who has a stake, and give each a hook, a second sentence, and what we'll show.
```

It works best with a library of your past videos and their analytics: one Markdown
file per video plus an index, in the [library format](skills/video-script/references/library.md).
Point the skill at it, and at your voice and pace, in `~/.video-script/profile.md`.
To review a posted video, give it the insights screenshots; it reads the retention
curve with `scripts/retention_curve.py` (Python 3 with Pillow and numpy) and
checks the reading against the app's average watch time.

## Evaluation

Run the new helpers' focused checks with Python 3.9+, FFmpeg/FFprobe on PATH, and
Pillow available for frame/layout tests (use an existing environment or an isolated
virtual environment):

```sh
python3 scripts/test_sync_skills.py
python3 skills/rojeru-format/scripts/test_format.py
python3 skills/rojeru-format/scripts/test_broll_index.py
python3 skills/colorgrade/scripts/test_color_audit.py
```

These exercise protected hook timing, captions, malformed plans, real frame extraction,
audio-only reference rejection, source preservation, catalog resume/offline behavior,
legacy-label boundaries, duplicates, LUT corruption, HDR refusal and shared installs.
They do not prove listening, taste, a live Resolve integration, or a finished video.

[Reflect's evaluation cases](skills/reflect/evals/evals.json) cover feedback, constructive pushback, unnecessary repeat checks, necessary investigation, findings that warrant no instruction changes, and keeping one project's output from becoming a default when it seeds a new skill.

[Animated Video's evaluation cases](skills/animated-video/evals/evals.json) cover locking the format before building, treating a past film as evidence rather than a template, and making an explainer without a reference video.

[RSI's evaluation cases](skills/rsi/evals/evals.json) cover missed skill discovery, exposed final tests, altered graders, authorized local adoption, creative judgment, and unproven improvement of the improvement process.

To assess behavior, give an independent agent `SKILL.md`, a case's request and session evidence, then its feedback at the appropriate point. Keep the case's `checks` hidden until reviewing the response. These are evaluation scenarios, not an automated test suite or a guarantee of future performance.

Run Video Edit's caption-helper check with Python 3:

```sh
python3 skills/video-edit/scripts/test_make_captions.py
```

This checks caption generation, time mapping, raw transcript preservation, and
known warning/error behavior. It does not validate a Resolve installation,
listening quality, visual taste, or an end-to-end video edit on your machine.

Run Asset Library's check, which builds a throwaway library in a temporary folder:

```sh
python3 skills/asset-library/scripts/test_library.py
```

It checks ingest and duplicate detection, bundle versions and their publishing, use recording,
the project check against a cut declaration, and that an older database is backed up and
migrated without losing rows. It says nothing about
whether the assets in your library are any good.

## Icons

[Charade](icons/README.md) is a set of line icons that act out what they mean. Each one plays a short
animation of its own verb when its button or link is hovered or focused: the lock unlocks, the
bell swings, the trash eats a crumb. There are 203 icons in plain SVG and CSS, with no
dependencies. Open `icons/index.html` from a local server to browse them.

## Contributing

Keep each skill self-contained and focused on a recurring need. Include examples or evaluation cases that expose meaningful mistakes. Keep transcripts, credentials, personal project history, and machine-specific paths out of published skills. For third-party contributions, preserve attribution and confirm license compatibility.

Keep general-purpose skills general; personalization lives outside the repo, in each skill's `~/.<skill>/profile.md` and the files it points to. This fork's explicitly personal `rojeru-format` is the exception for Roger's editing contract, while its source media and evidence still stay local. Before changing a general skill, ask whether the change would be right for a stranger making their own videos. If so, write it here generically. If it is right only for you (your audience, taste, numbers, machine or accounts), put it in your profile. When it is both, split it: the general rule here, your value and the evidence behind it in your profile. Bundle only assets whose license allows redistribution, and keep the creator's own footage, likeness and personal media out.

## License

[MIT](LICENSE).
