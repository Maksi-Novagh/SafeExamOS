#!/bin/sh
set -eu

echo "SafeExamOS runtime metrics"
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

echo "== Memory =="
free -m 2>/dev/null || true
echo

echo "== Processes =="
ps -eo pid,comm,rss,%mem,%cpu --sort=-rss 2>/dev/null | head -n 20 || true
echo

echo "== Boot timing =="
systemd-analyze 2>/dev/null || true
echo

echo "== Critical chain =="
systemd-analyze critical-chain safeexamos-kiosk.service 2>/dev/null || true
echo

echo "== Enabled services =="
systemctl list-unit-files --type=service --state=enabled --no-legend 2>/dev/null || true
echo

echo "== Running services =="
systemctl list-units --type=service --state=running --no-legend 2>/dev/null || true
