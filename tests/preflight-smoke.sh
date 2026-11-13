#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
COLLECTOR="$ROOT/build/amd64/config/includes.chroot/usr/local/sbin/safeexamos-preflight"
FALLBACK="$ROOT/build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/preflight.js"
command -v node >/dev/null 2>&1 || { echo "node is required" >&2; exit 2; }
command -v timeout >/dev/null 2>&1 || { echo "GNU timeout is required" >&2; exit 2; }
TEMP=$(mktemp -d)
trap 'rm -rf "$TEMP"' EXIT HUP INT TERM
mkdir -p "$TEMP/bin" "$TEMP/out"
cp "$FALLBACK" "$TEMP/out/preflight.js"
cat > "$TEMP/bin/nmcli" <<'SH'
#!/bin/sh
sleep 60
SH
chmod 0755 "$TEMP/bin/nmcli"
node - "$TEMP/out/preflight.js" <<'NODE'
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const scope={window:{}};
vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8'),scope,{timeout:1000});
assert.equal(scope.window.SAFEEXAMOS_PREFLIGHT.collectorStatus,'degraded');
NODE
start=$(date +%s)
PATH="$TEMP/bin:$PATH" timeout -k 2s 16s sh "$COLLECTOR" "$TEMP/out"
elapsed=$(( $(date +%s) - start ))
[ "$elapsed" -le 14 ] || { echo "preflight took too long: $elapsed seconds" >&2; exit 1; }
node - "$TEMP/out/preflight.js" <<'NODE'
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const scope={window:{}};
vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8'),scope,{timeout:1000});
const d=scope.window.SAFEEXAMOS_PREFLIGHT;
assert.equal(d.collectorStatus,'ok');
assert.equal(d.network.managerState,'unknown');
assert.equal(d.network.wifiInterfaces,'none');
assert.ok(d.memoryMiB>0);
assert.ok(typeof d.gpu==='string');
NODE
printf 'Preflight timeout/fail-closed snapshot test: PASS (%ss)\n' "$elapsed"
