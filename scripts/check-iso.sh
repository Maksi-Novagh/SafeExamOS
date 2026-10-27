#!/bin/sh
set -eu

ISO=${1:-}
if [ -z "$ISO" ] || [ ! -s "$ISO" ]; then
  echo "usage: $0 <SafeExamOS.iso>" >&2
  exit 2
fi

echo "Checking ISO: $ISO"

LIVE_LIST=$(xorriso -indev "$ISO" -ls /live 2>&1)

printf '%s
' "$LIVE_LIST"
printf '%s
' "$LIVE_LIST" | grep -q 'filesystem.squashfs'
printf '%s
' "$LIVE_LIST" | grep -Eq 'vmlinuz'
printf '%s
' "$LIVE_LIST" | grep -Eq 'initrd'

if [ -f "$ISO.sha256" ]; then
  (
    cd "$(dirname "$ISO")"
    sha256sum -c "$(basename "$ISO").sha256"
  )
fi

echo "ISO structure check: PASS"
