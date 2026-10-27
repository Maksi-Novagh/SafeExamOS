# Development policy

These rules apply to every SafeExamOS change.

## 1. Document as we build

Every meaningful implementation change must update documentation in the same change or explicitly state why documentation is unaffected.

Depending on the change, update one or more of:

- architecture;
- threat model;
- compatibility matrix;
- hardware support;
- design system;
- testing notes;
- roadmap;
- research notes.

Do not allow the codebase to become the only source of architectural truth.

## 2. Evidence before compatibility claims

No feature is described as SEB-compatible without:

- an upstream reference;
- a reproducible test;
- documented platform/version scope.

## 3. UI consistency is mandatory

All UI work follows `docs/design-system.md`.

New screens should derive from current Safe Exam Browser UI/site patterns. Any divergence must be documented and justified.

## 4. Security-sensitive changes

Any change touching:

- privilege;
- boot;
- browser containment;
- device policy;
- configuration parsing;
- network policy;
- proctoring;
- updates;

must include:

- threat-model impact;
- tests;
- failure behavior;
- rollback/recovery notes where relevant.

## 5. Keep research snapshots dated

Upstream SEB evolves. Research that can become stale belongs under:

`docs/research/YYYY-MM-DD-*.md`

Living design documents should link to the relevant snapshot.

## 6. Prefer small auditable components

Avoid large privileged services and hidden magic. Prefer explicit state machines, typed configuration and narrow IPC.

## 7. Repository freshness

At the beginning of active development sessions:

1. inspect the current SafeExamOS main branch;
2. inspect relevant upstream SEB changes if the work depends on them;
3. update dated research notes when upstream behavior materially changed;
4. then implement.

This is a workflow rule, not a promise of background maintenance while no development session is active.
