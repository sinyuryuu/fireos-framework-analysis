# Phase 7B — Amazon Framework/System Services IPC residual audit

Generated: 2026-08-10 (Asia/Taipei)

## Scope and safety

Baseline is public commit `6aa818a0f`, `findings/phase-6x4-report.md`, and `output/tables/phase6x4-control-surface.csv`. This worker read only the existing fosservices/boot-fosframework VDEX disassembly, service-context/SELinux inventory, manifests, fosinit XML, Phase 6 worker ledgers, and saved captures. It did not send a service call, Binder transaction, intent broadcast, APK install, device mutation, exploit, or root attempt, and did not modify device state.

The CSV records the required chain for each residual: caller → gate → Binder identity → user scope → exact sink → observed effect. Status values are deliberately limited to `unknown`, `bounded-negative`, and `duplicate`.

## Results

15 routes were audited: 4 `unknown`, 7 `bounded-negative`, and 4 `duplicate`.

The only material unresolved edges are provenance edges: the external caller and tx3-specific authorization for `AmazonUserManagerService`, the permission-holder/caller and target-user validation for prewarm, the downstream DPM→PMS caller join, the production caller for exported `SettingsProvider`, and the local DCPMS Binder bind caller. These are evidence gaps, not observed bypasses.

KFT component/application writers are bounded to the supplied `UserInfo.id` child/profile path. No recovered writer restores a Fire-specific User-0 preferred HOME. Launcher hijack prevention is an in-process visibility/permission callback, while key policy and the Amazon Activity callback are system_server callbacks rather than externally callable Binder routes.

SystemUI keyguard rows are retained as `duplicate` because Phase 6x4 already recorded the exact `IAmazonKeyguardService` methods and their `CONTROL_KEYGUARD`/Amazon permission checks. SettingsProvider remains `unknown` at caller provenance despite a statically real exported provider writer; the bounded implementation retains Binder caller identity and enforces WRITE permissions/cross-user resolution.

## Evidence and limitations

The principal binary evidence hashes are:

- fosservices disassembly: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- boot-fosframework disassembly: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Phase 6x4 report: `71ec3dbc4e895cc79068b7d3bfd17dfd55d8488b9ebb2449ba720a4e2cd48c7e`
- Phase 6x4 baseline CSV: `b6a3ad87a24e4fc185a29dc18c92c4144889ad19e6283ac9a17db762b10a52fc`

`evidence_sha256` in the CSV is the SHA-256 of each referenced existing artifact where available; combined evidence lists use semicolon-separated hashes in the same order. Existing captures are observations only and do not imply a fresh runtime test.

No claim is made that every service or future build is safe. Closure would require the missing caller/permission/identity/user-scope joins identified in `missing_edge`; obtaining them must remain host-only unless separately authorized.
