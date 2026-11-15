#!/usr/bin/env python3
"""Experimental native SafeExamOS Linux examination browser.

Independent Linux implementation informed by SEB Windows 3.10.3 architecture.
Not official SEB; does not implement BEK/CK, encrypted .seb or certified lockdown.
The existing Chromium portal remains the default system browser.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from linux_seb_policy import PolicyError, load_config


def run_native(policy) -> int:
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("WebKit2", "4.1")
        from gi.repository import Gdk, Gtk, WebKit2
    except (ImportError, ValueError) as exc:
        raise RuntimeError("GTK 3 / WebKit2GTK 4.1 dependencies unavailable") from exc

    class ExamWindow(Gtk.Window):
        def __init__(self):
            super().__init__(title="SafeExamOS Linux examination client (experimental)")
            self.set_default_size(1024, 768)
            self.connect("delete-event", self._deny_close)
            self.connect("key-press-event", self._intercept_keys)
            self.set_decorated(False)
            self.fullscreen()

            context = WebKit2.WebContext.new_ephemeral()
            # An ephemeral WebContext limits persistence; the application is
            # also run from a private runtime directory by SafeExamOS.
            context.connect("download-started", self._reject_download)
            view = WebKit2.WebView.new_with_context(context)
            self.web = view
            settings = view.get_settings()
            settings.set_enable_developer_extras(False)
            settings.set_enable_javascript(True)
            settings.set_enable_webgl(False)
            view.connect("decide-policy", self._decide_policy)
            view.connect("create", self._no_new_window)
            view.connect("permission-request", self._deny_permission)
            self.add(view)
            view.load_uri(policy.start_url)

        @staticmethod
        def _deny_close(_window, _event):
            # No untrusted page can close the session via window manager.
            return True

        @staticmethod
        def _intercept_keys(_window, event):
            # Best effort only: compositor-level shortcuts and all WebKit
            # native commands need independent OS-level validation.
            state = event.state
            control = bool(state & Gdk.ModifierType.CONTROL_MASK)
            shift = bool(state & Gdk.ModifierType.SHIFT_MASK)
            alt = bool(state & Gdk.ModifierType.MOD1_MASK)
            key = Gdk.keyval_name(event.keyval) or ""
            if control and key.lower() in ("t", "n", "w", "o", "p", "s", "u"):
                return True
            if control and shift and key.lower() in ("i", "j", "c"):
                return True
            if key in ("F12",) or (alt and key == "F4"):
                return True
            return False

        @staticmethod
        def _reject_download(_context, download):
            download.cancel()

        @staticmethod
        def _no_new_window(_view, _action):
            # The current application has exactly one WebView.
            return None

        @staticmethod
        def _deny_permission(_view, request):
            request.deny()
            return True

        def _decide_policy(self, _view, decision, decision_type):
            try:
                if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
                    uri = decision.get_navigation_action().get_request().get_uri()
                elif decision_type == WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:
                    decision.ignore()
                    return True
                elif decision_type == WebKit2.PolicyDecisionType.RESPONSE:
                    uri = decision.get_request().get_uri()
                else:
                    decision.ignore()
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
    parser.add_argument("--config", required=True, type=Path, help="Explicit Linux SEB lab JSON configuration")
    parser.add_argument("--check-config", action="store_true", help="Validate without launching any GUI")
    args = parser.parse_args(argv)
    try:
        policy = load_config(args.config)
        if args.check_config:
            print("SAFEEXAMOS_LINUX_SEB_CONFIG_OK (lab-only; not a real SEB .seb file)")
            return 0
        return run_native(policy)
    except (PolicyError, RuntimeError) as error:
        print("SAFEEXAMOS_LINUX_SEB_ERROR: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
