#!/usr/bin/env python3
"""Experimental native SafeExamOS Linux examination browser.

Independent Linux WebKitGTK implementation informed by public SEB behavior.
NOT official SEB and NOT suitable for supervised examinations yet.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import os
import sys
from pathlib import Path

from linux_seb_policy import PolicyError, load_config
from linux_seb_windows import ManagedWindows, WindowPolicyError


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

# CI-only child surface: distinct orange pixels prove that a *second* WebKit
# page is painted above the blue primary surface. No external URL is fetched.
OFFLINE_CHILD_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
body{margin:0;padding:22px;font-family:sans-serif;background:#fff;color:#252525}
main{background:white;border:2px solid #ed6a17;padding:24px}
h1{font-size:26px}.orange{background:#ed6a17;height:32px;margin:18px 0}
</style></head><body><main>
<h1>Managed secondary browser window</h1>
<div class="orange"></div>
<p>Separate native WebKitGTK surface. Offline QEMU fixture only.</p>
</main></body></html>"""


def run_native(policy, *, smoke_ui: bool = False, smoke_windows: bool = False) -> int:
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("WebKit2", "4.1")
        from gi.repository import Gdk, GLib, Gtk, WebKit2
    except (ImportError, ValueError) as exc:
        raise RuntimeError("GTK 3 / WebKit2GTK 4.1 dependencies unavailable") from exc

    if not Gtk.init_check()[0]:
        raise RuntimeError("No GTK display is available")

    manager = ManagedWindows(policy)
    main_record = manager.open_main()
    secondary_windows = {}

    class ExamWindow(Gtk.Window):
        def __init__(self):
            super().__init__(title="SafeExamOS - Linux native examination client (experimental)")
            self.set_default_size(1024, 768)
            self.set_decorated(False)
            self.fullscreen()
            self.record = main_record
            self._ci_child_started = False
            self.connect("delete-event", self._deny_close)
            self.connect("key-press-event", self._intercept_keys)

            self.context = WebKit2.WebContext.new_ephemeral()
            self.context.connect("download-started", self._reject_download)
            self.context.set_cache_model(WebKit2.CacheModel.DOCUMENT_VIEWER)
            self.web = self._managed_view(main_record)
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

        def _managed_view(self, record, related_view=None):
            # WebKit requires popup WebViews to be related to their opener.
            # This also keeps secondary pages in the ephemeral WebContext.
            view = (WebKit2.WebView.new_with_related_view(related_view)
                    if related_view is not None
                    else WebKit2.WebView.new_with_context(self.context))
            settings = view.get_settings()
            settings.set_enable_developer_extras(False)
            settings.set_enable_javascript(True)
            settings.set_enable_webgl(False)
            view.connect("decide-policy", self._decide_policy)
            view.connect("create", self._new_window, record.window_id)
            view.connect("permission-request", self._deny_permission)
            view.connect("context-menu", self._deny_context_menu)
            view.connect("load-changed", self._load_changed)
            return view

        def _new_window(self, _view, action, parent_id):
            # WebKit's create signal occurs before a new page is committed.
            # A child must have an approved exact HTTPS origin and capacity.
            try:
                uri = action.get_request().get_uri()
                record = manager.open_child(parent_id, uri)
            except (AttributeError, WindowPolicyError, TypeError):
                print("SAFEEXAMOS_NATIVE_SEB_DENIED_CHILD", file=sys.stderr)
                return None
            view = self._managed_view(record, related_view=_view)
            view.connect("ready-to-show", self._show_child, record)
            view.connect("close", self._close_child, record.window_id)
            return view

        def _show_child(self, view, record):
            # Real pop-ups are shown only after WebKit emits ready-to-show.
            self._present_child(view, record)

        def _present_child(self, view, record):
            if record.window_id not in manager.records:
                return None
            child = Gtk.Window(title="SEB approved resource")
            # The compositor must preserve a visible portion of the primary
            # surface so the CI can prove that both windows were rendered.
            child.set_default_size(640, 380)
            child.set_decorated(False)
            child.set_transient_for(self)
            child.set_modal(False)
            child.connect("key-press-event", self._intercept_keys)
            child.connect("delete-event", lambda *_: self._close_child(view, record.window_id))
            child.add(view)
            secondary_windows[record.window_id] = child
            child.show_all()
            print("SAFEEXAMOS_NATIVE_SEB_CHILD_OPEN", flush=True)
            return child

        def _open_ci_child(self):
            # Only an explicit QEMU lab command line can reach this function.
            # The policy is checked just as for an ordinary child request,
            # but the child content comes from an in-memory offline fixture.
            target = "https://exam.example.org/resource"
            try:
                record = manager.open_child(main_record.window_id, target)
            except WindowPolicyError as exc:
                print("SAFEEXAMOS_NATIVE_SEB_CI_CHILD_DENIED: " + str(exc), file=sys.stderr)
                return False
            view = self._managed_view(record, related_view=self.web)
            view.connect("close", self._close_child, record.window_id)
            if self._present_child(view, record) is not None:
                view.load_html(OFFLINE_CHILD_HTML, "about:blank")
            return False

        def _close_child(self, _view, window_id):
            try:
                manager.close(window_id)
            except WindowPolicyError:
                return True
            child = secondary_windows.pop(window_id, None)
            if child is not None:
                child.hide()
                child.destroy()
            print("SAFEEXAMOS_NATIVE_SEB_CHILD_CLOSED", flush=True)
            return True

        @staticmethod
        def _deny_permission(_view, request):
            request.deny()
            return True

        def _load_changed(self, view, event):
            if not smoke_ui or event != WebKit2.LoadEvent.FINISHED:
                return
            if view is self.web:
                print("SAFEEXAMOS_NATIVE_SEB_UI_READY", flush=True)
                if smoke_windows and not self._ci_child_started:
                    self._ci_child_started = True
                    GLib.idle_add(self._open_ci_child)
            elif smoke_windows:
                print("SAFEEXAMOS_NATIVE_SEB_CHILD_READY", flush=True)

        def _decide_policy(self, _view, decision, decision_type):
            try:
                if decision_type == WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:
                    # A child WebView is created by the managed create signal.
                    # This decision is never permission to launch a foreign app.
                    uri = decision.get_navigation_action().get_request().get_uri()
                    if policy.allow_secondary_windows and policy.permits(uri):
                        decision.use()
                    else:
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
    parser.add_argument("--smoke-windows", action="store_true",
                        help="CI-only second WebKitGTK window fixture; requires --smoke-ui")
    args = parser.parse_args(argv)
    try:
        policy = load_config(args.config)
        if args.check_config:
            print("SAFEEXAMOS_LINUX_SEB_CONFIG_OK (lab-only)")
            return 0
        if args.smoke_ui and os.environ.get("SAFEEXAMOS_NATIVE_CI") != "1":
            raise PolicyError("Offline UI smoke is only available in CI mode")
        if args.smoke_windows and not args.smoke_ui:
            raise PolicyError("Multiwindow CI requires the offline UI fixture")
        if args.smoke_windows:
            policy = replace(policy, max_browser_windows=2,
                             allow_secondary_windows=True)
        return run_native(policy, smoke_ui=args.smoke_ui,
                          smoke_windows=args.smoke_windows)
    except (PolicyError, RuntimeError) as error:
        print("SAFEEXAMOS_LINUX_SEB_ERROR: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
