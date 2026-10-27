#!/bin/sh
set -eu

ISO=${1:-}
if [ -z "$ISO" ] || [ ! -s "$ISO" ]; then
  echo "usage: $0 <SafeExamOS.iso>" >&2
  exit 2
fi

mkdir -p .ci
LOG=.ci/qemu-serial.log
rm -f "$LOG"

OVMF_CODE=""
for f in   /usr/share/OVMF/OVMF_CODE_4M.fd   /usr/share/OVMF/OVMF_CODE.fd   /usr/share/ovmf/OVMF.fd
do
  if [ -r "$f" ]; then
    OVMF_CODE=$f
    break
  fi
done

if [ -z "$OVMF_CODE" ]; then
  echo "error: OVMF firmware not found" >&2
  exit 1
fi

echo "Booting SafeExamOS under QEMU..."
echo "UEFI: $OVMF_CODE"

set +e
timeout 180 qemu-system-x86_64   -machine q35,accel=tcg   -cpu max   -m 2048   -smp 2   -drive "if=pflash,format=raw,readonly=on,file=$OVMF_CODE"   -cdrom "$ISO"   -boot d   -device virtio-net-pci,netdev=n0   -netdev user,id=n0   -display none   -serial "file:$LOG"   -no-reboot
RC=$?
set -e

if grep -q 'SAFEEXAMOS_CI_BOOT_OK' "$LOG"; then
  echo "QEMU boot smoke test: PASS"
  exit 0
fi

echo "error: guest never emitted SAFEEXAMOS_CI_BOOT_OK" >&2
echo "qemu exit code: $RC" >&2
tail -n 120 "$LOG" >&2 || true
exit 1
