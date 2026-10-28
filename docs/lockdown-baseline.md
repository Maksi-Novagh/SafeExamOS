# Lockdown baseline

Status: **implemented baseline, validation in progress**

This document records security controls already present in the prototype. It is not a claim that SafeExamOS is escape-proof.

## Browser surface

SafeExamOS launches Chromium as a single application surface rather than a normal tabbed browser window.

Managed Chromium policies currently disable:

- guest profiles;
- adding browser profiles;
- password saving;
- background browser processes;
- bookmark editing;
- browser file-selection dialogs;
- persistent "always allow" external-protocol choices;
- profile picker on startup.

These policies are machine-managed JSON under:

```text
/etc/chromium/policies/managed/
```

The policy directory is part of the read-only image and is not writable by the exam user.

## Session and console surface

The image currently:

- does not auto-spawn virtual terminals;
- reserves no alternate VT through logind;
- masks gettys on tty2 through tty6;
- masks the serial getty;
- masks `debug-shell.service`;
- masks `ctrl-alt-del.target`;
- runs the graphical session as the unprivileged `exam` user;
- restarts the kiosk service on failure.

## Remaining critical work

The following are still not considered solved:

- compositor/policy-level blocking of forbidden keyboard shortcuts;
- proof that browser exit cannot expose any usable console on physical hardware;
- restricted URL/navigation policy;
- controlled upload/download flows;
- device hotplug enforcement;
- explicit session teardown;
- local privileged policy daemon;
- security regression automation for shortcut attempts.

The defensive threat catalog in `docs/escape-and-cheating-catalog.md` remains the authoritative backlog.
