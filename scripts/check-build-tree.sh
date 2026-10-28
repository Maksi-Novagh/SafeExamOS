#!/bin/sh
set -eu

echo "Checking amd64 build tree..."

required="
build/amd64/build.sh
build/amd64/config/package-lists/safeexamos.list.chroot
build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session
build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-preflight
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

for pkg in cage chromium network-manager user-setup; do
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

echo "Build tree check: PASS"
