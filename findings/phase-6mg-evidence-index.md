# Phase 6MG evidence index

| Evidence ID | Source / file | SHA-256 | Observation | Confidence |
|---|---|---|---|---|
| 6MG-SCOPE-001 | `artifacts/phase6mg-oobe-helper-scope-20260810-01/summary.json` | `bfd317b77d46c358bc5d2c5d531f39cdb5f56c0f2ad96fd4fb31d6a509d1fcc9` | Four inputs, 29 signals, zero explicit user-scope signals; no ADB or device mutation. | **Confirmed** |
| 6MG-SETTINGS-001 | `SettingsDBUtils.java:51-64`; source hash in `input-hashes.tsv` | `6ceb23853939c6905bf2de12a6969e7568a3bf2119588a6c1d4347f4ba089b31` | Secure/global writes use `ContentResolver` and key/value; no `put*ForUser` in the reviewed helper. | **Confirmed** |
| 6MG-PACKAGE-001 | `PackageHelper.java:11-22`; source hash in `input-hashes.tsv` | `900f2dd69d349b3b4718b7f988b7d5bd153af2e2cb3c1586600e5b048e760ad8` | Component state values are enable `1` / disable `2`, flags `1`; no explicit user ID. | **Confirmed** |
| 6MG-OOBE-001 | `OOBEActivationHelper.java:29-34,53-74` | `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2` | Guarded OOBE setup keys, not a preferred-HOME writer. | **Confirmed** |
| 6MG-OTA-001 | `BootAfterSystemOTAReceiver.java:27-80`; sender at `fosservices/disassembly.log:96107-96126` | `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90`; VDEX `ecbe62...5151c` | Receiver is reached through guarded post-upgrade/OOBE flow; sender uses boot phase 550 and `isUpgrade()`. | **Confirmed** |
| 6MG-SCOPE-002 | `output/call-graphs/phase6mg-oobe-helper-scope.mmd` | `5d5aa50af2fe418434d2ca0117f4da61ec1ba6bc4f4626fa5a311913273203d2` | Graph intentionally leaves exact Context-to-user mapping pending. | **Confirmed** |

No live OOBE or OTA action was performed. The absence of a live event is a
scope limitation, not evidence that the lifecycle branch cannot run.
