"""Check failure cases that would otherwise produce a visibly wrong rojeru edit."""
import copy
import json
from pathlib import Path
import re
import tempfile
import unittest
from PIL import Image
import inspect_reference as ref
from validate_plan import validate


class PlanTests(unittest.TestCase):
    def setUp(self):
        doc = (Path(__file__).resolve().parents[1] / "references/edit-plan.md").read_text()
        self.plan = json.loads(re.search(r"```json\n(.*?)\n```", doc, re.S)[1])

    def test_documented_plan_and_title_hold(self):
        self.assertTrue(validate(self.plan)["valid"])
        self.assertGreater(self.plan["title"]["end_frame"], self.plan["body_start_frame"])
        self.plan["title"]["end_frame"] = self.plan["body_start_frame"] - 1
        self.assertFalse(validate(self.plan)["valid"])

    def test_protected_pause_and_broll_overlap(self):
        for mutate in (
            lambda p: p.update(body_start_frame=119),
            lambda p: p["dialogue"].append({"start_frame": 80, "end_frame": 90}),
            lambda p: p["broll"][0].update(end_frame=120),
            lambda p: p["broll"][1].update(start_frame=144),
        ):
            p = copy.deepcopy(self.plan); mutate(p)
            self.assertFalse(validate(p)["valid"])

    def test_exact_caption_contract(self):
        changes = [lambda p: p.update(width=1920),
                   lambda p: p["title"].update(name="rojeru_"),
                   lambda p: p["title"].update(font="Helvetica"),
                   lambda p: p["title"].update(text="a fresh start"),
                   lambda p: p["captions"][0].update(color="#FFFF00"),
                   lambda p: p["captions"][1].update(font="Helvetica"),
                   lambda p: p["captions"][0].update(lines=["i tried", "something new"]),
                   lambda p: p["captions"][0].update(lines=["i tried\nsomething new"]),
                   lambda p: p["captions"][0].update(lines=["i tried something new and found hope."]),
                   lambda p: p["captions"][0].update(lines=["I tried something new"]),
                   lambda p: p["captions"][1].update(lines=["found hope."]),
                   lambda p: p["captions"][2].update(color="#FFE32D"),
                   lambda p: p["dialogue"][0].update(volume_db=20),
                   lambda p: p["dialogue"][1].update(start_frame=121)]
        for mutate in changes:
            p = copy.deepcopy(self.plan); mutate(p)
            self.assertFalse(validate(p)["valid"], p)

    def test_broll_identity_and_gap_edges(self):
        for key in ("asset_id", "source_id", "source_hash"):
            p = copy.deepcopy(self.plan)
            p["broll"][0][key] = p["broll"][1][key] = "same-source"
            self.assertFalse(validate(p)["valid"])
        p = copy.deepcopy(self.plan)
        p["rejected_source_ids"] = [p["broll"][0]["source_id"]]
        self.assertFalse(validate(p)["valid"])
        for gap in (0, 47, 73):
            p = copy.deepcopy(self.plan)
            p["broll"][1]["start_frame"] = 144 + gap
            self.assertFalse(validate(p)["valid"])
        for gap in (48, 72):
            p = copy.deepcopy(self.plan)
            p["broll"][1]["start_frame"] = 144 + gap
            self.assertTrue(validate(p)["valid"])
        # No forced insert at the end of a video.
        p = copy.deepcopy(self.plan); p["broll"].pop()
        self.assertTrue(validate(p)["valid"])

    def test_case_and_chunk_coverage(self):
        p = copy.deepcopy(self.plan)
        p["sentences"]["s1"] = "Jesus gave me hope and found hope."
        p["captions"][0]["lines"] = ["Jesus gave me hope"]
        self.assertTrue(validate(p)["valid"])
        # Full-sentence cue is allowed when it fits six words on one line.
        self.assertEqual(len(p["captions"][2]["lines"]), 1)
        p["captions"][1]["lines"] = ["and lost hope."]
        self.assertFalse(validate(p)["valid"])

    def test_malformed_input_returns_errors(self):
        for p in (None, {}, [], {**self.plan, "fps": "0"}, {**self.plan, "title": []}, {**self.plan, "captions": [42]}):
            self.assertFalse(validate(p)["valid"])


class ReferenceTests(unittest.TestCase):
    def test_real_frames_and_audio_only_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            video, audio = base / "movie.mp4", base / "audio.mp4"
            ref.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=24",
                     "-t", "1", "-c:v", "libx264", "-threads", "2", str(video)])
            before = video.read_bytes()
            report = ref.inspect(video, base / "evidence", times=[0, 0.5], width=160)
            self.assertEqual(len(report["frames"]), 2)
            with Image.open(base / "evidence/contact-sheet.jpg") as im:
                self.assertEqual(im.width, 320)
            with self.assertRaises(FileExistsError):
                ref.inspect(video, base / "evidence", times=[0])
            with self.assertRaises(ValueError):
                ref.inspect(video, base / "invalid", times=[1])
            self.assertEqual(before, video.read_bytes())
            ref.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-c:a", "aac", str(audio)])
            with self.assertRaisesRegex(ValueError, "No video stream"):
                ref.inspect(audio, base / "audio-evidence")
            self.assertFalse((base / "audio-evidence").exists())


if __name__ == "__main__":
    unittest.main()
