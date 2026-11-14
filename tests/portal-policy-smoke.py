#!/usr/bin/env python3
"""Test restrictive school portal configurations before ISO builds."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("render_portals", ROOT / "scripts/render-portals.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PortalPolicyTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "config/portals.json").read_text())
        self.policy = json.loads((ROOT / "build/amd64/config/includes.chroot/etc/chromium/policies/managed/safeexamos.json").read_text())

    def test_outputs_are_current(self):
        policy, catalog = mod.build_outputs(self.config, self.policy)
        self.assertEqual(policy, mod.POLICY.read_text())
        self.assertEqual(catalog, mod.CATALOG.read_text())
        self.assertIn("https://smartschool.be", self.policy["URLAllowlist"])
        self.assertIn("http://*", self.policy["URLBlocklist"])
        self.assertIn("https://*", self.policy["URLBlocklist"])

    def test_fixed_exam_portal_is_admin_controlled(self):
        config = {
            "schema_version": 1,
            "identity_origins": [],
            "portals": [{"id": "exam", "label": "Exam", "kind": "fixed",
                        "start_url": "https://exams.example.edu/entry"}]
        }
        portals, origins = mod.validate(config)
        self.assertEqual(portals[0]["start_url"], "https://exams.example.edu/entry")
        self.assertEqual(origins, ["https://exams.example.edu"])

    def test_rejects_arbitrary_url_payloads(self):
        for uri in ("http://example.org/", "javascript:alert(1)", "https://user:password@example.org",
                    "https://example.org:8443", "https://example.org/path#fragment",
                    "https://example.org/a/../b", "https://example.org/evil\n"):
            with self.subTest(uri=uri):
                with self.assertRaises(ValueError):
                    mod.safe_url(uri)

    def test_rejects_unapproved_keys(self):
        config = dict(self.config)
        config["allow_any_url"] = True
        with self.assertRaises(ValueError):
            mod.validate(config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
