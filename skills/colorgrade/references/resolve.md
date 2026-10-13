# Resolve execution

Discover the connected Resolve tool/CLI and read its live schemas. If unavailable,
use the installed scripting API via a supported host or the native application UI.
Follow video-edit's Resolve setup when installed. Do not claim an external scripting
connection until it returns the actual running project; edition/version support varies.

Before mutation record project name, timeline name/ID, clip source/ID and frame range,
current local/remote grade version, color-management settings, and node labels/LUTs.
Save the project and a recovery artifact. Target explicit clips; do not apply to whatever
happens to be selected. Maintain one writer to the live timeline.

The installed Resolve scripting README is the API authority. On macOS it is normally:
`/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.txt`.
Resolve 21's documented operations inspected for this skill include:

- `TimelineItem.GetNodeGraph(layerIdx)`; inspect every relevant stack layer.
- `Graph.GetNumNodes()`, `Graph.GetNodeLabel(nodeIndex)`, `Graph.GetLUT(nodeIndex)`.
- `Graph.SetLUT(nodeIndex, lutPath)`; indices are **1-based**. Verify the node and path.
- `TimelineItem.SetCDL(...)` with `NodeIndex`, `Slope`, `Offset`, `Power`, `Saturation`.
  CDL slope/offset/power are not interchangeable with arbitrary Resolve wheel controls.
- `Graph.ApplyGradeFromDRX(path, gradeMode)`; mode 0 has no keyframes, 1 aligns by source
  timecode, 2 by start frame. Applying a DRX can replace a node structure; preserve it first.
- Local/remote version methods and `CopyGrades(...)`; understand their scope before use.

Check method availability and signatures in the user's installed version. Do not call
`SetProperty('Lift', ...)` because a wrapper advertises primary grading; inspect the
implementation and its capability report. Some wrappers offer approximations or unsupported
operations. If a control is unavailable, use the UI, a compatible DRX/LUT, or report the
specific limitation. Validate the resulting picture and persisted state after the call.

Preserve user-added nodes even when project generation scripts contain an older grade.
Do not rebuild the camera layer merely to update captions, framing, or sound. Shared
nodes, remote grades, group and timeline nodes may affect multiple clips. Make a local
isolated version before experiments, and record exactly what is shared versus local.

Save and re-render from the actual current timeline. A preview generated before manual
changes is not the source of truth. Keep a before/after frame and a native recovery
artifact; a still-image comparison does not prove all keyframes or plugin parameters.
