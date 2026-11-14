#!/usr/bin/env python3
"""Supervised portal/demo mode fixture, using only a local HTTP test server."""
import http.client
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "build/amd64/config/includes.chroot/usr/local/bin/safeexamos-browser-supervisor"
spec = importlib.util.spec_from_loader("safeexam_supervisor", SourceFileLoader("safeexam_supervisor", str(BINARY)))
sup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sup)

class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        (self.path / "index.html").write_text(
            '<meta name="safeexamos-transition-token" content="__SAFEEXAMOS_TRANSITION_TOKEN__">')
        (self.path / "demo.html").write_text(
            '<meta name="safeexamos-transition-token" content="__SAFEEXAMOS_TRANSITION_TOKEN__">')
        (self.path / "transition.js").write_text('/* fixture */')
        self.controller = sup.Controller()
        self.server = sup.LocalAppServer((sup.HOST, 0), self.path, self.controller)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temp.cleanup()

    def query(self, method, path, data=None, extra_headers=None):
        headers = {"Host": f"{sup.HOST}:{sup.PORT}"}
        if extra_headers:
            headers.update(extra_headers)
        conn = http.client.HTTPConnection(sup.HOST, self.server.server_port, timeout=4)
        conn.request(method, path, data, headers)
        response = conn.getresponse()
        result = response.status, response.read(), response.getheader("Cache-Control")
        conn.close()
        return result

    def transition(self, action, token=None, origin=None):
        data = json.dumps({"action": action}).encode()
        headers = {"Content-Type": "application/json", "Origin": origin or sup.ORIGIN,
                   "X-SafeExamOS-Token": token or self.controller.token}
        return self.query("POST", "/api/transition", data, headers)[0]

    def test_browser_profiles_do_not_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            portal = sup.browser_arguments("portal", path)
            demo = sup.browser_arguments("demo", path)
            self.assertIn("--app=http://127.0.0.1:38652/launcher/index.html", portal)
            self.assertIn("--app=http://127.0.0.1:38652/launcher/demo.html", demo)
            self.assertIn(f"--user-data-dir={path}/profiles/portal", portal)
            self.assertIn(f"--user-data-dir={path}/profiles/demo", demo)
            self.assertNotIn("--no-sandbox", portal + demo)
            self.assertNotIn("--remote-debugging-port=9222", portal + demo)

    def test_authored_pages_only_in_their_mode(self):
        code, page, cache = self.query("GET", "/launcher/index.html")
        self.assertEqual(code, 200)
        self.assertIn(self.controller.token.encode(), page)
        self.assertNotIn(b"__SAFEEXAMOS_TRANSITION_TOKEN__", page)
        self.assertEqual(cache, "no-store")
        self.assertEqual(self.query("GET", "/launcher/demo.html")[0], 404)
        self.assertEqual(self.query("GET", "/launcher/../../etc/passwd")[0], 404)
        self.assertEqual(self.query("GET", "/api/status")[0], 200)

    def test_external_origins_cannot_trigger_transition(self):
        self.assertEqual(self.transition("start-demo", origin="https://school.smartschool.be"), 403)
        self.assertEqual(self.transition("start-demo", token="invalid"), 409)
        self.assertEqual(self.query("POST", "/api/transition", b"{}")[0], 403)
        self.assertIsNone(self.controller.consume_pending())

    def test_mode_changes_require_token_and_rotate_it(self):
        old = self.controller.token
        self.assertEqual(self.transition("start-demo"), 202)
        self.assertEqual(self.controller.consume_pending(), "demo")
        self.assertEqual(self.transition("start-demo"), 409)
        self.controller.complete("demo")
        self.assertNotEqual(self.controller.token, old)
        self.assertEqual(self.query("GET", "/launcher/index.html")[0], 404)
        self.assertEqual(self.query("GET", "/launcher/demo.html")[0], 200)
        self.assertEqual(self.transition("finish-demo", token=old), 409)
        self.assertEqual(self.transition("finish-demo"), 202)
        self.controller.complete("portal")
        self.assertEqual(self.controller.mode, "portal")

    def test_unexpected_transition_rejected(self):
        self.assertEqual(self.transition("finish-demo"), 409)
        self.assertIsNone(self.controller.consume_pending())


if __name__ == "__main__":
    unittest.main(verbosity=2)
