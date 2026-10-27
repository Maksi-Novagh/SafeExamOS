# Contributing to SafeExamOS

SafeExamOS is an early security-sensitive research project.

## Before coding

Please read:

- `docs/architecture.md`
- `docs/threat-model.md`
- `docs/seb-compatibility.md`
- `SECURITY.md`

## Contribution rules

- Do not add features whose purpose is to bypass Safe Exam Browser or facilitate exam cheating.
- Security research should be reproducible in a lab and aimed at hardening.
- Do not publish a working upstream zero-day before responsible disclosure.
- Do not silently weaken fail-closed behavior.
- Do not add hidden keylogging, hidden webcam/microphone capture or covert remote control.
- Avoid running the graphical UI as root.
- Security-sensitive parsing and privileged code requires tests.
- Document architecture-specific behavior.

## Pull requests

A PR should explain:

1. what problem it solves;
2. threat-model impact;
3. supported architectures;
4. how it was tested;
5. whether it changes `.seb` compatibility;
6. whether it changes privacy/data collection.

## Compatibility claims

Do not label a feature "SEB compatible" without a test demonstrating the intended behavior against documented/reference behavior.

## Upstream code

Safe Exam Browser has its own licenses. If code is adapted or copied, preserve all required notices and document provenance. Prefer clean, independently implemented interfaces when practical.
