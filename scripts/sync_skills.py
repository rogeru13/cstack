#!/usr/bin/env python3
"""Link this checkout's skills into Codex and Claude; keep displaced installs as backups."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile


def sync(repo, home, apply=False):
    repo, home = Path(repo).resolve(strict=True), Path(home).expanduser().resolve()
    sources = sorted(p.parent for p in (repo / "skills").glob("*/SKILL.md"))
    if not sources:
        raise ValueError("No skills/*/SKILL.md found in repository")
    destinations = {"codex": home / ".agents/skills", "claude": home / ".claude/skills"}
    backup = None
    rows = []

    def preserve(path, group):
        nonlocal backup
        if backup is None:
            root = home / ".local/share/cstack/backups"
            root.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-")
            backup = Path(tempfile.mkdtemp(prefix=stamp, dir=root))
        target = backup / group / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        path.rename(target)  # Move the entry itself, never its symlink target.

    for source in sources:
        for agent, directory in destinations.items():
            target = directory / source.name
            same = target.is_symlink() and target.resolve() == source.resolve()
            rows.append({"agent": agent, "skill": source.name, "target": str(target), "status": "linked" if same else "needs-link"})
            if apply and not same:
                directory.mkdir(parents=True, exist_ok=True)
                if target.exists() or target.is_symlink():
                    preserve(target, agent)
                try:
                    target.symlink_to(source, target_is_directory=True)
                except OSError:
                    prior = backup / agent / target.name if backup else None
                    if prior and (prior.exists() or prior.is_symlink()):
                        prior.rename(target)
                    raise
        # Retire only matching cstack names from Codex's legacy scan directory.
        # Keeping a second copy there can shadow the shared maintained skill.
        legacy = home / ".codex/skills" / source.name
        if legacy.exists() or legacy.is_symlink():
            rows.append({"agent": "codex-legacy", "skill": source.name, "target": str(legacy), "status": "needs-backup"})
            if apply:
                preserve(legacy, "codex-legacy")
    if apply:
        checked = sync(repo, home, apply=False)
        checked["backup"] = str(backup) if backup else None
        return checked
    return {"in_sync": all(r["status"] == "linked" for r in rows), "skills": len(sources), "entries": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--home", type=Path, default=Path.home(), help="User home; override for a temporary test environment")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Back up conflicts and create shared links")
    mode.add_argument("--check", action="store_true", help="Read-only check (the default)")
    args = parser.parse_args()
    try:
        result = sync(args.repo, args.home, args.apply)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Skill synchronization failed: {exc}\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["in_sync"] else 1)


if __name__ == "__main__":
    main()
