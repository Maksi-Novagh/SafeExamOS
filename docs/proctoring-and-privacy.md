# Proctoring and privacy

SafeExamOS may support supervision, but surveillance is not the default security primitive.

## Current upstream context

Safe Exam Browser already includes screen-proctoring functionality in current releases. The Windows source includes settings for screenshot intervals, image format/downscaling, local cache limits, metadata capture and a proctoring service URL.

SafeExamOS should investigate interoperability before inventing a competing protocol.

## Principles

- visible supervision indicator;
- data minimization;
- explicit institution policy;
- least intrusive feature that satisfies the exam requirement;
- bounded retention;
- encryption in transit;
- access auditing;
- no silent remote keyboard/mouse control during an exam;
- no raw keylogging by default.

## Event logging

Preferred baseline:

- policy violation attempts;
- device hotplug;
- display changes;
- network changes;
- blocked navigation;
- session state changes;
- integrity failures;
- supervisor actions.

Do not record the text typed into the exam as a generic audit feature.

## Screenshots

Recommended modes:

1. disabled;
2. security-event-triggered;
3. periodic, only when explicitly configured;
4. upstream-compatible screen-proctoring mode if interoperability is validated.

Each screenshot should be tied to:

- session;
- timestamp;
- reason/capture mode;
- retention policy;
- integrity metadata.

## Live view

If implemented:

- read-only by default;
- visible indicator on the candidate device;
- authenticated supervisor;
- every view session logged;
- no hidden input injection.

A separate assistance mode may allow remote control, but it should require explicit policy and a clear on-screen state change.

## Retention

The technical design should allow institutions to configure short retention periods and deletion. The software must not force indefinite storage.

## Legal note

Institutions are responsible for evaluating their legal basis, transparency duties, retention rules, DPIA requirements and local education/privacy law. SafeExamOS documentation should help administrators minimize data, not pretend that a technical feature automatically makes processing lawful.
