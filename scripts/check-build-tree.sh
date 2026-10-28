#!/bin/sh
set -eu

echo "Checking amd64 build tree..."

required="
build/amd64/build.sh
build/amd64/config/package-lists/safeexamos.list.chroot
build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session
build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/index.html
build/amd64/config/hooks/live/0100-safeexamos-permissions.hook.chroot
build/amd64/config/includes.chroot/etc/systemd/system/safeexamos-ci-boot-marker.service
build/amd64/config/includes.chroot/etc/systemd/system/getty@tty1.service.d/autologin.conf
build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-ci-boot-marker
build/amd64/config/includes.chroot/etc/systemd/system/safeexamos-ci-ui-marker.service
build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-ci-ui-marker
"

for f in $required; do
  test -s "$f" || {
    echo "error: missing required build file: $f" >&2
    exit 1
  }
done

grep -Eq '^cage$' build/amd64/config/package-lists/safeexamos.list.chroot
grep -Eq '^chromium$' build/amd64/config/package-lists/safeexamos.list.chroot
grep -Eq '^network-manager$' build/amd64/config/package-lists/safeexamos.list.chroot

if grep -Eq 'exec cage .* -s([[:space:]]|$)' build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session; then
  echo "error: Cage VT switching (-s) must not be enabled in the exam session" >&2
  exit 1
fi

if grep -Eq 'chromium .*--no-sandbox' build/amd64/config/includes.chroot/usr/local/bin/safeexamos-session; then
  echo "error: Chromium sandbox must not be disabled" >&2
  exit 1
fi

echo "Build tree check: PASS"
