# Phase6AF — PS7331 OTA verifier gap（host-only）

日期：2026-08-10。本文只新增未閉合、negative 或 provenance evidence；Phase6X2 與既有 OTA worker 已閉合的 package identity、Java hash/metadata/signature gate、registry capability、extraction/writer capability、固定 named targets 與 `MakeFreeSpaceOnCache -> __readlink_chk` callsite 不重複列出。

## Scope / safety

只讀取保存的官方 PS7331 OTA、`META-INF/update-binary`、debugdata、Phase6MK/MD/NE/MM/KT derived tables。未執行 `bin/update-binary`、recovery、sideload、flash、OTA、reboot、Binder、真機或 partition I/O；未製作 malformed/downgrade/symlink/traversal OTA。每筆 evidence 都說明禁止 runtime 的理由。

## New unresolved / negative / provenance evidence

| ID | 新增結論 | host evidence（檔案/offset） | SHA-256 | status | caller / identity gate | why runtime is not allowed |
|---|---|---|---|---|---|---|
| 6AF-OTA-001 | updater-script 的 build-date/product abort 不是 rollback-index proof。 | `firmware/extracted/PS7331/META-INF/com/google/android/updater-script:1-2` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | `UNRESOLVED_DATE_PRODUCT_NOT_ROLLBACK` | recovery/Edify context implied；Java verifier 與 native caller 未連接 | 需要 recovery 評估或 downgrade/rollback package；會跨越高權限更新與 boot-state 邊界。 |
| 6AF-OTA-002 | verifier→AVB/rollback→native exec provenance 未閉合；audit 只保存 updater markers。 | `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:binary_markers.update_binary[0..5]` | `01e29ec3a2649d85d033ce7ce65034631ebb44ef00633e34a95b0eb063f317f9` | `PROVENANCE_GAP_AVB_ROLLBACK` | `RecoverySystemWrapper`/`RecoverySystem` API boundary；native recovery identity 未恢復 | 需要執行 recovery/update-binary 才可能觀察 handoff；明確禁止且可能觸及 partition。 |
| 6AF-OTA-003 | `CacheSizeCheck` 對 `MakeFreeSpaceOnCache` 的 sign-bit failure 做 error normalization：error path 後回傳 `1`，正常路徑回傳 `0`。 | `artifacts/phase6ne-updater-cache-flow-20260810-03/focus-disassembly.txt:0x414720-0x41475c` | `ca482551bea143f0c22ca3599655a6c10bfbb66033c9f99242f72048220797ee` | `NEW_ERROR_BRANCH` | caller edges 在 `PerformBlockImageUpdate:0x409cb4,0x409cdc`；只證明 native updater context | 不能以 live cache/path state 驗證，因會進入 privileged updater。 |
| 6AF-OTA-004 | 兩個 `CacheSizeCheck` caller 只對 `w0==0` 走 continuation；nonzero branch 是否可達 writer 未閉合。 | `artifacts/phase6ne-updater-cache-flow-20260810-03/return-branches.csv:PerformBlockImageUpdate rows; callsites 0x409cb8,0x409ce0` | `95f469e697c636a2f09bcb6d3f27540f9d336a4bf042d2a5b33b37156a28b87b` | `NEW_BOUNDED_NEGATIVE` | `PerformBlockImageUpdate` recovery/updater identity；無 untrusted caller | 追蹤 continuation 需帶入 archive/cache inputs，可能抵達 named-partition writer。 |
| 6AF-OTA-005 | `MakeFreeSpaceOnCache` 內多個 address-only edges 未解析；不能把 readlink/unlink 直接歸因到 extraction 或 writer。 | `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv:0x417858,0x4178b0,0x4178e0,0x417904,0x41792c,0x41793c,0x417a18,0x417a5c,0x417a6c,0x417c54,0x417c84,0x417d0c,0x417d1c,0x417d24,0x417d38,0x417d7c,0x417e60,0x417f74,0x417fb4,0x417fbc` | `d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477` | `UNRESOLVED_INDIRECT_DISPATCH` | entered via `CacheSizeCheck:0x414730`; untrusted caller absent | 執行 binary 或構造 filesystem/symlink state 才能解析語意，均越界。 |
| 6AF-OTA-006 | no-follow/canonicalization 仍是 bounded negative：markers 存在，但 selected graph 無 direct edge；不等於 binary-wide absence。 | `artifacts/phase6mk-updater-dispatch-20260810-04/canonicalization-context.csv:5 rows`; `artifacts/phase6md-native-updater-path-audit-20260810-02/summary.json:18-19` | `44f61840637e65d7a263b4912d340d834aba1b41b7a84dc7d20382e45fd1a726`; `6dec85cee148a60daba1e8c781f30370389c6d95ff787623cb6ac830f058a834` | `BOUNDED_NEGATIVE_NO_DIRECT_EDGE` | registry dispatch indirect；selected native updater context | symlink/traversal/no-follow 只能用不安全 path input 做 runtime test，明確禁止。 |
| 6AF-OTA-007 | extraction/open 與 writer/open/write direct edges 已存在，但每次 invocation 的 archive argument→named target provenance 未閉合。 | `artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv:PackageExtractFileFn 0x4021b4/0x4022cc/0x40238c; WriteToPartition 0x413dcc-0x413f08` | `7dc9e3ef02a86d978d5973640bad0273288d83c71b8e7117eefb96c7bfffdbb` | `UNRESOLVED_ARGUMENT_PROVENANCE` | registered Edify handlers；recovery updater identity；ordinary app/shell caller 未建立 | handler execution 會開啟/寫入 protected file or partition，禁止 runtime。 |
| 6AF-OTA-008 | Java verifier、`UpdateSystem.install`、recovery exec、native registry 是分離 provenance domains；final native caller/SELinux identity 未閉合。 | `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json:inputs.recovery_wrapper; inputs.update_system_wrapper; execution_policy` | `01e29ec3a2649d85d033ce7ce65034631ebb44ef00633e34a95b0eb063f317f9` | `UNRESOLVED_NATIVE_CALLER_IDENTITY` | Java privileged OTA path 有 API boundary；native recovery caller、execution flags/domain 未恢復 | 需要 recovery/OTA 或 device inspection 才能補足，均不在本 host-only delegation。 |

## Interpretation boundary

這些 evidence 只支持：`CacheSizeCheck` 的 error/continuation semantics 已比既有 inventory 更細；其間接 callees、argument provenance、verifier→AVB/rollback→recovery identity 仍未閉合。它們不支持 symlink bypass、no-follow vulnerability、signature bypass、rollback bypass、root、shell reachability 或 named-partition 實際寫入。

## Host-only disposition

所有下一步若要補足上述 gap，仍只能做保存 binary/debugdata 的靜態 CFG、pointer-table、argument/return tracing。不得以 `update-binary`、recovery、malformed/symlink OTA、sideload、flash、reboot、partition write 或真機觀察取代缺失證據。
