# Component/package-state mutation authorization provenance

Date: 2026-08-10. Scope: host-only static review of the saved corpus. No ADB,
Binder, service, ioctl, root, OTA, flashing, grant/revoke, or state mutation was
performed by this work.

## Bottom line

The corpus proves that `android.permission.CHANGE_COMPONENT_ENABLED_STATE` is
declared by the `android` package with `prot=signature|privileged`, and that the
saved PackageManager state records it as granted to `com.android.vending`
(UID 10180) and a set of system/priv-app packages. It does **not** prove that
the Play Store has a usable route to a protected package/component, nor that it
can write HOME/preferred state. The ordinary installed-package route remains
**UNKNOWN as a generic capability question**, and **not proven for Fire
Launcher/HOME**.

The strongest negative conclusion is narrower: no ordinary installed package
has a proven corpus-backed route from its own caller identity to a successful
PackageManager mutator for a protected Fire Launcher target. A permission
holder row is not caller provenance, and a static setter call is not runtime
reachability.

## Evidence and provenance chain

### Permission declaration and protection level — Confirmed

The preserved package dump defines the permission as:

* `artifacts/phase6j/phase6j-ota-controller-holders-20260805-01/dumpsys_package_all.stdout.txt:10107-10111`:
  `sourcePackage=android`, `uid=1000`, `prot=signature|privileged`.
* Source SHA-256: `6f2754f4e9655567524de00c5b044326cbd992d6a9022b87397369fb5b905909`.

The same protection level is independently visible in the decoded framework
manifest at
`artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/041_framework-res.xmltree.txt:2199-2200`
(source SHA-256 `7b6d377dd8676066ae93651b69dda06f59122cb886d4c2ca1483b3264a4b801d`).
The declaration establishes a protected permission requirement; it does not
identify a caller or establish a protected-package exception.

### Holder, requested/granted state, signing and placement — Confirmed

The saved holder census records 11 package blocks with this granted permission
(the parser intentionally stops before `Shared users`; see
`findings/phase-6lz-component-state-permission-audit.md:25-31`). The relevant
Play Store block says:

* `.../dumpsys_package_all.stdout.txt:21397-21411`: package
  `com.android.vending`, UID 10180, code/resource path `/data/app/...`, flags
  without `SYSTEM`, and private flags without `PRIVILEGED`.
* `.../dumpsys_package_all.stdout.txt:21424-21427`: installer is itself and
  signing digest is `e3ca78d8`; permissions are fixed.
* `.../dumpsys_package_all.stdout.txt:21452-21464`: install-permission state
  includes `INSTALL_PACKAGES` and `CHANGE_COMPONENT_ENABLED_STATE` with
  `granted=true`.
* Source SHA-256 is the dump hash above.

This distinguishes a recorded grant from a manifest declaration and from
privileged placement. The dump does not reveal the grant event, grant actor,
historical package state, or whether the grant is accepted for every PMS sink.

For comparison, the reproducible holder table records system/privileged
placement for Amazon holders and data-app placement for Vending:
`output/tables/phase6lz-component-state-permissions/component-state-permission-holders.csv:2-12`
(the table is generated from the dump; the input hash is recorded in
`findings/phase-6lz-component-state-permission-audit.md:10-16`).

### Privapp provenance for Vending — Not found; grant source UNKNOWN

The extracted permission configuration contains no
`<privapp-permissions package="com.android.vending">` block. Exact relevant
scope:

* `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp_permissions.xml:1-...`, SHA-256
  `643cf114ed7d7b82a642fea650ed7d2f53b5dab2291e4f043c272cbe577df732`.
* `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp-permissions-platform.xml:1-...`, SHA-256
  `0b30c1624ffdab6c5454746737a060157276da5d2bd43addc74cd3919ae4aad1`.
* The positive control for other packages is visible at
  `privapp_permissions.xml:78-84` (`com.amazon.alta.h2clientservice`) and
  `privapp-permissions-platform.xml:88-104`
  (`com.android.managedprovisioning`).

This is version-scoped negative evidence, not proof that no install-time or
persisted grant source exists. Therefore Vending's grant provenance is
**UNKNOWN**.

### Actual Vending caller and downstream sink — Generic writer only; route UNKNOWN

The Vending static audit found generic calls, including:

* `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/defpackage/uls.java:339-365`
  (SHA-256 `f2222f618f0fece363bdb6b4ded0646b1103a149fb041251536aa1e631b6b6c7`)
  and `artifacts/phase6mb-vending-jadx-20260810-01/base/sources/com/google/android/finsky/verifier/impl/enforcement/UninstallTask.java:216-238`
  (SHA-256 `438e9ae9ef9626a4efe0d4dba0d840f4431367fda5095d3a572897f07201f332`),
  summarized at `artifacts/phase6mb-vending-static-20260810-01/static-search-summary.md:17-25`
  (SHA-256 `4354ef160b28c4ee6aa3d27e0b2da59d2e00cc0543067dfe217ad699db08ffe9`):
  setter targets are internally supplied/generic; no Fire literal, preferred
  activity writer, `startHomeActivity`, or HOME selection writer was found in
  the bounded generated source scan.
