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
KERNEL=.ci/qemu-ui/vmlinuz
INITRD=.ci/qemu-ui/initrd.img

rm -f "$LOG" "$MON" "$PPM" "$KERNEL" "$INITRD"

xorriso -osirrox on -indev "$ISO"   -extract /live/vmlinuz "$KERNEL"   -extract /live/initrd.img "$INITRD" >/dev/null 2>&1

test -s "$KERNEL"
test -s "$INITRD"

qemu-system-x86_64   -machine q35,accel=tcg   -cpu max   -m 2048   -smp 2   -kernel "$KERNEL"   -initrd "$INITRD"   -append "boot=live components quiet console=ttyS0,115200n8 username=exam hostname=safeexamos locales=en_US.UTF-8 keyboard-layouts=us"   -drive "file=$ISO,media=cdrom,readonly=on,format=raw"   -device virtio-vga   -device virtio-net-pci,netdev=n0   -netdev user,id=n0   -display none   -serial "file:$LOG"   -monitor "unix:$MON,server,nowait"   -no-reboot   >/dev/null 2>&1 &

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
deadline=$(( $(date +%s) + 150 ))
while [ "$(date +%s)" -lt "$deadline" ]; do
  if grep -q 'SAFEEXAMOS_CI_UI_OK' "$LOG" 2>/dev/null; then
    echo "Graphical runtime marker received."
    break
  fi

  if ! kill -0 "$QEMU_PID" 2>/dev/null; then
    echo "error: QEMU exited before graphical runtime became ready" >&2
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

printf 'screendump %s\n' "$PPM" | socat - "UNIX-CONNECT:$MON" >/dev/null
sleep 1

test -s "$PPM"
header=$(head -n 3 "$PPM" | tr "\n" " ")
printf '%s\n' "$header" | grep -Eq '^P6 [0-9]+ [0-9]+ 255 ' || {
  echo "error: invalid PPM framebuffer header: $header" >&2
  exit 1
}

echo "Captured graphical framebuffer: $PPM"
echo "QEMU graphical smoke test: PASS"
