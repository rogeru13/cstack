"""Exercise migration against temporary homes; never modify real installations."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from sync_skills import sync


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.repo, self.home = self.base / "repo", self.base / "home"
        self.source = self.repo / "skills/example"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("one maintained copy")

    def tearDown(self):
        self.tmp.cleanup()

    def test_migration_preserves_custom_and_unrelated_files(self):
        legacy = self.home / ".codex/skills/example"
        legacy.mkdir(parents=True)
        (legacy / "custom.txt").write_text("preserve me")
        other = legacy.parent / "unrelated"
        other.mkdir()
        (other / "SKILL.md").write_text("unrelated")
        before = set(self.base.rglob("*"))
        self.assertFalse(sync(self.repo, self.home)["in_sync"])
        self.assertEqual(before, set(self.base.rglob("*")))
        result = sync(self.repo, self.home, True)
        self.assertTrue(result["in_sync"])
        self.assertEqual((Path(result["backup"]) / "codex-legacy/example/custom.txt").read_text(), "preserve me")
        self.assertFalse(legacy.exists())
        for d in (".agents", ".claude"):
            self.assertEqual((self.home / d / "skills/example").resolve(), self.source.resolve())
        self.assertTrue((other / "SKILL.md").exists())
        self.assertIsNone(sync(self.repo, self.home, True)["backup"])
        (self.source / "SKILL.md").write_text("updated once")
        for d in (".agents", ".claude"):
            self.assertEqual((self.home / d / "skills/example/SKILL.md").read_text(), "updated once")

    def test_broken_link_is_preserved_without_following_target(self):
        target = self.home / ".claude/skills/example"
        target.parent.mkdir(parents=True)
        target.symlink_to(self.base / "missing")
        result = sync(self.repo, self.home, True)
        prior = Path(result["backup"]) / "claude/example"
        self.assertTrue(prior.is_symlink())
        self.assertEqual(prior.readlink(), self.base / "missing")
        self.assertEqual(target.resolve(), self.source.resolve())

    def test_failed_link_restores_displaced_folder(self):
        target = self.home / ".agents/skills/example"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("custom")
        with patch.object(Path, "symlink_to", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                sync(self.repo, self.home, True)
        self.assertEqual((target / "SKILL.md").read_text(), "custom")


if __name__ == "__main__":
    unittest.main()
