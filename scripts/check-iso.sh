#!/bin/sh
set -eu

ISO=${1:-}
if [ -z "$ISO" ] || [ ! -s "$ISO" ]; then
  echo "usage: $0 <SafeExamOS.iso>" >&2
  exit 2
fi

echo "Checking ISO: $ISO"

xorriso -indev "$ISO" -find / -name 'filesystem.squashfs' -print | grep -q filesystem.squashfs
xorriso -indev "$ISO" -find / -name 'vmlinuz*' -print | grep -q vmlinuz
xorriso -indev "$ISO" -find / -name 'initrd*' -print | grep -q initrd

if [ -f "$ISO.sha256" ]; then
  (
    cd "$(dirname "$ISO")"
    sha256sum -c "$(basename "$ISO").sha256"
  )
fi

echo "ISO structure check: PASS"
