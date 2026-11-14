#!/usr/bin/env python3
"""Fail the build if Chromium exam baseline policies regress."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "build/amd64/config/includes.chroot/etc/chromium/policies/managed/safeexamos.json"
policy = json.loads(PATH.read_text(encoding="utf-8"))
expected = {
    "DeveloperToolsAvailability": 2,
    "DefaultPopupsSetting": 2,
    "PrintingEnabled": False,
    "IncognitoModeAvailability": 1,
    "AllowFileSelectionDialogs": False,
    "PasswordManagerEnabled": False,
    "BrowserGuestModeEnabled": False,
    "BrowserAddPersonEnabled": False,
    "SpellcheckEnabled": False,
    "TranslateEnabled": False,
    "DownloadRestrictions": 3,
}
for name, value in expected.items():
    if policy.get(name) != value:
        raise SystemExit(f"Chromium lockdown policy mismatch: {name} != {value!r}")
for required in ("http://*", "https://*", "view-source:*", "devtools:*"):
    if required not in policy.get("URLBlocklist", []):
        raise SystemExit(f"Missing blocked navigation scheme: {required}")
if policy.get("ExtensionInstallBlocklist") != ["*"]:
    raise SystemExit("Chromium extensions must remain blocked by default")
print("Managed Chromium baseline policy: PASS")
