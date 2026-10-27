#!/bin/sh
set -eu

ISO=${1:-}
if [ -z "$ISO" ] || [ ! -s "$ISO" ]; then
  echo "usage: $0 <SafeExamOS.iso>" >&2
  exit 2
fi

for cmd in qemu-system-x86_64 xorriso; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "error: required command not found: $cmd" >&2
    exit 1
  }
done

mkdir -p .ci/qemu-root
LOG=.ci/qemu-serial.log
KERNEL=.ci/qemu-root/vmlinuz
INITRD=.ci/qemu-root/initrd.img
rm -f "$LOG" "$KERNEL" "$INITRD"

echo "Extracting kernel and initrd from ISO..."
xorriso -osirrox on -indev "$ISO"   -extract /live/vmlinuz "$KERNEL"   -extract /live/initrd.img "$INITRD" >/dev/null 2>&1

test -s "$KERNEL"
test -s "$INITRD"

echo "Booting SafeExamOS userspace under QEMU..."
echo "Mode: direct kernel/initrd smoke test"

set +e
timeout 180 qemu-system-x86_64   -machine q35,accel=tcg   -cpu max   -m 2048   -smp 2   -kernel "$KERNEL"   -initrd "$INITRD"   -append "boot=live components quiet console=ttyS0,115200n8 username=exam hostname=safeexamos locales=en_US.UTF-8 keyboard-layouts=us"   -drive "file=$ISO,media=cdrom,readonly=on,format=raw"   -device virtio-net-pci,netdev=n0   -netdev user,id=n0   -display none   -serial "file:$LOG"   -no-reboot
RC=$?
set -e

if grep -q 'SAFEEXAMOS_CI_BOOT_OK' "$LOG"; then
  echo "QEMU userspace smoke test: PASS"
  exit 0
fi

echo "error: guest never emitted SAFEEXAMOS_CI_BOOT_OK" >&2
echo "qemu exit code: $RC" >&2
tail -n 160 "$LOG" >&2 || true
exit 1
