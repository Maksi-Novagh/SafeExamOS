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

    def test_child_cannot_spawn_grandchildren_or_use_boolean_parent(self):
        policy = parse_config(fixture(max_browser_windows=3, allow_secondary_windows=True))
        windows = ManagedWindows(policy)
        main = windows.open_main()
        child = windows.open_child(main.window_id, "https://exam.example.org/resource")
        for parent in (child.window_id, True, False, 999):
            with self.subTest(parent=parent), self.assertRaises(WindowPolicyError):
                windows.open_child(parent, "https://exam.example.org/next")
        self.assertEqual(len(windows.records), 2)
        self.assertTrue(windows.close(child.window_id))
        reopened = windows.open_child(main.window_id, "https://exam.example.org/resource")
        self.assertGreater(reopened.window_id, child.window_id)
        self.assertEqual(reopened.parent_id, main.window_id)

    def test_packaged_window_policy_matches_source(self):
        packaged = (ROOT / "build/amd64/config/includes.chroot/usr/local/bin/linux_seb_windows.py").read_bytes()
        source = (BASE / "windows.py").read_bytes()
        self.assertEqual(packaged, source, "ISO window policy must not drift from tested source")

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

    def test_two_window_ci_fixture_is_explicit_and_offline(self):
        app = (BASE / "app.py").read_text(encoding="utf-8")
        session = (ROOT / "build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session").read_text(encoding="utf-8")
        observer = (ROOT / "build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-ci-ui-marker").read_text(encoding="utf-8")
        runner = (ROOT / "scripts/qemu-native-seb-smoke.sh").read_text(encoding="utf-8")
        self.assertIn("--smoke-ui --smoke-windows", session)
        self.assertIn("safeexamos.windows_ci=1", session)
        self.assertIn("SAFEEXAMOS_NATIVE_SEB_CHILD_READY", app)
        self.assertIn("SAFEEXAMOS_CI_MANAGED_WINDOWS_OK", observer)
        self.assertIn("--managed-child", runner)
        self.assertIn("WebKit2.WebView.new_with_related_view", app)
        self.assertIn("OFFLINE_CHILD_HTML", app)
        self.assertIn('smoke_windows and not args.smoke_ui', app)
        self.assertIn("max_browser_windows=2", app)
        self.assertNotIn("subprocess.Popen", app)
        config = fixture()
        self.assertNotIn("allow_secondary_windows", config)
        self.assertFalse(parse_config(config).allow_secondary_windows)

    def test_real_webkit_popup_fixture_is_ci_only(self):
        app = (BASE / "app.py").read_text(encoding="utf-8")
        session = (ROOT / "build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session").read_text(encoding="utf-8")
        marker = (ROOT / "build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-ci-ui-marker").read_text(encoding="utf-8")
        runner = (ROOT / "scripts/qemu-native-seb-smoke.sh").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("window.open('about:blank'", app)
        self.assertIn("window.open('https://blocked.invalid/exam'", app)
        self.assertIn("SAFEEXAMOS_NATIVE_SEB_POPUP_CREATE", app)
        self.assertIn("SAFEEXAMOS_NATIVE_SEB_POPUP_DENIED", app)
        self.assertIn("set_javascript_can_open_windows_automatically(bool(smoke_popups))", app)
        self.assertIn("if args.smoke_popups and not (args.smoke_ui and args.smoke_windows)", app)
        self.assertIn("safeexamos.popups_ci=1", session)
        self.assertIn("--smoke-windows --smoke-popups", session)
        self.assertIn("SAFEEXAMOS_CI_WEBKIT_POPUPS_OK", marker)
        self.assertIn("safeexamos.popups_ci=1", runner)
        self.assertIn("qemu-webkit-popups:", workflow)
        # No user-provided exam profile may silently enable popups.
        self.assertFalse(parse_config(fixture()).allow_secondary_windows)

    def test_native_webkit_crash_and_close_are_fail_closed(self):
        app = (BASE / "app.py").read_text(encoding="utf-8")
        packaged = (ROOT / "build/amd64/config/includes.chroot/usr/local/bin/safeexamos-linux-seb").read_text(encoding="utf-8")
        self.assertEqual(app, packaged)
        self.assertIn('view.connect("web-process-terminated", self._renderer_terminated, record.window_id)', app)
        self.assertIn('child.connect("destroy", lambda *_: self._close_child(view, record.window_id))', app)
        self.assertIn('if not manager.close(window_id):', app)
        self.assertIn('renderer_failed["value"] = True', app)
        self.assertIn('return 2 if renderer_failed["value"] else 0', app)

    def test_secondary_close_is_idempotent(self):
        p = parse_config(fixture(max_browser_windows=2, allow_secondary_windows=True))
        registry = ManagedWindows(p)
        main = registry.open_main()
        child = registry.open_child(main.window_id, "https://exam.example.org/doc")
        self.assertTrue(registry.close(child.window_id))
        self.assertFalse(registry.close(child.window_id))
        self.assertEqual(list(registry.records), [main.window_id])

    def test_supervised_lab_is_explicit_and_packaged(self):
        app = (BASE / "app.py").read_text(encoding="utf-8")
        packaged = (ROOT / "build/amd64/config/includes.chroot/usr/local/bin/safeexamos-linux-seb").read_text(encoding="utf-8")
        self.assertEqual(app, packaged)
        self.assertIn("--supervised-lab", app)
        self.assertIn("SAFEEXAMOS_NATIVE_SUPERVISOR_LAB", app)
        self.assertIn("End experimental lab session", app)
        self.assertIn('self.web.load_html(OFFLINE_SMOKE_HTML, "about:blank")', app)
        self.assertIn("safeexamos.native_supervisor_lab=1", (ROOT / "build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session").read_text())

    def test_native_handoff_ci_is_explicit(self):
        app = (BASE / "app.py").read_text(encoding="utf-8")
        session = (ROOT / "build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session").read_text()
        marker = (ROOT / "build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-ci-ui-marker").read_text()
        self.assertIn("SAFEEXAMOS_NATIVE_HANDOFF_CI_READY", app)
        self.assertIn("safeexamos.native_handoff_ci=1", session)
        self.assertIn("SAFEEXAMOS_CI_NATIVE_HANDOFF_OK", marker)

    def test_cross_uid_wayland_probe_is_opt_in_and_checks_both_sides(self):
        probe = (ROOT / "build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-wayland-acl-probe").read_text()
        observer = (ROOT / "build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-ci-ui-marker").read_text()
        session = (ROOT / "build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session").read_text()
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn('attempt(path, "exam") and not attempt(path, "nobody")', probe)
        self.assertIn('stat.S_IMODE(root_stat.st_mode) != 0o700', probe)
        self.assertIn('SAFEEXAMOS_CI_WAYLAND_ACL_OK', observer)
        self.assertIn('safeexamos.wayland_acl_ci=1', session)
        self.assertIn('qemu-wayland-acl:', workflow)

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
