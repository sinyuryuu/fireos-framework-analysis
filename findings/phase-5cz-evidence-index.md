# Phase 5CZ evidence index

## P5CZ-E01

- Source: read-only device capture
- File: `adb/phase5/PHASE5CZ-SELFTEST-PRESENCE-20260804-01/result.md`
- SHA-256: `a15fa18b7b15dd5da908f0603e81a4b7139ee7a61413bd30885c035f8d267e22`
- Observed: `device_matching_lines=0`; no matching futex/kselftest/rtmutex/
  requeue binary was observed in the bounded search.
- Confidence: **Confirmed negative observation**

## P5CZ-E02

- Source: read-only command record
- File: `adb/phase5/PHASE5CZ-SELFTEST-PRESENCE-20260804-01/commands.txt`
- Observed: explicit serial and bounded read-only `find` searches; no copy,
  execution, or invocation command.
- Confidence: **Confirmed**

## P5CZ-E03

- Source: PS7331 source index
- File: `adb/phase5/PHASE5CZ-SELFTEST-PRESENCE-20260804-01/source-selftest-index.txt`
- Observed: source paths include futex functional requeue-PI tests.
- Confidence: **Confirmed**

## P5CZ-E04

- Source: PS7331 kernel Makefile excerpt captured in the source index
- File: `artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/Makefile`
- Observed: kselftest build/run target and root/build/install/boot wording.
- Confidence: **Confirmed**

## P5CZ-E05

- Source: capture integrity record
- File: `adb/phase5/PHASE5CZ-SELFTEST-PRESENCE-20260804-01/sha256sums.txt`
- SHA-256: `ccf8013148a125e1c2b4299262ba36b321d20b6342f4328f554c1451139a3a66`
- Observed: raw capture files are hashed and preserved.
- Confidence: **Confirmed**