* The specific decompiled writer evidence is cited by
  `findings/phase-6mb-vending-permission-and-state-writer-audit.md:71-95`
  (`uls.java:339-365`, `UninstallTask.java:216-238`, and listed generic
  restore/component writers). These establish candidate downstream calls to
  package/component mutators, not their external caller authorization.

The static scan covered 52,327 generated Java files and JADX exited 3 after
partial output; native/resources/failed regions remain **UNKNOWN**. Thus the
corpus supports “generic package/component setter callsites exist,” but not
“Vending can mutate a chosen protected target.”

### PMS authorization and protected-package sink — Confirmed boundary

The standard sink is `IPackageManager` transaction 90 to
`PackageManagerService.setComponentEnabledSetting()`:

* `findings/phase-6ci-tahoe-user0-component-gate.md:70-83` (SHA-256
  `4d6d857f4f714726441aed73ba124ea958800a95e2d682a3281b7e83d3d12d26`) identifies the
  delegation, `Binder.getCallingUid()`, the
  `CHANGE_COMPONENT_ENABLED_STATE` check for non-system callers, cross-user
  enforcement, and the system-package component gate.
* The same finding's flow at `:99-109` ends in `SecurityException` before state
  persistence for the tested shell path.
* The current static caller inventory explicitly labels each row
  `static_invoke_site_only` and says it does not infer caller UID, Binder
  reachability, user scope, or runtime execution:
  `findings/phase-6kv-pms-home-caller-closure.md:76-78` (SHA-256
  `a3c3d90315895c8295c8cee73f889f020b96f31cded80fa9e1672dc9ae598ef1`).
  Its source hashes are `fosservices` `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
  and `services` `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`.

Accordingly, permission possession can satisfy one authorization check while
still failing the downstream protected-package gate. The actual caller,
identity clearing, explicit user, target package, and successful sink result
are separate fields and are not established for Vending.

## Other holders and writers

The saved table records system/privileged holders such as
`com.amazon.alta.h2clientservice`, `com.amazon.tahoe`,
`com.amazon.alexa.multimodal.gemini`, `com.android.musicfx`, and
`com.android.managedprovisioning`; see
`output/tables/phase6lz-component-state-permissions/component-state-permission-holders.csv:2-12`.
Their package placement/signing metadata is holder evidence only. The
package-state writer inventory found 21 setter references, but classifies them
as lifecycle, child-user, policy, boot-receiver, shell, or framework-internal
paths; `findings/phase-6mh-package-state-writer-closure.md:7-20,31-47`.
The KFT row has Fire/Tahoe/Launcher3 literals but uses `UserInfo.id` and is a
child/profile lifecycle path, not proven User-0 ordinary-app reachability
(`findings/phase-6kv-pms-home-caller-closure.md:95-105`).

HOME/preferred writers do exist inside trusted framework paths, including
`PackageManagerService.setHomeActivity()` → `replacePreferredActivity()` and
Device Policy owner paths, but the inventory explicitly classifies them as
system/owner paths rather than ordinary-shell evidence
(`findings/phase-6kv-pms-home-caller-closure.md:107-129`). No Vending HOME or
preferred writer was proven.

## Final authorization matrix

| Question | Result | Why |
|---|---|---|
| Permission declared? | Confirmed | Android package definition at dump `:10107-10111`. |
| Protection level? | Confirmed | `signature|privileged`; framework XML corroborates. |
| Vending holder recorded? | Confirmed | Granted state at dump `:21452-21464`. |
| Vending requested vs granted? | Granted in saved install state; manifest/request provenance separately UNKNOWN | Dump shows install grant; bounded manifest evidence is not the grant event. |
| Vending system/privileged? | Data-app; no captured `PRIVILEGED` flag | Dump `:21400-21411`. |
| Vending signing identity? | Digest `e3ca78d8` recorded; trust equivalence to platform not established | Dump `:21424-21425`; framework digest differs per Phase 6MB. |
| Vending actual caller? | UNKNOWN | Static writers do not prove invoking component/UID/Binder path. |
| Vending downstream mutator sink? | Generic setter candidates only; exact target/success UNKNOWN | Phase 6MB bounded scan and decompiled writer citations above. |
| Vending HOME/preferred writer? | Not found in bounded scan; hidden/native/resource path UNKNOWN | Static-search summary `:17-25`. |
| Any ordinary installed package with proven protected mutator route? | No | Corpus has capability/holder rows and static callsites, but no proven ordinary caller→accepted protected sink chain. |

This conclusion closes the provenance question without converting a capability
into an assumed route.
