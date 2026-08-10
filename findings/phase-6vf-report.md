# Phase 6VF — cross-launcher privilege-surface closure

Generation HEAD: `92c6596ca6315f783c88e99b72f0788ca68caaa4`.

## Scope and safety

This phase broadens the analysis beyond Fire Launcher to every preserved
high-impact surface that could plausibly change package/component state, HOME,
settings, user/profile state, trust/update state, native memory/IO state, or a
partition. Acceptance remains:

`caller → permission / SELinux / service-manager / lifecycle gate → identity and user scope → exact sink → observed effect`

The five worker ledgers below were produced by host-only analysis. No Binder
transaction, guessed service code, driver node/ioctl, OTA/recovery execution,
malformed input, reboot, package/settings mutation, Fire Launcher mutation,
Root/exploit attempt, or partition write was performed.

## Inputs

- **6VA fosinit residual closure:** `work/luna_worker_phase6va_fosinit_residual_closure_20260810.md` (b9b039d34a6d80e4483ce55bb71c16f3547d09339e9f40e6a2749ab70680fb55); `work/luna_worker_phase6va_fosinit_residual_closure_20260810.csv` (834676c20c53cb7910f2ed56f382fd4d90e0f04c56aaba23433a4b770c3eab2c); 15 row(s).
- **6VB OTA post-install closure:** `work/luna_worker_phase6vb_ota_postinstall_closure_20260810.md` (3489ce7b51e225ac05fa2439df5b2652100aa78a9becd68f719f777f5eb5873b); `work/luna_worker_phase6vb_ota_postinstall_closure_20260810.csv` (4eaeb6302d1fde0752bc052cd9c67b0b5ee1d3bac7f93935352dced1c36d3fd5); 13 row(s).
- **6VC native driver caller/policy closure:** `work/luna_worker_phase6vc_driver_caller_policy_20260810.md` (dda3425e4d6fca88aab7957689cc94209c0a31c919e455cdfa72379693122433); `work/luna_worker_phase6vc_driver_caller_policy_20260810.csv` (8bb5edcc5b5e1cf0bfb8e45cd14c1e185ac873c4d307e67594c024ccd3b69ad0); 7 row(s).
- **6VD existing-test reconciliation:** `work/luna_worker_phase6vd_test_reconciliation_20260810.md` (b129bdc5a15be77c1430a4a9585d0009d645822e2db9ee37ca5655ef1b85ab9e); `work/luna_worker_phase6vd_test_reconciliation_20260810.csv` (78462b8645a0c05bb134a0bae89a62cf154d0126c4aae24a93afe03d3be8a95e); 19 row(s).
- **6VE Framework IPC sink inventory:** `work/luna_worker_phase6ve_framework_sink_inventory_20260810.md` (9905f33d8cdc858a4bf59cfec8ef24f8d7a763db49f9cc0b33215de94eebae8a); `work/luna_worker_phase6ve_framework_sink_inventory_20260810.csv` (42d609d5d427fb691031e54caf9d25ee62718f9be64f7bf32fbc53d7eb88ab6a); 32 row(s).

Context hashes: `findings/phase-6ur-report.md` (cf9abf2d24bdcbe3486dd64f1bd23a7ffe82f804622964f0d996ac5db298340f); `output/tables/phase6ur-control-surface.csv` (2aadae1355ded824caa8409a69bcab31612793c7a002d39f83036d17b8b07d33); `findings/phase-6ui-readonly-snapshot.md` (0983f132483e235d82b35a0b0f42f7dd577666249c3b347c891e8e35773b5882); `output/tables/phase6ui-readonly-state.csv` (7cfe1aa24ac4eeffca6147935ebac6ed9f71e92cde31b669eeead92e3ffcdc5b)

## Cross-surface findings

### 已證實：privileged sinks exist, but are not low-privilege routes

The Framework inventory contains direct enabled-state and preferred/HOME sinks.
It also contains KFT child/profile-scoped writes, ProductPolicy package/component
writers, DPM/PMS sinks, Amazon user/settings writers, and recovery/update
partition writers. These are concrete code locations, not proof that shell or
an ordinary app can obtain the required handle or accepted identity.

### 高可信推論：User-0 formal HOME and package-state control remain protected

The saved PS7331 read-only snapshot still resolves User 0 HOME to Fire Launcher
at priority 50. The reconciled historical tests show ordinary preferred records,
package/component setters, accessibility/foreground redirects, child/KFT
lifecycle, DPM, settings/overlay, private IPC, OTA, driver and PI-futex routes
did not establish a sustainable User-0 HOME replacement or root transition.
KFT evidence is explicitly child/profile scoped; it must not be generalized to
User 0.

### 待驗證：bounded static gaps remain, but none authorizes live probing

The residual fosinit rows include unresolved caller/authz or receiver-side sink
details for CRL trust/update, tablet broadcast relay, package recency, settings,
factory-reset whitelist, FireOS OTA callback, and related lifecycle services.
The OTA audit still lacks complete recovery-to-updater identity/AVB handoff;
native CMDQ/ION/Amazon-LD joins lack all exact shipped node, policy and caller
edges. These gaps are finite host-side closure targets, not permission to guess
Binder codes, open nodes, execute update paths, or mutate the device.

### 已排除：repeating equivalent tests is not a new control surface

The Phase 6VD reconciliation de-duplicates 19 historical route families. It
records no new durable User-0 writer and specifically preserves the distinction
between a child/profile state change, a foreground redirect, a protected setter
rejection, and a formal HOME resolver change. No same-condition component-disable
or preferred-activity replay is justified.

### 因風險拒絕測試

Recovery/update-binary partition writes, unknown private Binder transactions,
driver/ioctl operations, root/exploit payloads, Fire Launcher mutation, and any
operation requiring a recovery or factory-reset rollback were not performed.

## Highest-value remaining questions

1. Can the residual fosinit rows be closed with exact caller, permission,
   identity and sink joins from preserved artifacts?
2. Can the OTA verifier-to-recovery handoff be proven to require only signed,
   authorized recovery context?
3. Do exact shipped native libraries contain an ordinary-app or system-service
   caller to CMDQ/ION/Amazon-LD with a security-sensitive sink?
4. Is there any exact-build private service whose external handle and caller
   authorization both close to a User-0 package/settings/HOME writer?

Until one of these questions has a complete chain and a safe observation, the
evidence supports protected-control analysis, not a root claim.

## Metrics

- Integrated rows: `86`
- CSV parse warnings: `0`
- Worker families: `5`

## Verdict vocabulary

- **已證實:** exact static edge or saved read-only effect within the cited scope.
- **高可信推論:** bounded interpretation with named missing evidence.
- **待驗證:** a caller, gate, identity, user scope, sink, or runtime effect is incomplete.
- **已排除:** the cited route did not achieve its target under recorded conditions.
- **因風險拒絕測試:** deliberately not executed because rollback/safety was insufficient.
