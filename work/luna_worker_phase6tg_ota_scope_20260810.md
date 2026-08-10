# Phase 6TG — Fire OS 7.3.3.1 source / OTA / post-install host-only audit

日期：2026-08-10。範圍：PS7331 / trona，僅本機既有 extraction、boot/OTA artifacts、
`update-binary` / OOBE / `otadexopt` findings 與 hash manifests。未下載工具、未構造
或修改 OTA、未執行 update/recovery/sideload/flash/reboot，未接觸設備。本報告把
「高權限 capability」與「實際 caller / 低權限可達性」分開。

## 結論

官方 OTA provenance 與內容是 **Confirmed**：本機包為 PS7331 Fire OS 7.3.3.1，
傳統 signed Edify/block-image 形態；已知 member set 有 `update-binary`、
`updater-script`、system/vendor `.new.dat.br`、transfer lists、`boot.img` 與多個
boot-chain image，沒有 `payload.bin` 或 A/B post-install executable。Script 明確
列出 system/vendor/boot/firmware partitions 與 `/cache/recovery/last_blocklist`。

`update-binary` 的 registry、`PackageExtractFileFn`、`block_image_update`、
`PerformBlockImageUpdate`、`CacheSizeCheck`、`WriteToPartition` 形成 **Strong
evidence / Confirmed capability** 的 recovery-context writer chain；這不是普通
shell 或 APK caller 證據。Java verifier/staging → `UpdateSystem.install` 是正常
privileged handoff，但 recovery/native caller 的完整端到端 provenance 仍是
**Unknown**。沒有證據建立 shell/普通 app → partition writer、OOBE writer 或 root
transition 的完整鏈，故不作 exploit 結論。

`otadexopt` 有 shell-visible service 與 `OtaDexoptShellCommand`，但保存的唯讀
`done/progress` 觀察只證明 service/precondition path；`prepare/next/cleanup` 的
dexopt/OAT mutation 未呼叫，且未見 partition/HOME/root sink。這是 capability，
不是 shell-to-partition reachability。

## Evidence matrix

