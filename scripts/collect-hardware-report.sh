#!/bin/sh
set -eu

OUT=${1:-safeexamos-hardware-report.txt}

{
  echo "SafeExamOS hardware report"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "== System =="
  uname -a || true
  echo
  echo "== CPU =="
  awk -F: '/model name|Hardware|Processor/ {gsub(/^[ 	]+/,"",$2); print $2; exit}' /proc/cpuinfo 2>/dev/null || true
  echo
  echo "== Memory =="
  grep -E 'MemTotal|MemAvailable' /proc/meminfo 2>/dev/null || true
  echo
  echo "== Firmware =="
  if [ -d /sys/firmware/efi ]; then echo UEFI; else echo BIOS; fi
  echo
  echo "== PCI =="
  lspci -nnk 2>/dev/null || true
  echo
  echo "== USB =="
  lsusb 2>/dev/null || true
  echo
  echo "== Network =="
  ip -brief link 2>/dev/null || true
  nmcli -f DEVICE,TYPE,STATE,CONNECTION device status 2>/dev/null || true
  echo
  echo "== DRM =="
  for f in /sys/class/drm/card*-*/status; do
    [ -r "$f" ] || continue
    printf '%s: %s\n' "$(basename "$(dirname "$f")")" "$(cat "$f")"
  done
  echo
  echo "== Input =="
  grep -E '^(N: Name=|H: Handlers=)' /proc/bus/input/devices 2>/dev/null || true
  echo
  echo "== Power =="
  for d in /sys/class/power_supply/*; do
    [ -d "$d" ] || continue
    echo "[$(basename "$d")]"
    for f in type status capacity manufacturer model_name; do
      [ -r "$d/$f" ] && printf '%s=%s\n' "$f" "$(cat "$d/$f")"
    done
  done
  echo
  echo "== Loaded graphics/network/input modules =="
  lsmod 2>/dev/null | grep -Ei 'amdgpu|i915|nouveau|iwl|rtw|ath|mt76|r8169|igc|e1000|hid|i2c_hid|psmouse' || true
} > "$OUT"

echo "Hardware report written to $OUT"
