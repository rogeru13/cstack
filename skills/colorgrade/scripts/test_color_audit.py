"""LUT corruption and real FFmpeg scope checks on synthetic, temporary media."""
from pathlib import Path
import tempfile
import unittest
from PIL import Image
import color_audit as c


class ColorAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def cube(self, contents):
        p = self.base / "test.cube"
        p.write_text(contents)
        return p

    def test_cube_identity_and_intentional_extended_range(self):
        p = self.cube('TITLE "test"\nLUT_1D_SIZE 2\n0 0 0\n1.2 1 1 # extended range\n')
        result = c.audit_cube(p)
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["rows_outside_unit_interval"], 1)
        self.assertEqual(len(result["sha256"]), 64)

    def test_cube_corruption_is_rejected(self):
        for body in ("LUT_3D_SIZE 2\n0 0 0\n", "LUT_1D_SIZE 2\n0 0 0\nnan 1 1\n",
                     "LUT_1D_SIZE 2\nDOMAIN_MIN 1 0 0\n0 0 0\n1 1 1\n",
                     "LUT_1D_SIZE 2\nLUT_3D_SIZE 2\n0 0 0\n1 1 1\n"):
            with self.subTest(body=body), self.assertRaises(ValueError):
                c.audit_cube(self.cube(body))

    def make_video(self, transfer="bt709"):
        p = self.base / f"{transfer}.mp4"
        c.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=24",
               "-t", "1", "-vf", f"setparams=color_primaries=bt709:color_trc={transfer}:colorspace=bt709",
               "-c:v", "libx264", "-threads", "2", "-pix_fmt", "yuv420p",
               "-color_primaries", "bt709", "-color_trc", transfer, "-colorspace", "bt709", str(p)])
        return p

    def test_real_scopes_preserve_source_and_evidence(self):
        source = self.make_video()
        before = source.read_bytes()
        dest = self.base / "scopes"
        with self.assertRaises(ValueError):
            c.scopes(source, dest, [0.25])
        self.assertFalse(dest.exists())
        report = c.scopes(source, dest, [0.25], True)
        self.assertEqual(len(report["samples"]), 1)
        with Image.open(dest / "00-rgb-parade.png") as im:
            self.assertEqual(im.size, (960, 320))
        self.assertTrue((dest / "00-vectorscope.png").is_file())
        with self.assertRaises(FileExistsError):
            c.scopes(source, dest, [0.25], True)
        self.assertEqual(before, source.read_bytes())

    def test_hdr_refuses_false_sdr_confirmation(self):
        source = self.make_video("smpte2084")
        self.assertEqual(c.probe(source)["video"].get("color_transfer"), "smpte2084")
        dest = self.base / "wrong"
        with self.assertRaises(ValueError):
            c.scopes(source, dest, [0.25], True)
        self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
