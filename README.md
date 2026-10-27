# SafeExamOS

**A bootable, ephemeral examination operating system designed for the Safe Exam Browser ecosystem.**

SafeExamOS aims to turn almost any compatible computer into a clean, predictable and secure examination workstation without depending on the student's installed operating system.

Boot from USB, select a network, load a `.seb` configuration or enter an exam code, and start the examination.

After shutdown, the examination environment disappears.

## Why?

Safe Exam Browser provides a secure examination environment on supported operating systems. SafeExamOS explores a complementary approach:

**Instead of securing the student's existing operating system, boot into an operating system built specifically for the exam.**

This can provide:

- a known and reproducible system state;
- reduced interference from installed software;
- disposable exam sessions;
- hardware pre-flight checks;
- centralized supervision and event logging;
- compatibility with `.seb` configurations;
- support for institution-managed and BYOD computers;
- AMD64 and ARM64 builds, with additional architectures planned.

## Intended workflow

```text
Power on
   ↓
Boot SafeExamOS
   ↓
Hardware & network check
   ↓
Enter exam code / URL
or load .seb file
   ↓
Validate configuration
   ↓
Enter locked exam environment
   ↓
Complete examination
   ↓
Submit
   ↓
Shutdown
   ↓
Session data destroyed
```

## Project goals

SafeExamOS is intended to investigate and develop:

- a Linux-based examination kiosk;
- Safe Exam Browser configuration compatibility;
- hardware compatibility detection;
- signed and immutable system images;
- ephemeral user sessions;
- Chromium-based restricted browsing;
- configurable USB and Bluetooth policies;
- event-based examination auditing;
- optional read-only live screen supervision;
- integration with SEB Server and existing LMS platforms;
- multi-architecture builds.

## Non-goals

SafeExamOS is **not** intended to bypass or weaken Safe Exam Browser.

The project is focused on secure examination infrastructure, interoperability, defensive security research and improving the reliability of digital examinations.

## Status

🚧 **Early research and prototyping**

SafeExamOS is currently an independent community project and is **not affiliated with or endorsed by the Safe Exam Browser project, ETH Zürich or the SEB Alliance.**

We would however strongly welcome discussion and collaboration with the Safe Exam Browser community.
