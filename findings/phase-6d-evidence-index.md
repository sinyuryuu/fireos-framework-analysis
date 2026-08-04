# Phase 6D Evidence Index

| Evidence ID | Source / file | SHA-256 or identity | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| P6D-CFG-001 | `artifacts/phase6d/phase6d-init-cfg-20260804-03/callsite-markers.csv` | artifact manifest | `w5=1` rootable candidate、`w5=0` standard candidate，兩者呼叫 `0x41be00`；`0x41be48` 有 `tbnz`。 | rootable/standard instruction-level split exists。 | Confirmed |
| P6D-CFG-002 | `artifacts/phase6d/phase6d-init-cfg-20260804-03/cfg-edges.csv` | `38b720e9b65b4623c73a15953eefb15dc59d2e4a6c26c6ceaa8ca4e594e18616` | `B41bdf4` 到 `0x41c30c` 與 `0x41be4c` 的 branch/fallthrough edges。 | pure strings-only residue 不足以解釋現象。 | Strong evidence |
| P6D-BIN-001 | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init` | `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd` | PS7331 `/init` binary used for host-only disassembly。 | provenance input is fixed。 | Confirmed |
| P6D-AOSP-001 | `artifacts/phase6d/phase6d-init-pipeline-diff-20260804-01/pipeline.json` | `init/selinux.cpp` SHA `b2bb7d74d8cb8863d04b2172eedc22d0074129cab16c3335285fc9c2f9e69fa1` | r1/r61 contain standard SELinux loader anchors；GPL package lacks init source。 | AOSP anchor available; Amazon source diff unavailable。 | Confirmed |
| P6D-DEV-001 | `adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-20260804-03/metadata.txt` | `5c0a43485151e59c258d7f8efed54bba141a6219088033419c84d94b78b67b1e` | `device_mutation=false`, `policy_selected=false`, `boot_property_changed=false`, `fastboot_invoked=false`。 | snapshot was non-mutating; it does not prove active policy variant。 | Confirmed |
| P6D-DEV-002 | `adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-20260804-03/selinux_mode.stdout.txt` and `getprop.stdout.txt` | see directory manifest | stock state is enforcing/retail locked according to preserved properties and mode output。 | userspace shell did not establish a writable policy selector。 | Strong evidence |
| P6D-S1-001 | `artifacts/phase6d/phase6d-policy-scenarios-20260804-01/policy-scenarios.csv` | `6b6116fcd088e6befbb0977534dc5fb60d3ad46160f95507ab764147c562d7f6` | no source-level link from writable `persist.*`/`/data` state to rootable branch。 | S1 remains unproven. | Hypothesis |
| P6D-S3-001 | `artifacts/phase6c/phase6c-init-policy-loader-audit-20260804-02/policy-loader-audit.json` | `37d77ceed1004aa76e38004fd365c286eade2abca112c89e0e5f7898e51e5235` | AVB/crypto/eFuse markers are present; guard relation is not recovered。 | S3 remains unproven. | Hypothesis |
| P6H-PM-001 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96950-97049` | source artifact hash in local manifest | `ControlProtectedPackagesCallback` reads `PackageManagerDenyList`/`DenyListKeyPackages` and checks system app plus UID 2000。 | vendor protected-package policy is a real static control surface。 | Confirmed |
| P6H-HOME-001 | `decompiled/baksmali/vdexExtractor/services/disassembly.log:977415`, `988383-988450` | source artifact hash in local manifest | Home key path has `KeyPolicyManager` and `VendorPhoneWindowManagerCallback` boundaries before standard `startActivityAsUser`。 | callback can influence/consume Home, but Fire selection is not proven。 | Strong evidence |
| P6H-RESOLVE-001 | `decompiled/baksmali/vdexExtractor/services/disassembly.log:951258-951310`, `959804+` | source artifact hash in local manifest | resolver queries candidates, chooses best activity, and checks persistent before ordinary preferred records。 | standard resolver remains visible in selected path。 | Strong evidence |
| P6I-OTA-001 | `artifacts/phase6i/phase6i-ota-postinstall-20260804-01/summary.json` | OTA SHA `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | 27 members, update-binary/updater-script, system/vendor/boot-chain targets。 | package is a full update transaction, not a reversible userspace switch。 | Confirmed |
| P6I-OTA-002 | `artifacts/phase6i/phase6i-ota-postinstall-20260804-01/result.md` | see artifact manifest | updater was not executed; malformed package, symlink and partition tests were rejected。 | no dynamic OTA exploitability claim is made。 | Confirmed |

## Evidence boundary

No evidence in this index proves that a retail device loads `rootable_*` policy,
that a writable userspace flag selects it, or that a root payload can be run.
