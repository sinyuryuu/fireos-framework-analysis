# Phase 6AF evidence index：PS7331 `OtaDexoptService` implementation closure

## E6AF-01 — concrete service class

- **Source:** PS7331 services VDEX disassembly
- **File:** `decompiled/baksmali/vdexExtractor/services/disassembly.log:482129-482734`
- **SHA-256:** `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`
- **Test ID:** `PHASE6AF-HOST-OTADEXOPT-IMPLEMENTATION-20260805-03`
- **Timestamp:** 2026-08-05 host analysis
- **Command:** `python3 tools/scripts/audit_phase6af_otadexopt_implementation.py ...`
- **Observed result:** `com.android.server.pm.OtaDexoptService` is present with `main`, `prepare`, `cleanup`, `isDone`, `getProgress`, `nextDexoptCommand`, `dexoptNextPackage`, and `onShellCommand`.
- **Interpretation:** Phase 6AE's old implementation gap is closed; the class is present in the saved artifact.
- **Confidence:** Confirmed
- **Related hypothesis:** implementation was absent from the saved PS7331 scope.

## E6AF-02 — service registration and startup gate

- **Source:** installed and adjacent PS7331 VDEX disassemblies
- **File:** `decompiled/baksmali/vdexExtractor/services/disassembly.log:107990-108045,482249-482263`; `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:2585840-2585895`
- **SHA-256:** `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`; `04d68d0bb562a14e9cbff3bdce63b66eb911ee4bb7e728ca77cd435a5b03c146`
- **Test ID:** `PHASE6AF-HOST-OTADEXOPT-IMPLEMENTATION-20260805-03`
- **Timestamp:** 2026-08-05 host analysis
- **Command:** host parser, no device contact
- **Observed result:** `SystemServer` checks `mOnlyCore` and `config.disable_otadexopt`, then calls `OtaDexoptService.main`; `main` publishes `otadexopt` through `ServiceManager.addService`.
- **Interpretation:** the service is a normal system-server OTA dexopt surface, not an Amazon HOME-specific service.
- **Confidence:** Confirmed
- **Related hypothesis:** service publication might be a private Amazon-only privilege route.

## E6AF-03 — command side effects

- **Source:** method-level disassembly
- **File:** `decompiled/baksmali/vdexExtractor/services/disassembly.log:482460-482734`
- **SHA-256:** `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`
- **Test ID:** `PHASE6AF-HOST-OTADEXOPT-IMPLEMENTATION-20260805-03`
- **Timestamp:** 2026-08-05 host analysis
- **Command:** host parser
- **Observed result:** `prepare` builds command state and may call `deleteOatArtifactsOfPackage` on low space; `next` removes/clears command state; `cleanup` clears state; `step` throws `UnsupportedOperationException` in this build.
- **Interpretation:** these commands are not safe read probes and remain risk-rejected.
- **Confidence:** Confirmed / risk-rejected
- **Related hypothesis:** a shell-visible OTA dexopt command may be a safe mutable research surface.

## E6AF-04 — runtime implementation identity

- **Source:** preserved read-only device status capture
- **File:** `adb/phase6ae/PHASE6AE-STATUS-20260805-01/metadata.json`; `otadexopt_done.stderr.txt`; `otadexopt_progress.stdout.txt`
- **SHA-256:** `85609bc93c8ab417efb549cbe0434333868a4f60bb547dc6352499d526b3c180`; `3bb2d44c2c1eaebabd18dbd4ea8f30d23eff2463d7324d7ca09c2190a9e40ccb`; `cf9dcf6da8a82be1335c398a4005def7ee3a53d4698c59dbc6b2b14e72d1263c`
- **Test ID:** `PHASE6AE-STATUS-20260805-01`
- **Timestamp:** 2026-08-04T23:14:25.904524Z
- **Command:** `cmd otadexopt done`; `cmd otadexopt progress`
- **Observed result:** `done` stack names `OtaDexoptService.java:176`, `OtaDexoptShellCommand.java:76`, and `IOtaDexopt$Stub.onTransact`; `progress` returns `1.00`.
- **Interpretation:** the documented shell path reached the installed concrete service. No mutating command was invoked.
- **Confidence:** Confirmed
- **Related hypothesis:** the listed Binder interface might not map to the recovered implementation.

## E6AF-05 — no HOME or root route

- **Source:** static implementation and same-capture HOME resolver
- **File:** `artifacts/phase6af/otadexopt-implementation-closure-20260805-03/implementation.json`; `adb/phase6ae/PHASE6AE-STATUS-20260805-01/home_resolve.stdout.txt`
- **SHA-256:** `93433acfd46b808212cd20ffa77d86cf8e2f7a8154e4ba1d52b73ae59d99db13`; `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`
- **Test ID:** `PHASE6AF-HOST-OTADEXOPT-IMPLEMENTATION-20260805-03`; `PHASE6AE-STATUS-20260805-01`
- **Timestamp:** 2026-08-05 host analysis / 2026-08-04T23:14:25.904524Z capture
- **Command:** host parser and preserved HOME resolve capture
- **Observed result:** no Fire Launcher comparison, HOME selector, privilege transition, or root primitive was found; HOME remained `com.amazon.firelauncher/.Launcher` with priority 50.
- **Interpretation:** `otadexopt` is not a demonstrated workaround or escalation route.
- **Confidence:** Strong evidence
- **Related hypothesis:** OTA dexopt service controls HOME or grants a low-privilege escalation.

## Safety record

No `prepare`, `step`, `next`, or `cleanup` command was run. No private Binder
transaction, OOBE broadcast, OTA/recovery action, package/settings mutation,
reboot, Root, or partition write was performed.
