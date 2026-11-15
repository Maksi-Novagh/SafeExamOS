#!/usr/bin/env python3
"""SafeExamOS native Linux SEB policy tests (no display/server required)."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "linux-seb/policy.py"
spec = importlib.util.spec_from_file_location("linux_seb_policy", MODULE)
assert spec and spec.loader
import sys
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

def fixture(**update):
    result = {
        "schema": "safeexamos-linux-seb-lab-v1",
        "title": "Test examination",
        "start_url": "https://exam.example.org/start",
        "allowed_origins": ["https://exam.example.org"],
        "allow_downloads": False,
        "allow_uploads": False,
    }
    result.update(update)
    return result

class PolicyTests(unittest.TestCase):
    def test_explicit_origin_allow_and_default_deny(self):
        p = module.parse_config(fixture())
        self.assertTrue(p.permits("https://exam.example.org/page?q=1"))
        self.assertFalse(p.permits("https://bad.exam.example.org/page"))
        self.assertFalse(p.permits("https://exam.example.org.evil.test"))
        self.assertFalse(p.permits("http://exam.example.org/start"))
        self.assertFalse(p.permits("file:///etc/passwd"))
        self.assertFalse(p.permits("javascript:alert(1)"))
        self.assertFalse(p.permits("https://127.0.0.1/a"))

    def test_untrusted_settings_fail_closed(self):
        for value in [
            fixture(allow_downloads=True),
            fixture(allow_uploads=True),
            fixture(browser_exam_key="fake"),
            fixture(allow_shell=True),
            fixture(allowed_origins=["https://exam.example.org", "http://bad.test"]),
            fixture(start_url="https://other.example.org"),
            fixture(start_url="https://user:password@exam.example.org"),
            fixture(start_url="https://exam.example.org:443/a"),
            fixture(allowed_origins=["https://exam.example.org/path"]),
            fixture(allowed_origins=["https://exam.example.org", "https://exam.example.org"]),
            fixture(allowed_origins=[]),
            fixture(schema="official-seb"),
        ]:
            with self.subTest(value=value):
                with self.assertRaises(module.PolicyError):
                    module.parse_config(value)

    def test_missing_or_oversized_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.json"
            with self.assertRaises(module.PolicyError):
                module.load_config(path)
            path.write_bytes(b"x" * (module.MAX_BYTES + 1))
            with self.assertRaises(module.PolicyError):
                module.load_config(path)
            path.write_text(json.dumps(fixture()), encoding="utf-8")
            self.assertTrue(module.load_config(path).permits("https://exam.example.org/start"))

    def test_native_smoke_is_only_explicit_ci_boot(self):
        app = (ROOT / "linux-seb/app.py").read_text(encoding="utf-8")
        session = (ROOT / "build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session").read_text(encoding="utf-8")
        self.assertIn("SAFEEXAMOS_NATIVE_CI", app)
        self.assertIn("safeexamos.native_ci=1", session)
        self.assertIn("OFFLINE_SMOKE_HTML", app)
        self.assertIn("SAFEEXAMOS_NATIVE_SEB_UI_READY", app)
        self.assertIn("WebKit2.WebContext.new_ephemeral()", app)
        self.assertNotIn("--no-sandbox", app)

    def test_local_addresses_rejected(self):
        for origin in ["https://localhost", "https://127.0.0.1", "https://192.168.0.1",
                       "https://exam.example.org:8443", "http://exam.example.org",
                       "https://exam.example.org.evil.test/path"]:
            with self.subTest(origin=origin), self.assertRaises(module.PolicyError):
                module.validate_origin(origin)

if __name__ == "__main__":
    unittest.main(verbosity=2)
