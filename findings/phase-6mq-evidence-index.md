# Phase 6MQ evidence index — AmazonProfileService launcher-helper closure

Generated: 2026-08-10
Scope: host-only; no device contact, Binder call, mutation, reboot, exploit, or partition write.

## 6MQ-E01

- Source: preserved PS7331 fosservices disassembly
- File: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `2026-08-10` (host generation date)
- Command: `python3 tools/scripts/audit_phase6mq_profile_launcher_helper.py`
- Observed result: `initiateLauncher()` calls `access$6400()`, logs `Initiate launcher`, returns `AmazonProfileManager.SUCCESS`; no launch or package-state instruction in the window.
- Interpretation: the method name does not identify a HOME launch sink.
- Confidence: Confirmed
- Related hypothesis: `AmazonProfileService.initiateLauncher` directly forces Fire Launcher — Disproved (bounded).

## 6MQ-E02

- Source: preserved PS7331 fosservices disassembly
- File: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `2026-08-10`
- Command: exact line-window extraction, `78685-78691`
- Observed result: synthetic bridge calls `enforceProfileInteractionPermissions()` and returns.
- Interpretation: `initiateLauncher` is permission-gated through the profile interaction check.
- Confidence: Confirmed
- Related hypothesis: shell can use this helper without the required private permission — not supported by this evidence.

## 6MQ-E03

- Source: preserved PS7331 fosservices disassembly
- File: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `2026-08-10`
- Command: exact line-window extraction, `78949-78966`
- Observed result: checks `com.amazon.device.permission.PROFILE_INTERACTION` with process and user IDs and throws `SecurityException` on denial.
- Interpretation: the observed permission gate is explicit; no private Binder replay was attempted.
- Confidence: Confirmed
- Related hypothesis: unprivileged direct access to `initiateLauncher` is available — not supported.

## 6MQ-E04

- Source: preserved PS7331 fosservices disassembly
- File: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `2026-08-10`
- Command: exact line-window extraction, `77222-77280`
- Observed result: explicit configured package/activity is launched with `startActivityAsUser` for `ActivityManager.getCurrentUser()`.
- Interpretation: this is a profile-picker path, not a HOME resolver or preferred-activity writer.
- Confidence: Confirmed
- Related hypothesis: the profile picker method directly selects Fire Launcher for HOME — Disproved (bounded).

## 6MQ-E05

- Source: preserved PS7331 fosservices disassembly
- File: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `2026-08-10`
- Command: exact line-window extraction, `80813-80823`
- Observed result: `amazonprofileservice` Binder publication, local service publication, and package receiver registration.
- Interpretation: identifies the service publication boundary; it does not prove a HOME writer.
- Confidence: Confirmed
- Related hypothesis: service existence alone proves HOME control — Disproved.

## 6MQ-E06

- Source: preserved PS7331 fosservices disassembly
- File: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `2026-08-10`
- Command: bounded scan of lines `74942-77607`
- Observed result: no `setHomeActivity`, preferred-activity writer, package/component enabled-state writer, `com.amazon.firelauncher`, `CATEGORY_HOME`, or `ACTION_MAIN`; the only `startActivityAsUser` hit is the profile picker window.
- Interpretation: strong bounded negative for this BinderService class slice only.
- Confidence: Strong evidence
- Related hypothesis: this class slice directly implements the Fire Launcher HOME enforcement — not supported.

## Safety disposition

`service call amazonprofileservice ...`, guessed transaction codes, intent replay,
package-state mutation, Fire Launcher disable/hide/suspend/force-stop/clear,
Root/exploit execution, OTA/recovery/fastboot, and partition writes were not
performed. Such actions remain **因風險拒絕測試** for this static closure.