| ID | scope / source | method and path | observed boundary | status |
|---|---|---|---|---|
| TG-01 | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`; SHA-256 `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | saved `members.json` / `ota-findings.csv` member inventory; `firmware/extracted/PS7331/` | Official package provenance; 27 known members including metadata, cert, updater, payloads, images | Confirmed |
| TG-02 | `artifacts/phase6i/.../members.json`; SHA-256 `73647770903168819a92b5861bb57416226abd4bfc29f2d135f76a2f3e5f48d4` | host-side ZIP/member listing; no execution | `update-binary`, `updater-script`, `system/vendor.new.dat.br`, transfer lists, `boot.img`, `images/*.img`; no `payload.bin` in known members | Confirmed |
| TG-03 | `firmware/extracted/PS7331/META-INF/com/google/android/updater-script`; package hash `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | script text audit, lines 1–24 | build/device gates; `block_image_update` system/vendor; `package_extract_file` boot-chain; blocklist → `/cache/recovery/last_blocklist` | Confirmed |
| TG-04 | `META-INF/com/google/android/update-binary`; SHA-256 `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` | saved CFG/disassembly and registration table | `main` registers install/block-image functions; extraction/open/fsync/close and block-image handlers are present | Strong evidence |
| TG-05 | `artifacts/phase6mk-updater-dispatch-20260810-01/registration-dispatch.csv`; report SHA-256 `443c69127293d18903d469f7a670a4b58b208cdbf6402c240ecaeec6e307ecb3` | static callback registry / direct-edge review | 24/24 saved install callback registrations; registry is not a shell API | Confirmed |
| TG-06 | `artifacts/phase6ne-updater-cache-flow-20260810-03/{selected-functions.csv,direct-call-edges.csv}`; summary SHA-256 `1cb21f3de9403c54e080c27f2d285d8e76a0e3a970063a250cdcc3c222a98b60` | bounded disassembly call-edge review | `PerformBlockImageUpdate → CacheSizeCheck`; `mkdir/stat/chown` and readlink-family markers exist in selected flow; full canonicalization/dataflow not closed | Unknown |
| TG-07 | `findings/phase-6kt-recovery-verifier-provenance.md`; report SHA-256 `484273958f44898c6b94a208da4e144936df09a191e03efe6316c18d167fe732` | Java source/decompiled path audit | metadata/hash/signature/PVT validation → `RecoverySystem.verifyPackage` → `UpdateSystem.install`; final native recovery caller not fully recovered | Strong evidence |
| TG-08 | `output/tables/phase6kt-recovery-gates.csv` | saved evidence-table review | fixed named targets and privileged handoff; no shell/ordinary-app updater caller established | Strong evidence |
| TG-09 | `output/tables/phase6ae-otadexopt-methods.csv`; `findings/phase-6ae-shell-visible-otadexopt.md` | saved VDEX/disassembly plus prior read-only capture | `otadexopt` service and shell command; `done/progress` reached precondition/read path; mutating verbs not invoked | Confirmed |
| TG-10 | `artifacts/phase6u/bootafter-ota-scope-20260805-01/bootafter-ota-scope.csv`; summary/input hashes in artifact | source/dataflow and saved state review | system-server boot phase 550 + `PackageManagerService.isUpgrade()` sends protected-permission action; receiver can enable OOBE and mutate setup state | Confirmed |
| TG-11 | `artifacts/phase6r/ota-oobe-authorization-20260805-05/oobe-authorization-matrix.csv` | manifest + sender/receiver permission comparison | receiver declaration lacks observed `android:permission`; sender uses permission argument; action name alone is not caller authentication | Strong evidence; authorization completeness Unknown |
| TG-12 | `artifacts/phase6i/.../summary.json` | saved audit metadata | `device_contacted=false`, `updater_executed=false`, no malformed/symlink/traversal package | Confirmed negative procedure boundary |
| TG-13 | `artifacts/phase6c5/gpl-source-scope-20260804-01/scope.csv`; source manifest `kernel/source-manifest.json` | archive scope/hash manifest and path existence review | kernel MT8183 4.4 source present; Android userspace `system/core/init` and SELinux init sources absent from claimed source scope | Confirmed |
| TG-14 | `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-04/phase6nb-amzn-drv-test-source.csv` | source grep/selected-config review | Amazon test driver has proc write callback and owner-write mode in source; selected `trona_defconfig` presence/config and shipped node/SELinux caller are not closed | Strong evidence (capability); Unknown (reachable) |
| TG-15 | requested symlink/temp/permission-transfer tests | safety boundary review | no symlink traversal, malformed OTA, recovery execution, partition write, device test, or permission-transfer experiment performed | Risk-rejected |

## Caller versus capability disposition

* **Partition/boot writer capability:** Confirmed in `update-binary` and script. Caller is
  recovery/update context only in the saved evidence; ordinary shell/APK reachability is
  not established.
* **OOBE/setup writer:** Confirmed for the guarded system-server post-OTA lifecycle.
  The receiver permission metadata and sender argument are separate authorization facts;
  an action string or receiver presence is not ordinary-app caller proof.
* **`otadexopt`:** shell-visible service is confirmed, but its sensitive operations are
  not equivalent to partition/HOME writer capability. Only read/precondition capture is
  in scope; mutation reachability remains Unknown.
* **Kernel/Amazon debug surfaces:** source-visible capability is not proof of a shipped
  node, Unix mode, SELinux allow rule, or ordinary APK path. Keep these as capability-only
  until those independent inputs exist.

## Limitations and non-findings

The source tar summary reports a complete known member inventory for the bounded audit,
but absence from the analyzed corpus is not a universal claim about other releases or
unselected nested inputs. Native indirect dispatch, full `CacheSizeCheck` body and
canonicalization input/output are not fully closed. No status above treats static strings,
proc/ioctl presence, service visibility, or missing `capable()` checks as proof of a
low-privilege exploit path.

詳細逐列 machine-readable matrix：`work/luna_worker_phase6tg_ota_scope_20260810.csv`。
