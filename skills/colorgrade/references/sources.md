# Sources and optional tools

Reviewed 2026-10-13. These are primary references and optional implementations, not
dependencies to install automatically. No third-party implementation is vendored here.

| Source | Useful for | Boundary |
| --- | --- | --- |
| [Blackmagic Color](https://www.blackmagicdesign.com/products/davinciresolve/color) and [training](https://www.blackmagicdesign.com/products/davinciresolve/training) | Native grading, matching, scopes, color management | Use the installed manual/API for version-specific operations. |
| [colour-science/colour](https://github.com/colour-science/colour) | Color-space math, color differences and LUT I/O | Scientific tools do not infer an unknown camera profile or judge a creative look. |
| [OpenColorIO](https://github.com/AcademySoftwareFoundation/OpenColorIO) | Explicit color transforms and reproducible viewing pipelines | Requires the correct config, input, display and view; not a universal film look. |
| [baldavenger/DCTLs](https://github.com/baldavenger/DCTLs) | Study of DCTL technical transforms and grading utilities | GPL-3.0; do not copy into this MIT tree without handling licensing. Check edition and GPU compatibility. |
| [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp) | Example Resolve automation integration | Verify the connected fork/version and real API behavior; tool names alone do not establish working controls. |
| [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) | Waveform, vectorscope, LUT processing and diagnostics | Explicit transforms and signal interpretation still belong to the operator. |

Prefer native Resolve operations for an editable project. Add Colour or OCIO only when
a specific conversion/validation requires it. Use a documented camera-vendor transform
before writing one from scratch. Research/ML reference-transfer repositories can suggest
candidate looks, but require temporal, gamut and skin checks before production use.
