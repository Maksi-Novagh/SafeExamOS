# Experimental Wayland descriptor handoff

Status: offline transport primitive only; **not enabled in the kiosk**.

## Intent

To separate browser and compositor accounts safely, the browser should not
receive pathname access to the compositor's private Wayland socket. A trusted
launcher may instead connect on the authorized client's behalf and transfer
exactly one connected Unix-domain stream descriptor using `SCM_RIGHTS`.
The browser can then use Linux's `WAYLAND_SOCKET` environment contract, with
its inherited descriptor made available at process exec time.

The new source module `linux-seb/fd_handoff.py` implements one-descriptor
transfer and strict receiver validation. The offline regression test covers
connection use without pathname traversal, missing descriptors, unexpected
file types, and CLOEXEC behavior. The transport is **not wired to Cage,
labwc, or Chromium yet**.

## Authorization design — still required

- A compositor-owner account must be separate from a browser account.
- A small privileged launcher must open exactly one permitted Wayland socket.
- The broker must authenticate its intended child process and never expose an
  unrestricted public broker endpoint reachable by other browser-UID processes.
- The browser must inherit only the granted connection; its filesystem view
  must not permit opening the compositor's socket path.
- Child renderer processes must not gain unintended access to the channel.
- Crash handling and FD revocation need live tests.
- Negative QEMU tests must demonstrate that an unapproved browser-UID process
  cannot open a second Wayland connection.

Passing a descriptor does **not** prevent a compromised authorized client from
abusing its existing connection or creating surfaces. It also provides no
replacement for Wayland compositor policy, syscall confinement, or verified
boot. Existing kiosk behavior remains unchanged pending actual integration.

Rollback: remove the new source/test/documentation files. No boot options
or service definitions have changed.
