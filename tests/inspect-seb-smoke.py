#!/usr/bin/env python3
"""Regression fixtures for the read-only, fail-closed SEB container inspector."""
import gzip
import importlib.util
import plistlib
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "inspect-seb.py"
spec = importlib.util.spec_from_file_location("inspect_seb", MODULE)
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


def make_plnd(settings):
    xml = plistlib.dumps(settings, fmt=plistlib.FMT_XML)
    return gzip.compress(b"plnd" + gzip.compress(xml))


class InspectSEBTests(unittest.TestCase):
    def test_plain_wrapped_seb_report_never_launchable(self):
        result = inspector.inspect_bytes(make_plnd({
            "startURL": "https://example.invalid/exam",
            "allowQuit": False,
            "unsupportedExtraSetting": True,
        }))
        self.assertEqual(result["status"], "inspect-only")
        self.assertEqual(result["format"], "seb-plnd-gzip-xml")
        self.assertEqual(result["recognized_keys"], ["allowQuit", "startURL"])
        self.assertEqual(result["unrecognized_keys"], ["unsupportedExtraSetting"])
        self.assertFalse(result["launchable"])
        self.assertFalse(result["authenticated"])
        self.assertNotIn("https://", str(result), "report must not reveal URL/config values")

    def test_plain_xml_is_never_launchable(self):
        xml = plistlib.dumps({"startURL": "https://example.invalid/"})
        result = inspector.inspect_bytes(xml)
        self.assertEqual(result["format"], "plain-xml-inspection-only")
        self.assertFalse(result["launchable"])

    def test_encrypted_seb_rejected(self):
        for prefix in (b"pswd", b"pwcc", b"pkhs", b"phsk"):
            with self.subTest(prefix=prefix):
                with self.assertRaisesRegex(inspector.SebInspectionError, "Encrypted configuration"):
                    inspector.inspect_bytes(gzip.compress(prefix + b"secret"))

    def test_invalid_and_unrecognized_rejected(self):
        for data in (b"", b"not a SEB file", gzip.compress(b"NOPEpayload")):
            with self.subTest(data=data[:10]):
                with self.assertRaises(inspector.SebInspectionError):
                    inspector.inspect_bytes(data)

    def test_bomb_rejected(self):
        excessive = b"x" * (inspector.MAX_EXPANDED_BYTES + 1)
        with self.assertRaises(inspector.SebInspectionError):
            inspector.inspect_bytes(gzip.compress(b"plnd" + gzip.compress(excessive)))

    def test_too_large_input_rejected(self):
        with self.assertRaisesRegex(inspector.SebInspectionError, "size limit"):
            inspector.inspect_bytes(b"\x00" * (inspector.MAX_FILE_BYTES + 1))

    def test_nested_plist_not_a_dict_rejected(self):
        with self.assertRaisesRegex(inspector.SebInspectionError, "dictionary"):
            inspector.inspect_bytes(make_plnd(["not", "settings"]))

    def test_actual_file_reading(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "test.seb"
            path.write_bytes(make_plnd({"startURL": "https://example.invalid"}))
            self.assertEqual(inspector.inspect_path(path)["setting_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
