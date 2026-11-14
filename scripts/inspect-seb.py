#!/usr/bin/env python3
"""Read-only Safe Exam Browser .seb format inspector.

Level L0 only: never applies configuration, decrypts files, launches
browsers, or claims Config Key / Browser Exam Key compatibility.

See https://safeexambrowser.org/developer/seb-file-format.html
"""
from __future__ import annotations

import argparse
import json
import plistlib
import sys
import zlib
from pathlib import Path

MAX_FILE_BYTES = 1024 * 1024
MAX_EXPANDED_BYTES = 4 * 1024 * 1024

ENCRYPTED_PREFIXES = {
    b"pswd": "password-encrypted exam settings",
    b"pwcc": "password-encrypted client settings",
    b"pkhs": "certificate-encrypted settings",
    b"phsk": "hybrid certificate-encrypted settings",
}

# These are recognized for *inspection*, not supported for exam launching.
RECOGNIZED_KEYS = frozenset({
    "startURL",
    "allowQuit",
    "quitURL",
    "quitURLConfirm",
    "browserWindowAllowReload",
    "browserWindowAllowBackForward",
    "browserWindowShowURL",
    "URLFilterEnable",
    "URLFilterRules",
    "enableJavaScript",
    "allowDownUploads",
    "allowDownloads",
    "allowUploads",
    "newBrowserWindowByLinkPolicy",
    "newBrowserWindowByScriptPolicy",
    "sebServerURL",
    "sebServerEnabled",
    "permittedProcesses",
    "prohibitedProcesses",
    "embeddedCertificates",
    "proxySettings",
})


class SebInspectionError(ValueError):
    """The file cannot be safely inspected or must not be accepted."""


def gunzip_limited(blob: bytes) -> bytes:
    if not blob.startswith(b"\x1f\x8b"):
        raise SebInspectionError("Expected gzip-compressed SEB data")
    try:
        decoder = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
        result = decoder.decompress(blob, MAX_EXPANDED_BYTES + 1)
        if (
            len(result) > MAX_EXPANDED_BYTES
            or decoder.unconsumed_tail
            or not decoder.eof
            or decoder.unused_data
        ):
            raise SebInspectionError("Oversized, truncated, or concatenated gzip input")
        return result
    except zlib.error as exc:
        raise SebInspectionError("Malformed gzip data") from exc


def inspect_bytes(data: bytes) -> dict[str, object]:
    if len(data) > MAX_FILE_BYTES:
        raise SebInspectionError("SEB file exceeds input size limit")
    if not data:
        raise SebInspectionError("Empty SEB file")

    if data.startswith(b"\x1f\x8b"):
        wrapped = gunzip_limited(data)
        prefix = wrapped[:4]
        if prefix in ENCRYPTED_PREFIXES:
            raise SebInspectionError(
                "Encrypted configuration (" + ENCRYPTED_PREFIXES[prefix] +
                ") is not supported; no decryption was attempted"
            )
        if prefix != b"plnd":
            raise SebInspectionError("Unknown SEB wrapper prefix")
        raw_xml = gunzip_limited(wrapped[4:])
        file_format = "seb-plnd-gzip-xml"
    elif data.lstrip().startswith(b"<?xml"):
        # SEB Server and configuration tools can export plain XML for research.
        # This is never an authenticated or tamper-resistant exam file.
        raw_xml = data
        file_format = "plain-xml-inspection-only"
    else:
        raise SebInspectionError("Unrecognized SEB file type")

    try:
        settings = plistlib.loads(raw_xml, fmt=plistlib.FMT_XML)
    except (ValueError, TypeError, ExpatError) as exc:
        raise SebInspectionError("Malformed SEB XML plist") from exc

    if not isinstance(settings, dict):
        raise SebInspectionError("SEB settings must be a dictionary")
    if len(settings) > 500:
        raise SebInspectionError("Too many SEB setting keys")
    if any(not isinstance(key, str) or len(key) > 200 for key in settings):
        raise SebInspectionError("Invalid SEB setting key")

    names = sorted(settings)
    return {
        "status": "inspect-only",
        "format": file_format,
        "launchable": False,
        "authenticated": False,
        "setting_count": len(names),
        "recognized_keys": [name for name in names if name in RECOGNIZED_KEYS],
        "unrecognized_keys": [name for name in names if name not in RECOGNIZED_KEYS],
        "message": (
            "Keys are identified only, not applied. Do not use these "
            "settings for an examination; security-sensitive compatibility "
            "and encrypted configuration handling are not implemented."
        ),
    }


def inspect_path(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise SebInspectionError("SEB input must be a regular file")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise SebInspectionError("SEB file exceeds input size limit")
    with path.open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    return inspect_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="Local .seb or plain XML test file")
    parser.add_argument("--json", action="store_true", help="Machine-readable report")
    options = parser.parse_args()
    try:
        result = inspect_path(options.file)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (SebInspectionError, OSError) as exc:
        report = {"status": "rejected", "launchable": False, "error": str(exc)}
        if options.json:
            print(json.dumps(report, sort_keys=True))
        else:
            print("SEB inspection rejected: " + str(exc), file=sys.stderr)
        return 2


# Avoid depending on implementation details of the plistlib XML exception.
from xml.parsers.expat import ExpatError  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
