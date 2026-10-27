# SafeExamOS image build

Status: **prototype**

The first build target is a Debian 13 (Trixie) amd64 live ISO created with Debian `live-build`.

This is intentionally a small proof of concept. It is **not yet hardened enough for real examinations**.

## Requirements

On a Debian 13 build host:

```bash
sudo apt update
sudo apt install live-build
```

## Build

```bash
cd build/amd64
sudo ./build.sh
```

Expected output: `out/SafeExamOS-amd64.iso`.

The prototype contains Debian 13, Chromium, Cage, NetworkManager, firmware packages, the local SafeExamOS launcher, and no full desktop environment.

See `docs/build-amd64.md`, `docs/threat-model.md`, and `ROADMAP.md` before interpreting this as a secure exam image.
