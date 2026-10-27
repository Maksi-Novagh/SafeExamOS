# Security policy

SafeExamOS is not production-ready and currently makes **no security certification claim**.

## Reporting vulnerabilities

Please do not publish an immediately exploitable vulnerability in an issue when it could affect real exam deployments or upstream Safe Exam Browser users.

Until a dedicated private disclosure channel is configured:

- for SafeExamOS-only design weaknesses that are not exploitable in production, a GitHub issue is acceptable;
- for serious vulnerabilities, contact the repository owner privately through an available GitHub contact method;
- if the issue affects upstream Safe Exam Browser, follow the upstream project's responsible-disclosure process.

## Scope

Security areas include:

- boot integrity;
- privilege boundaries;
- browser containment;
- session escape;
- device policy;
- network policy;
- configuration parsing;
- SEB interoperability;
- audit/proctoring integrity;
- privacy-sensitive data collection;
- update and supply-chain security.

## Research expectations

A useful security report includes:

- affected commit/image;
- hardware/architecture;
- exact preconditions;
- reproduction steps in a lab;
- expected vs actual result;
- impact;
- suggested mitigation if known.

Do not include real exam credentials, student data or production secrets.

## Safe research boundary

We welcome analysis of how exam-security controls can fail **for the purpose of strengthening them**. The project will not ship tooling whose primary purpose is escaping a real examination environment.
