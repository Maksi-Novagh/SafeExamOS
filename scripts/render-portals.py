#!/usr/bin/env python3
"""Build the pre-exam portal catalog and its Chromium navigation exceptions.

This is an *institution configuration* generator. It does not configure an
exam policy and cannot turn SafeExamOS into a certified lockdown browser.
Use --check in CI; use --write only while preparing an authorized image.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/portals.json"
POLICY = ROOT / "build/amd64/config/includes.chroot/etc/chromium/policies/managed/safeexamos.json"
CATALOG = ROOT / "build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/portals.js"

ID = re.compile(r"^[a-z][a-z0-9-]{0,39}$")
HOST = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$")
SUPPORTED = {"smartschool", "fixed"}


def safe_url(value: str, *, origin_only: bool = False) -> tuple[str, str]:
    if not isinstance(value, str) or len(value) > 1024:
        raise ValueError("Invalid portal URL")
    if any(ch.isspace() or ord(ch) < 32 for ch in value):
        raise ValueError("Whitespace/control characters are not allowed in a portal URL")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.port is not None or parsed.fragment
            or not HOST.fullmatch(parsed.hostname) or parsed.hostname != parsed.hostname.lower()):
        raise ValueError("Portal must use a canonical HTTPS domain without credentials, ports or fragment")
    if origin_only and (parsed.path not in ("", "/") or parsed.query):
        raise ValueError("Identity provider origins must not contain a path or query")
    if ".." in parsed.path.split("/") or "\\" in parsed.path:
        raise ValueError("Unsafe portal URL path")
    return "https://" + parsed.hostname, parsed.geturl()


def validate(config: object) -> tuple[list[dict[str, str]], list[str]]:
    if not isinstance(config, dict) or set(config) != {"schema_version", "portals", "identity_origins"}:
        raise ValueError("Portal configuration has unexpected fields")
    if config["schema_version"] != 1:
        raise ValueError("Unsupported portal configuration version")
    portals = config["portals"]
    origins = config["identity_origins"]
    if not isinstance(portals, list) or not 1 <= len(portals) <= 12:
        raise ValueError("Expected 1-12 configured portals")
    if not isinstance(origins, list) or len(origins) > 12:
        raise ValueError("Too many identity providers")
    result = []
    allowed = set()
    seen = set()
    for portal in portals:
        if not isinstance(portal, dict):
            raise ValueError("Portal entry must be an object")
        kind = portal.get("kind")
        if kind not in SUPPORTED:
            raise ValueError("Unrecognized portal kind")
        required = {"kind", "id", "label"} | ({"start_url"} if kind == "fixed" else set())
        if set(portal) != required:
            raise ValueError("Unexpected or missing portal fields")
        name = portal["id"]
        label = portal["label"]
        if not isinstance(name, str) or not ID.fullmatch(name) or name in seen:
            raise ValueError("Invalid/duplicate portal ID")
        if not isinstance(label, str) or not 1 <= len(label) <= 60 or any(ord(c) < 32 for c in label):
            raise ValueError("Invalid portal label")
        seen.add(name)
        if kind == "smartschool":
            allowed.add("https://smartschool.be")
            result.append({"id": name, "label": label, "kind": kind})
        else:
            origin, normalized = safe_url(portal["start_url"])
            allowed.add(origin)
            result.append({"id": name, "label": label, "kind": kind, "start_url": normalized})
    for origin in origins:
        canonical, _ = safe_url(origin, origin_only=True)
        if origin.rstrip("/") != canonical:
            raise ValueError("Identity provider URL must be canonical")
        allowed.add(canonical)
    return result, sorted(allowed)


def build_outputs(config: dict, current_policy: dict) -> tuple[str, str]:
    portals, allowed = validate(config)
    policy = dict(current_policy)
    if not isinstance(policy.get("URLBlocklist"), list) or not all(
        pattern in policy["URLBlocklist"] for pattern in ("http://*", "https://*")
    ):
        raise ValueError("No default-deny HTTP(S) blocklist found")
    policy["URLAllowlist"] = allowed
    # Authentication pages may rely on popup dialogs. This is only a pre-exam
    # portal allowance; it must not be inherited as a secure exam policy.
    policy["PopupsAllowedForUrls"] = allowed
    public_data = {"schema_version": 1, "portals": portals}
    catalog_js = "window.SAFEEXAMOS_PORTALS = " + json.dumps(
        public_data, separators=(",", ":"), ensure_ascii=True, sort_keys=True
    ) + ";\n"
    return json.dumps(policy, indent=2, sort_keys=True, ensure_ascii=True) + "\n", catalog_js


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Verify generated outputs match the portal config")
    mode.add_argument("--write", action="store_true", help="Generate outputs for a new institutional image")
    args = parser.parse_args()
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        current_policy = json.loads(POLICY.read_text(encoding="utf-8"))
        policy, catalog = build_outputs(config, current_policy)
        if args.check:
            if POLICY.read_text(encoding="utf-8") != policy or CATALOG.read_text(encoding="utf-8") != catalog:
                raise ValueError("Portal outputs are stale; run scripts/render-portals.py --write")
        else:
            POLICY.write_text(policy, encoding="utf-8")
            CATALOG.parent.mkdir(parents=True, exist_ok=True)
            CATALOG.write_text(catalog, encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as err:
        print("Portal policy validation failed: " + str(err), file=sys.stderr)
        return 1
    print("Portal policy: PASS" if args.check else "Portal policy: generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
