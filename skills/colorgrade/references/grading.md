# Grading decisions

## Input, working space, and output

Read the live settings rather than replacing them with a universal template. In an
RCM workflow, verify the input assignment per clip, timeline working space and output
transform. In an explicit CST workflow, account for the input and output CSTs exactly
once. In ACES, verify the input and output transforms and the working encoding.
Avoid mixing these architectures accidentally. A working gamut/transfer and an output
display gamut/transfer are distinct choices.

For camera originals, inspect sidecars/recording evidence before assigning an input.
For a previously graded export, treat the look as baked unless proven otherwise.
A technical camera LUT, a creative scene-referred LUT, and a display-referred LUT have
different expected inputs; record each LUT's expected input and output. Missing input
documentation is a reason to test, not a reason to assume that every `.cube` is Rec.709.

For HLG/PQ to SDR, use a known color-managed conversion with an explicit target and
tone/gamut mapping. Preserve an HDR deliverable when requested. Do not fix HDR previews
with brightness or saturation sliders. Color-range mistakes can resemble crushed
blacks or washed-out footage; inspect levels before correcting exposure.

## Correction versus creative look

An adaptable explicit-node concept is input normalization → exposure/WB → shot match
→ contrast/look → selective work → finish → output transform. The live color pipeline
determines where these operations belong; it is not a mandatory node count.
Noise reduction and texture placement depend on the effect and source. Preserve the
existing order unless a tested change fixes a demonstrated problem.

Balance neutral objects only when they are actually neutral and similarly lit. Match
the same person/scene before comparing overall histograms. Skin hue can vary under
intentional colored light; protect natural hue relationships without removing the set's
lighting. Avoid universal skin IRE numbers or a fixed saturation boost.

For a reference match, compare skin, neutral surfaces, shadows, highlights, and dominant
colors separately. Note what cannot be reproduced from the source lighting, exposure,
or lens. A reference LUT cannot recover clipped highlights or absent color information.
Keep a creative comparison to a small number of meaningfully different treatments.

## Export diagnosis

Compare corresponding frames, not nearby expressions or different lighting. View both
with the same display transform, dimensions, and surround. Check stream primaries,
transfer, matrix, range, bit depth, and intended codec. Inspect decoded pixel behavior
as well as tags. A `bt709` transfer tag alone does not document the whole mastering setup.

If Resolve, QuickTime, and a browser differ, check color management, display settings,
and file tags before baking a compensating gamma change. Rec.709-A is not a blanket
fix for every Mac export. Check the actual delivery path where possible and say when
the display has not been calibrated. Do not promise calibrated accuracy from screenshots.

Check grain and halation in motion and at the final compression quality. Watch for
NR trails, mask chatter, plastic skin, clipped colored channels, gradient banding,
or changes in exposure/WB across a cut. A still or a LUT integrity check cannot pass
these temporal checks.
