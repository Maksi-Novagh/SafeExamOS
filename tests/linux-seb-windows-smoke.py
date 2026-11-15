#!/usr/bin/env python3
"""Fail-closed multiwindow and compositor fixture checks (no GUI required)."""
import importlib.util
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "linux-seb"
for name, file in [("linux_seb_policy", "policy.py"), ("linux_seb_windows", "windows.py")]:
    spec = importlib.util.spec_from_file_location(name, BASE / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

from linux_seb_policy import PolicyError, parse_config
from linux_seb_windows import ManagedWindows, WindowPolicyError

def fixture(**values):
    data = {
        "schema": "safeexamos-linux-seb-lab-v1",
        "title": "Window management fixture",
        "start_url": "https://exam.example.org/entry",
        "allowed_origins": ["https://exam.example.org"],
    }
    data.update(values)
    return data

class ManagedWindowTests(unittest.TestCase):
    def test_default_is_one_window_only(self):
        policy = parse_config(fixture())
        windows = ManagedWindows(policy)
        main = windows.open_main()
        self.assertEqual(main.role, "main")
        with self.assertRaises(WindowPolicyError):
            windows.open_child(main.window_id, policy.start_url)
        with self.assertRaises(WindowPolicyError):
            windows.close(main.window_id)

    def test_approved_children_and_capacity(self):
        policy = parse_config(fixture(max_browser_windows=3, allow_secondary_windows=True))
        m = ManagedWindows(policy)
        primary = m.open_main()
        first = m.open_child(primary.window_id, "https://exam.example.org/resource")
        second = m.open_child(primary.window_id, "https://exam.example.org/resource2")
        self.assertEqual(len(m.records), 3)
        with self.assertRaises(WindowPolicyError):
            m.open_child(primary.window_id, "https://exam.example.org/new")
        with self.assertRaises(WindowPolicyError):
            m.open_child(primary.window_id, "https://evil.example.org/new")
        self.assertTrue(m.close(first.window_id))
        self.assertEqual(len(m.records), 2)
        self.assertFalse(m.close(999))
        m.clear()
        self.assertEqual(len(m.records), 0)

    def test_mismatched_multiwindow_fields_fail(self):
        bad = [
            fixture(max_browser_windows=2),
            fixture(allow_secondary_windows=True),
            fixture(max_browser_windows=True),
            fixture(max_browser_windows=0),
            fixture(max_browser_windows=4, allow_secondary_windows=True),
            fixture(allow_secondary_windows="true", max_browser_windows=2),
        ]
        for config in bad:
            with self.subTest(config=config), self.assertRaises(PolicyError):
                parse_config(config)

    def test_no_arbitrary_program_spawn_or_desktop_launcher(self):
        config_path = ROOT / "build/amd64/config/includes.chroot/etc/safeexamos/labwc/rc.xml"
        root = ET.parse(config_path).getroot()
        self.assertEqual(root.tag, "labwc_config")
        actions = {x.get("name") for x in root.findall(".//action")}
        for forbidden in ("Execute", "Close", "ShowMenu", "Exit", "GoToDesktop"):
            self.assertNotIn(forbidden, actions)
        self.assertFalse(root.findall(".//default"))
        self.assertLessEqual(len(root.findall("./desktops/name")), 1)
        app = (BASE / "app.py").read_text()
        self.assertIn("def _new_window", app)
        self.assertIn("manager.open_child", app)
        self.assertNotIn("subprocess.Popen", app)

if __name__ == "__main__":
    unittest.main(verbosity=2)
