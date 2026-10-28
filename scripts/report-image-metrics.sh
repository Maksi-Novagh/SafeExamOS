#!/bin/sh
set -eu

ISO=${1:-build/amd64/out/SafeExamOS-amd64.iso}

if [ ! -s "$ISO" ]; then
  echo "error: ISO not found: $ISO" >&2
  exit 2
fi

for cmd in stat xorriso; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "error: required command not found: $cmd" >&2
    exit 1
  }
done

iso_bytes=$(stat -c %s "$ISO")
iso_mib=$(( (iso_bytes + 1048575) / 1048576 ))

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT INT TERM

xorriso -osirrox on -indev "$ISO" -extract /live/filesystem.squashfs "$tmp_dir/filesystem.squashfs" >/dev/null 2>&1
squash_bytes=$(stat -c %s "$tmp_dir/filesystem.squashfs")
squash_mib=$(( (squash_bytes + 1048575) / 1048576 ))

packages="unknown"
if xorriso -osirrox on -indev "$ISO" -extract /live/filesystem.packages "$tmp_dir/filesystem.packages" >/dev/null 2>&1; then
  packages=$(wc -l < "$tmp_dir/filesystem.packages" | tr -d ' ')
fi

cat <<EOF
SafeExamOS image metrics
ISO: $ISO
ISO bytes: $iso_bytes
ISO MiB: $iso_mib
SquashFS bytes: $squash_bytes
SquashFS MiB: $squash_mib
Package entries: $packages
EOF
