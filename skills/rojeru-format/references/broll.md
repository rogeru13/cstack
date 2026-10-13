# Local B-roll workflow

The profile points to the catalog; the default is `~/.rojeru-format/broll`.
Python 3.9+ and FFprobe suffice for indexing and search. The catalog stays on the
computer, outside the source roots. Original media stays on the SSD.

```sh
python3 SKILL_DIR/scripts/broll_index.py search "waterfall" --min-duration 3 --reviewed-only
python3 SKILL_DIR/scripts/broll_index.py search "laptops" --min-duration 3
python3 SKILL_DIR/scripts/broll_index.py show ASSET_ID
python3 SKILL_DIR/scripts/broll_index.py scan --import-legacy --verify-duplicates
```

On another machine, configure explicit sources once:

```sh
python3 SKILL_DIR/scripts/broll_index.py scan \
  --root 'cinematic=/path/to/cinematic_shots' --root 'friends=/path/to/friends'
```

Use the same aliases if the drive mount changes. Repeat scans retain stable IDs,
probe only changed/new/failed media, and mark missing roots offline without erasing
their entries. Search rechecks file existence. `--include-offline` reveals retained
offline records; these cannot be placed until reconnected. `--deduplicate` suppresses
only full-hash-proven duplicates, never merely similar clips. Cache/hidden/support
files remain inventoried but are excluded from media search.

Search by what the sentence needs: setting, visible action, object, emotion supported
by the shot, or scene. Results distinguish fresh visual evidence from imported
`legacy_unverified` hints. `--reviewed-only` excludes semantic matches based solely
on legacy labels, but a path match still isn't visual proof of the query. Read each
annotation's description, timestamps and evidence.

`--min-duration 3` checks total source duration, **not a usable reviewed interval**.
Sampled frames establish visible contents at those timestamps, not camera movement,
continuous action, clean handles, or a good 4:3 crop. Review the candidate interval in
context, inspect its opening/middle/end crop, and record source in/out frames. The hook
needs an unbroken insert lasting through the two-second pause and into resumed speech.

Add grounded search annotations after inspecting the evidence:

```sh
python3 SKILL_DIR/scripts/broll_index.py annotate ASSET_ID \
  --tags 'waterfall,river,trees' --description 'Wide waterfall with trees on both banks' \
  --start 1 --end 4 --evidence /local/review/contact-sheet.jpg
```

This records sampled review coverage; keep guaranteed usable source intervals and crop
decisions in the project visual manifest. Leave motion unreviewed unless playback
supports it and provide `--motion-evidence` when adding a motion claim. Do not infer
people's identities or relationships merely from the directory or appearance.

Treat this catalog as source discovery. When using asset-library for a finished edit,
register the actually selected files and their provenance there; retain this catalog
ID in the visual manifest. Avoid importing every cache file into the project library.
