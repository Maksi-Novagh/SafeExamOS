#!/bin/sh
set -eu

echo "Checking mandatory SafeExamOS UI direction..."

test -s docs/design-system.md
test -s ui/prototype/styles.css
test -s build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/index.html

grep -qi "dodgerblue" ui/prototype/styles.css
grep -qi "#f0f0f0" ui/prototype/styles.css
grep -qi "lightblue" ui/prototype/styles.css
grep -qi "Segoe UI" ui/prototype/styles.css

grep -qi "dodgerblue" build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/index.html
grep -qi "#f0f0f0" build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/index.html
grep -qi "Segoe UI" build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/index.html

if grep -Eqi 'glassmorphism|backdrop-filter|linear-gradient|radial-gradient'   ui/prototype/styles.css   build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/index.html; then
  echo "error: unrelated visual language detected; see docs/design-system.md" >&2
  exit 1
fi

echo "UI direction check: PASS"
