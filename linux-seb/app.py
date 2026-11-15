#!/usr/bin/env python3
"""Experimental native SafeExamOS Linux examination browser.

Independent Linux WebKitGTK implementation informed by public SEB behavior.
NOT official SEB and NOT suitable for supervised examinations yet.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from linux_seb_policy import PolicyError, load_config


# This page is only used in an explicit QEMU CI boot. It is never an exam.
OFFLINE_SMOKE_HTML = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<style>
:root { font-family: sans-serif; color: #282828; background: #f0f0f0; }
body { margin: 0; padding: 36px; }
main { padding: 34px; background: white; border: 2px solid #1e90ff; }
h1 { color: #202020; font-size: 30px; margin: 0 0 16px; }
.blue { background: #1e90ff; height: 22px; margin: 18px 0; }
p { font-size: 18px; }
small { color: #666; }
</style></head>
<body><main>
<h1>SafeExamOS Linux native client</h1>
<div class="blue"></div>
<p>WebKitGTK rendered this offline laboratory page.</p>
<p>No exam content, credentials or network access is involved.</p>
<small>EXPERIMENTAL - NOT OFFICIAL SAFE EXAM BROWSER</small>
</main></body></html>"""


def run_native(policy, *, smoke_ui: bool = False) -> int:
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("WebKit2", "4.1")
        from gi.repository import Gdk, Gtk, WebKit2
    except (ImportError, ValueError) as exc:
        raise RuntimeError("GTK 3 / WebKit2GTK 4.1 dependencies unavailable") from exc

    if not Gtk.init_check()[0]:
        raise RuntimeError("No GTK display is available")

    class ExamWindow(Gtk.Window):
        def __init__(self):
            super().__init__(title="SafeExamOS - Linux native examination client (experimental)")
            self.set_default_size(1024, 768)
            self.set_decorated(False)
            self.fullscreen()
            self.connect("delete-event", self._deny_close)
            self.connect("key-press-event", self._intercept_keys)

            self.context = WebKit2.WebContext.new_ephemeral()
            self.context.connect("download-started", self._reject_download)
            self.context.set_cache_model(WebKit2.CacheModel.DOCUMENT_VIEWER)
            self.web = WebKit2.WebView.new_with_context(self.context)
            settings = self.web.get_settings()
            settings.set_enable_developer_extras(False)
            settings.set_enable_javascript(True)
            settings.set_enable_webgl(False)
            self.web.connect("decide-policy", self._decide_policy)
            self.web.connect("create", self._no_new_window)
            self.web.connect("permission-request", self._deny_permission)
            self.web.connect("context-menu", self._deny_context_menu)
            self.web.connect("load-changed", self._load_changed)
            self.add(self.web)

            if smoke_ui:
                self.web.load_html(OFFLINE_SMOKE_HTML, "about:blank")
            else:
                self.web.load_uri(policy.start_url)

        @staticmethod
        def _deny_close(_window, _event):
            return True

        @staticmethod
        def _deny_context_menu(_view, _context_menu, _event, _hit_test):
            return True

        @staticmethod
        def _intercept_keys(_window, event):
            # Defense-in-depth only. The compositor must ultimately own
            # forbidden shortcut handling; GTK cannot block all OS hotkeys.
            state = event.state
            control = bool(state & Gdk.ModifierType.CONTROL_MASK)
            shift = bool(state & Gdk.ModifierType.SHIFT_MASK)
            alt = bool(state & Gdk.ModifierType.MOD1_MASK)
            key = (Gdk.keyval_name(event.keyval) or "").lower()
            if control and key in ("t", "n", "w", "o", "p", "s", "u"):
                return True
            if control and shift and key in ("i", "j", "c"):
                return True
            return key == "f12" or (alt and key == "f4")

        @staticmethod
        def _reject_download(_context, download):
            download.cancel()

        @staticmethod
        def _no_new_window(_view, _action):
            return None

        @staticmethod
        def _deny_permission(_view, request):
            request.deny()
            return True

        def _load_changed(self, _view, event):
            if smoke_ui and event == WebKit2.LoadEvent.FINISHED:
                print("SAFEEXAMOS_NATIVE_SEB_UI_READY", flush=True)

        def _decide_policy(self, _view, decision, decision_type):
            try:
                if decision_type == WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:
                    decision.ignore()
                    return True
                if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
                    uri = decision.get_navigation_action().get_request().get_uri()
                elif decision_type == WebKit2.PolicyDecisionType.RESPONSE:
                    uri = decision.get_request().get_uri()
                else:
                    decision.ignore()
                    return True
                # The lab page is an in-memory WebKit document, not an
                # exception to the real examination URL policy.
                if smoke_ui and uri in ("about:blank", None):
                    decision.use()
                    return True
                if policy.permits(uri):
                    decision.use()
                else:
                    print("SAFEEXAMOS_LINUX_SEB_BLOCKED_NAVIGATION", file=sys.stderr)
                    decision.ignore()
                return True
            except (AttributeError, TypeError):
                decision.ignore()
                return True

    win = ExamWindow()
    win.show_all()
    Gtk.main()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path,
                        help="Explicit Linux SEB lab JSON configuration")
    parser.add_argument("--check-config", action="store_true",
                        help="Validate a lab configuration without launching GUI")
    parser.add_argument("--smoke-ui", action="store_true",
                        help="CI-only offline WebKitGTK render test; not an examination")
    args = parser.parse_args(argv)
    try:
        policy = load_config(args.config)
        if args.check_config:
            print("SAFEEXAMOS_LINUX_SEB_CONFIG_OK (lab-only)")
            return 0
        if args.smoke_ui and os.environ.get("SAFEEXAMOS_NATIVE_CI") != "1":
            raise PolicyError("Offline UI smoke is only available in CI mode")
        return run_native(policy, smoke_ui=args.smoke_ui)
    except (PolicyError, RuntimeError) as error:
        print("SAFEEXAMOS_LINUX_SEB_ERROR: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
