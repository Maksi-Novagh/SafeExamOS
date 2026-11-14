# SEB input inspection and browser baseline (2026-11-14)

Status: **L0 inspect-only prototype; NOT a certified SEB client**.

## Why this is restrictive

Official SEB configuration files use an outer gzip wrapper followed by a four-byte format prefix. The unencrypted `plnd` form contains a second gzip-compressed XML property list. Password/certificate-encrypted variants `pswd`, `pwcc`, `pkhs`, `phsk` require separate audited cryptographic support.

Reference: https://safeexambrowser.org/developer/seb-file-format.html

Use the read-only inspector with: `python3 scripts/inspect-seb.py --json local-test.seb`

It never applies settings, launches a website or reveals values. It reports format and recognized/unrecognized setting *names*. A `plnd` file is unauthenticated and cannot be accepted as a production exam configuration.

## Defensive limits

- Maximum input size: 1 MiB; maximum expanded gzip layer: 4 MiB
- Only XML plist dictionaries; malformed data rejected
- Encrypted wrappers rejected without decryption attempts
- No secret values, exam URLs, passwords, or key material in reports
- Unknown keys are classified, never silently applied
- Recognition of a key does not imply support for its semantics

Tests: `tests/inspect-seb-smoke.py` covers real-format gzip/plnd/gzip plist, malformed wrappers, encrypted-prefix rejection, and size limits.

## Chromium managed-policy baseline

The Debian image has a default-deny browser policy: DevTools, printing, unmanaged extensions, popups, downloads and guest/incognito/profile features are restricted. Ordinary HTTP/HTTPS navigation is blocked for this offline-only prototype. External exam navigation requires a future validated, scoped policy from authenticated configuration, not an unsafe blanket exception.

The build verifies policy presence, not full live-browser enforcement.

## Known shortcut defect

The user observed that `Ctrl+T` and `Ctrl+Shift+I` still work in the previous build.

- `Ctrl+Shift+I`: policy `DeveloperToolsAvailability=2` was added as an interim mitigation, but must be verified in a running Chromium instance.
- `Ctrl+T`, `Ctrl+N`, `Ctrl+W` and OS-level shortcuts remain **release blockers**. Browser app mode and managed policies are not sufficient. These need compositor/browser-level command interception with real input-event tests.
- HTML/JavaScript keydown handlers are not an acceptable sole enforcement boundary for untrusted exam pages.

## Next gates

1. Verify managed policies are actually loaded and exercise DevTools shortcut against the live browser.
2. Implement and test browser/compositor shortcut restrictions; test all blocked keyboard commands in QEMU and VMware.
3. Implement audited encrypted `.seb` handling, supported-setting mapping and strict unknown-key failure policy.
4. Add authenticated configuration, scoped exam URL allowlists, session lifecycle, and secure profile destruction.
5. Validate on real hardware; do not claim SEB Server, Config Key or Browser Exam Key compatibility until tested.

No official SEB compatibility or secure exam readiness is claimed by this baseline.
