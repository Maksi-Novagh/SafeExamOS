#!/bin/sh
set -eu

echo "Checking amd64 build tree..."

required="
build/amd64/build.sh
build/amd64/config/package-lists/safeexamos.list.chroot
build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session
build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-preflight
build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-seat-ready
build/amd64/config/includes.chroot/etc/systemd/system/seatd.service.d/10-safeexamos.conf
build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/preflight.js
build/amd64/config/hooks/live/0100-safeexamos-permissions.hook.chroot
build/amd64/config/hooks/live/0130-safeexamos-kiosk.hook.chroot
build/amd64/config/hooks/live/0140-safeexamos-lockdown.hook.chroot
build/amd64/config/hooks/live/0200-safeexamos-cleanup.hook.chroot
build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/index.html
build/amd64/config/includes.chroot/etc/dpkg/dpkg.cfg.d/01-safeexamos-minimal
build/amd64/config/includes.chroot/etc/systemd/system/safeexamos-kiosk.service
build/amd64/config/includes.chroot/etc/chromium/policies/managed/safeexamos.json
build/amd64/config/includes.chroot/etc/systemd/logind.conf.d/50-safeexamos.conf
build/amd64/config/includes.chroot/etc/systemd/system/safeexamos-ci-boot-marker.service
build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-ci-boot-marker
build/amd64/config/includes.chroot/etc/systemd/system/safeexamos-ci-ui-marker.service
build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-ci-ui-marker
scripts/report-image-metrics.sh
scripts/verify-framebuffer.py
scripts/inspect-seb.py
scripts/check-chromium-policy.py
tests/inspect-seb-smoke.py
tests/launcher-smoke.cjs
tests/demo-exam-smoke.cjs
build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/demo.html
build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/demo-exam.js
tests/preflight-smoke.sh
scripts/report-runtime-metrics.sh
scripts/collect-hardware-report.sh
hardware/profiles/qemu-amd64.json
hardware/profiles/lenovo-v15-g2-alc-82kd.json
docs/release-target-2026-11-04.md
docs/lockdown-baseline.md
docs/escape-and-cheating-catalog.md
"

for f in $required; do
  test -s "$f" || {
    echo "error: missing required build file: $f" >&2
    exit 1
  }
done

PKGS=build/amd64/config/package-lists/safeexamos.list.chroot
SESSION=build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session

for pkg in cage chromium network-manager user-setup seatd libseat1; do
  grep -Eq "^$pkg$" "$PKGS" || {
    echo "error: required runtime package missing: $pkg" >&2
    exit 1
  }
done

if grep -Eq 'exec cage .* -s([[:space:]]|$)' "$SESSION"; then
  echo "error: Cage VT switching must not be enabled in the exam session" >&2
  exit 1
fi

if grep -Eq 'chromium .*--no-sandbox' "$SESSION"; then
  echo "error: Chromium sandbox must not be disabled" >&2
  exit 1
fi

grep -Fq -- '--app="$LAUNCHER"' "$SESSION" || {
  echo "error: Chromium must launch the exam surface in app mode" >&2
  exit 1
}

if grep -Fq -- '--kiosk' "$SESSION"; then
  echo "error: legacy Chromium kiosk mode must not replace app mode" >&2
  exit 1
fi

grep -Fq '"BrowserGuestModeEnabled": false' build/amd64/config/includes.chroot/etc/chromium/policies/managed/safeexamos.json
grep -Fq 'NAutoVTs=0' build/amd64/config/includes.chroot/etc/systemd/logind.conf.d/50-safeexamos.conf

SEAT_UNIT=build/amd64/config/includes.chroot/etc/systemd/system/safeexamos-kiosk.service
SEAT_HOOK=build/amd64/config/hooks/live/0130-safeexamos-kiosk.hook.chroot
SEAT_DROPIN=build/amd64/config/includes.chroot/etc/systemd/system/seatd.service.d/10-safeexamos.conf

grep -Fq 'Requires=seatd.service' "$SEAT_UNIT"
grep -Fq 'After=live-config.service' "$SEAT_UNIT"
grep -Fq 'Environment=LIBSEAT_BACKEND=seatd' "$SEAT_UNIT"
grep -Fq 'ExecStartPre=/usr/local/sbin/safeexamos-seat-ready' "$SEAT_UNIT"
grep -Fq 'systemctl enable seatd.service' "$SEAT_HOOK"
grep -Fq 'ExecStart=/usr/sbin/seatd -g video' "$SEAT_DROPIN"
# Never launch Chromium or Cage as root or disable the browser sandbox.
grep -Fq 'User=exam' "$SEAT_UNIT"
grep -Fq 'Environment=WLR_RENDERER=pixman' "$SEAT_UNIT"
grep -Fq 'Environment=XDG_CACHE_HOME=/run/safeexamos-exam/cache' "$SEAT_UNIT"
grep -Fq 'Environment=HOME=/run/safeexamos-exam' "$SEAT_UNIT"

command -v node >/dev/null 2>&1 || {
  echo "error: Node.js is required for automated launcher fixtures" >&2
  exit 1
}
command -v python3 >/dev/null 2>&1 || {
  echo "error: Python 3 is required for framebuffer verification" >&2
  exit 1
}
node ./tests/launcher-smoke.cjs
node ./tests/demo-exam-smoke.cjs
python3 ./tests/inspect-seb-smoke.py
python3 ./scripts/check-chromium-policy.py
sh ./tests/preflight-smoke.sh
python3 -m py_compile ./scripts/verify-framebuffer.py

echo "Build tree check: PASS (including launcher and preflight fixtures)"
