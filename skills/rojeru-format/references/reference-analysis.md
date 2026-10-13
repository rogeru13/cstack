# Learn from a reference without guessing

Use user-named examples first. Prefer the final local movie plus its native Resolve
timeline, source footage, caption sidecar and edit notes when available. Confirm the
file identity from its folder, metadata and picture; do not confuse an agent preview,
an earlier trial, and a final exported after a manual grade change.

Create a local evidence folder, outside the public repository. The helper requires
FFmpeg/ffprobe and Pillow; use an existing Python environment with Pillow or an agreed
isolated environment. It never changes or uploads the source:

```sh
python3 SKILL_DIR/scripts/inspect_reference.py VIDEO --output NEW_EVIDENCE_FOLDER
python3 SKILL_DIR/scripts/inspect_reference.py VIDEO --times 0.1,1,2,3,4,5,6 \
  --output NEW_HOOK_EVIDENCE_FOLDER
```

Inspect the emitted contact sheet and individual frames. Sample densely around the
first sentence's end, title entry, speech return, B-roll cuts, and caption changes.
Use frame-by-frame playback or consecutive frames to establish motion. Waveform/ASR
and listening establish spoken timing; a still alone does not. Use the local transcript
tool if a transcript is missing. Record when listening/playback is unavailable.

Keep an evidence table: file/version, observed time range, property, measurement,
confidence, and evidence method. Separate **user requirement**, **observed behavior**,
**project-specific choice**, and **unverified hypothesis**. A font identity or exact
color from a compressed movie is tentative without the native settings. An export's
darkness does not prove a particular LUT or exposure value.

Compare at least the chosen examples before promoting an observed trait to a default.
Explicit user instructions already qualify; they do not need statistical confirmation.
If an older reference differs from the current instructions, preserve the current
instructions and note the difference. Do not copy footage, licensed music, LUTs or
private paths into the public skill.

Finish with a measured reference map and one short representative treatment when an
edit is requested. Use the user's feedback to update the accepted-reference registry.
A contact sheet or a successful render does not establish acceptance.
