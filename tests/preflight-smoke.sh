#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
COLLECTOR="$ROOT/build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-preflight"
command -v node >/dev/null 2>&1 || { echo "node is required to validate the generated JavaScript" >&2; exit 2; }
command -v timeout >/dev/null 2>&1 || { echo "timeout is required" >&2; exit 2; }
TEMP=$(mktemp -d)
trap 'rm -rf "$TEMP"' EXIT HUP INT TERM
mkdir -p "$TEMP/bin" "$TEMP/out"
cat > "$TEMP/bin/nmcli" <<'SH'
#!/bin/sh
sleep 60
SH
chmod 0755 "$TEMP/bin/nmcli"
start=$(date +%s)
PATH="$TEMP/bin:$PATH" sh "$COLLECTOR" "$TEMP/out"
elapsed=$(($(date +%s)-start))
if [ "$elapsed" -gt 12 ]; then
  echo "Pre-flight unexpectedly slow: $elapsed seconds" >&2
  exit 1
fi
node - "$TEMP/out/preflight.js" <<'NODE'
const fs=require("node:fs");
const vm=require("node:vm");
const assert=require("node:assert/strict");
const scope={window:{}};
vm.runInNewContext(fs.readFileSync(process.argv[2],"utf8"),scope,{timeout:1000});
const p=scope.window.SAFEEXAMOS_PREFLIGHT;
assert.equal(p.collectorStatus,"ok");
assert.equal(p.network.managerState,"unknown");
assert.ok(Number.isInteger(p.memoryMiB) && p.memoryMiB > 0);
assert.ok(typeof p.cpu==="string");
NODE
echo "Pre-flight bounded-network smoke test: PASS"
