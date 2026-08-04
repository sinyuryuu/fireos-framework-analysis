# Phase 5P futex applicability gates

- Test ID: PHASE5BL-FUTEX-GATES-20260804-01
- Serial: G001LT0511550CFT
- Timestamp UTC: 2026-08-04T04:50:28Z
- Read-only: yes
- Futex/PI trigger: no
- Device state mutation: no

Failures of individual read-only proc/sysctl reads are preserved and are not
treated as evidence that a feature is enabled or disabled.
