# Phase 6TM-A — H2 `BIND_SERVICE` provenance (host-only)

Scope: exact-build host artifacts only. No device, adb, Binder bind/call, service call, package/settings/user mutation, root, or exploit was used.

## Result

The exact-build H2 APK XML-tree positively declares
`com.amazon.alta.h2clientservice.permission.BIND_SERVICE` with raw
`protectionLevel=0x2` (`signature`), and the exported H2 service references that
permission. The service is `singleUser=true` and `directBootAware=true`.

The custom permission holder and custom grant are **UNKNOWN**. The H2 package's
UID 10012, `system-priv-app` placement, package signature digest `e627f73a`, and
granted platform permissions (`CHANGE_COMPONENT_ENABLED_STATE`, `MANAGE_USERS`,
`WRITE_SECURE_SETTINGS`) do not prove ownership or grant of this custom
permission. `privapp_permissions.xml` contains only those platform permissions;
no matching custom entry was found in the bounded privapp/sysconfig XML set.

The recovered static H2 path establishes a signature-gated household/profile
capability reaching `AmazonUserManager.createAdultUser/createChildUser`; it does
not identify an external production caller/client by package and signing
identity. No Fire Launcher/HOME or package-state writer was found in the bounded
H2 path. Therefore classification is `SIGNATURE_GATE_POSITIVE_CUSTOM_HOLDER_UNKNOWN_PRODUCTION_CALLER_UNKNOWN`.

## Evidence ledger

| path / SHA-256 / line | declaration | holder | grant | caller | gate | classification | next safe step |
|---|---|---|---|---|---|---|---|
| `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/017_com.amazon.h2clientservice.xmltree.txt`; `f14670a78cdbddf4c46375d78e1607fe491c33fd4d807de57abfe5e2b5300242`; lines 69–74 | Package `com.amazon.alta.h2clientservice` declares custom `BIND_SERVICE`; raw `0x2`; group ACCOUNTS | UNKNOWN | UNKNOWN | UNKNOWN | Signature declaration POSITIVE | `DECLARATION_CONFIRMED_PROVENANCE_OPEN` | Preserve exact-build owner/request/signing-policy artifacts; no bind/call |
| same XML-tree; lines 102–110 | `H2ClientService` uses custom permission; `exported=true`, `singleUser=true`, `directBootAware=true`; action `IH2ClientService` | UNKNOWN | UNKNOWN | UNKNOWN external caller | Custom signature gate POSITIVE | `EXPORTED_BUT_SIGNATURE_BOUND` | Host-only caller/signature join; no service invocation |
| `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp_permissions.xml`; `643cf114ed7d7b82a642fea650ed7d2f53b5dab2291e4f043c272cbe577df732`; lines 78–84 | H2 privapp block lists only five platform permissions | Not a custom holder record | No custom grant entry | UNKNOWN | Platform `signature|privileged` policy only | `PLATFORM_GRANTS_DO_NOT_PROVE_CUSTOM_GRANT` | Obtain a preserved exact-build custom-permission grant/owner policy source |
| `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp-permissions-platform.xml`; `0b30c1624ffdab6c5454746737a060157276da5d2bd43addc74cd3919ae4aad1`; bounded search no H2/custom hit; `system/etc/sysconfig/framework-sysconfig.xml`; `bd6e7c52f1c036be4a770bd3be06d0c3a237d05f97921f47c2f652de59ca8fc3`; bounded search no hit | No platform-privapp/sysconfig custom `BIND_SERVICE` entry observed | UNKNOWN | UNKNOWN | UNKNOWN | No custom policy evidence | `CUSTOM_HOLDER_GRANT_UNKNOWN` | Preserve additional exact-build permissions/sysconfig XML if available |
| `artifacts/phase6mc-permission-holder-audit-20260810-05/permission-holders.csv`; `1f97fa825f8b7cd86f05653259ecf43359d496d15af4e21e0c53512274ebdb18`; line 8 | Package-state row: H2 path `/system/priv-app/com.amazon.h2clientservice`, UID 10012, three platform grants | H2 is not proven custom holder | Custom grant UNKNOWN; platform grants observed only | UNKNOWN | Platform grant inventory; custom permission absent | `UID_PLATFORM_GRANT_NOT_CUSTOM_PROVENANCE` | Keep custom holder/grant UNKNOWN; do not infer from UID |
| `output/tables/phase6lz-component-state-permissions/component-state-permission-holders.csv`; `8eeb03c1757832d9ea33abe4968724444ce3d0fe2befc4ea296e482b5ac398e1`; line 2 | Package signature inventory records H2 `PackageSignatures... signatures:[e627f73a]` | Signing identity `e627f73a` confirmed for package inventory only | Does not prove custom grant | UNKNOWN | Signature identity is not caller identity | `PACKAGE_SIGNING_IDENTITY_CONFIRMED_CUSTOM_HOLDER_UNKNOWN` | Join against a preserved custom permission owner/grant/signature source |
| `artifacts/phase6mc-caller-provenance-20260810-01/caller-provenance.csv`; `fbb4f21dad1c3948bb3748fe7bcf652b6b136a6fb07e62cb4e7d7e6d51e1b11d`; lines 2–3 | H2 `onBind`/AIDL and add-user path recorded | UNKNOWN | Signature-bound workflow only | External production package/signature UNKNOWN | `BIND_SERVICE` plus workflow checks; Binder UID logging only | `PRODUCTION_CALLER_UNKNOWN_PROFILE_WORKFLOW_STATIC_ONLY` | Host-only inspect preserved upstream client APK/source; no bind/replay |
| `findings/phase-6tj-tl-report.md`; `90e677aa19f058e6e4dd5adacba27448809649bbdb8f947a023e7181dbf302b0`; lines 19–21, 31–33 | Phase 6TJ conclusion: declaration/gate positive; holder/grant/external client unproven | UNKNOWN | UNKNOWN | UNKNOWN | Acceptance rule requires caller→gate→identity/user scope→sink | `UNKNOWN_NOT_NEGATIVE` | Retain bounded UNKNOWN; do not claim low-privilege caller or HOME mutation |

## Static sink/caller boundary

`artifacts/phase6mc-alta-jadx-20260810-01/sources/com/amazon/alta/h2shared/helpers/AndroidUserHelper.java`
(`d13b354533ff60e96f8dcc8e3da3ecfc1b57ea5e7c0a0e4939119b5537487767`, lines
78–81) reaches `createAdultUser/createChildUser`. This is a static internal
profile-lifecycle edge, not proof of an external production caller. The bounded
corpus contains no caller package plus signing-identity join for the H2 bind.
