# Phase 6C futex/policy surface audit

Host-only; no ADB, ELF execution, futex trigger, kernel memory access, or payload.

- Text files scanned outside kernel paths: 7135
- Named non-kernel REQUEUE_PI source hits: 0
- Policy-named files outside kernel paths: 0
- Native named REQUEUE_PI files: 0

No policy file or marker result is an absence proof; indirect/stripped/unpulled callers remain unverified.
