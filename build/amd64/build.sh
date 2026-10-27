#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
WORK_DIR="${SAFEEXAMOS_BUILD_DIR:-$ROOT_DIR/.build/amd64}"
OUT_DIR="$ROOT_DIR/build/amd64/out"

if [ "$(id -u)" -ne 0 ]; then
  echo "error: run this prototype build as root" >&2
  exit 1
fi

if ! command -v lb >/dev/null 2>&1; then
  echo "error: live-build is not installed (apt install live-build)" >&2
  exit 1
fi

rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR" "$OUT_DIR"
cd "$WORK_DIR"

lb config noauto \
  --mode debian \
  --distribution trixie \
  --architectures amd64 \
  --binary-images iso-hybrid \
  --debian-installer none \
  --archive-areas "main contrib non-free-firmware" \
  --apt-recommends true \
  --memtest none \
  --iso-application "SafeExamOS" \
  --iso-publisher "SafeExamOS community project" \
  --iso-volume "SAFEEXAMOS" \
  --bootappend-live "boot=live components quiet username=exam hostname=safeexamos locales=en_US.UTF-8 keyboard-layouts=us"

cp -a "$ROOT_DIR/build/amd64/config/." "$WORK_DIR/config/"

lb build

IMAGE=$(find . -maxdepth 1 -type f -name "*.iso" | head -n 1)
if [ -z "$IMAGE" ]; then
  echo "error: build completed but no ISO was found" >&2
  exit 1
fi

cp "$IMAGE" "$OUT_DIR/SafeExamOS-amd64.iso"
(
  cd "$OUT_DIR"
  sha256sum "SafeExamOS-amd64.iso" > "SafeExamOS-amd64.iso.sha256"
)

echo "SafeExamOS prototype image: $OUT_DIR/SafeExamOS-amd64.iso"
