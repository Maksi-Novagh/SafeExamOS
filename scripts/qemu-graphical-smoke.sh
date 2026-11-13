#!/bin/sh
set -eu

ISO=${1:-}
if [ -z "$ISO" ] || [ ! -s "$ISO" ]; then
  echo "usage: $0 <SafeExamOS.iso>" >&2
  exit 2
fi

for cmd in qemu-system-x86_64 xorriso socat; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "error: required command not found: $cmd" >&2
    exit 1
  }
done

mkdir -p .ci/qemu-ui
LOG=.ci/qemu-ui/serial.log
MON=.ci/qemu-ui/monitor.sock
PPM=.ci/qemu-ui/safeexamos-ui.ppm
QEMU_ERR=.ci/qemu-ui/qemu-stderr.log
KERNEL=.ci/qemu-ui/vmlinuz
INITRD=.ci/qemu-ui/initrd.img

rm -f "$LOG" "$MON" "$PPM" "$QEMU_ERR" "$KERNEL" "$INITRD"

xorriso -osirrox on -indev "$ISO"   -extract /live/vmlinuz "$KERNEL"   -extract /live/initrd.img "$INITRD" >/dev/null 2>&1

test -s "$KERNEL"
test -s "$INITRD"

qemu-system-x86_64   -machine q35,accel=tcg   -cpu max   -m 2048   -smp 2   -kernel "$KERNEL"   -initrd "$INITRD"   -append "boot=live components quiet console=ttyS0,115200n8 username=exam hostname=safeexamos locales=en_US.UTF-8 keyboard-layouts=us"   -drive "file=$ISO,media=cdrom,readonly=on,format=raw"   -device virtio-vga   -device virtio-net-pci,netdev=n0   -netdev user,id=n0   -display none   -serial "file:$LOG"   -monitor "unix:$MON,server,nowait"   -no-reboot   >/dev/null 2>"$QEMU_ERR" &

QEMU_PID=$!
cleanup() {
  if kill -0 "$QEMU_PID" 2>/dev/null; then
    kill "$QEMU_PID" 2>/dev/null || true
    wait "$QEMU_PID" 2>/dev/null || true
  fi
  rm -f "$MON"
}
trap cleanup EXIT INT TERM

echo "Waiting for Cage + Chromium launcher..."
deadline=$(( $(date +%s) + 240 ))
while [ "$(date +%s)" -lt "$deadline" ]; do
  if grep -q 'SAFEEXAMOS_CI_UI_OK' "$LOG" 2>/dev/null; then
    echo "Graphical runtime marker received."
    break
  fi

  if ! kill -0 "$QEMU_PID" 2>/dev/null; then
    set +e
    wait "$QEMU_PID"
    qemu_rc=$?
    set -e
    echo "error: QEMU exited before graphical runtime became ready (exit=$qemu_rc)" >&2
    echo "--- QEMU stderr ---" >&2
    tail -n 200 "$QEMU_ERR" >&2 || true
    echo "--- guest serial ---" >&2
    tail -n 200 "$LOG" >&2 || true
    exit 1
  fi

  sleep 2
done

if ! grep -q 'SAFEEXAMOS_CI_UI_OK' "$LOG" 2>/dev/null; then
  echo "error: graphical runtime marker not received" >&2
  tail -n 200 "$LOG" >&2 || true
  exit 1
fi

# Wait for actual painted launcher pixels instead of only Chromium process startup.
# CI runs QEMU without GPU acceleration, so allow several display frames to settle.
ready=0
frame_deadline=$(( $(date +%s) + 60 ))
while [ "$(date +%s)" -lt "$frame_deadline" ]; do
  printf 'screendump %s\n' "$PPM" | socat - "UNIX-CONNECT:$MON" >/dev/null || true
  sleep 2
  if test -s "$PPM" && python3 ./scripts/verify-framebuffer.py "$PPM"; then
    ready=1
    break
  fi
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  echo "error: Cage/Chromium processes started but launcher pixels are not visible" >&2
  tail -n 100 "$LOG" >&2 || true
  exit 1
fi

# Exercise the real QEMU input channel. Chromium focuses the typing-test field.
# The second framebuffer must change visually after the key is delivered.
PPM_TYPED=.ci/qemu-ui/safeexamos-after-input.ppm
rm -f "$PPM_TYPED"
printf 'sendkey a\n' | socat - "UNIX-CONNECT:$MON" >/dev/null
sleep 3
printf 'screendump %s\n' "$PPM_TYPED" | socat - "UNIX-CONNECT:$MON" >/dev/null
sleep 1
test -s "$PPM_TYPED"
python3 ./scripts/verify-framebuffer.py "$PPM" --after-input "$PPM_TYPED"

echo "Captured graphical framebuffer: $PPM"
echo "Captured keyboard response framebuffer: $PPM_TYPED"
echo "QEMU graphical smoke test: PASS"
