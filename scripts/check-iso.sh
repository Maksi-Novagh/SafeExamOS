#!/bin/sh
set -eu

ISO=${1:-}
if [ -z "$ISO" ] || [ ! -s "$ISO" ]; then
  echo "usage: $0 <SafeExamOS.iso>" >&2
  exit 2
fi

echo "Checking ISO: $ISO"

ISO_TREE=$(xorriso -indev "$ISO" -find / 2>&1)

printf '%s
' "$ISO_TREE" | grep -q '/live/filesystem.squashfs'
printf '%s
' "$ISO_TREE" | grep -Eq '/live/vmlinuz([0-9.-]*)?$'
printf '%s
' "$ISO_TREE" | grep -Eq '/live/initrd([0-9.-]*)?\.img$|/live/initrd([0-9.-]*)?$'

if [ -f "$ISO.sha256" ]; then
  (
    cd "$(dirname "$ISO")"
    sha256sum -c "$(basename "$ISO").sha256"
  )
fi

echo "ISO structure check: PASS"
