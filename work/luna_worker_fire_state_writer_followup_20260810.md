# Fire package-state writer provenance follow-up

公開基準：`77c076b76`。範圍限定為 host-only static/data-flow；輸入為 Phase 6AI、6KQ、6S、6EC、6PW、6PX 與 PS7331 VDEX/smali/resource。未執行 adb、package/component mutation、Binder replay、root/exploit 或 reboot。

## 結論

去重後，能直接寫 Fire Launcher/Tahoe/Launcher3 package/component state 的 Fire-specific writer 只有 KFT child/profile writer：它接受 `UserInfo.id`，啟用 Tahoe launcher component，並對同一 child user 停用 Fire Launcher 與 Launcher3。它不是 User 0 restoration writer，也沒有證據可由 shell 取得 tx3 或繞過 PMS protected gate。

PMS Amazon protected gate 的 static chain 是：system/privileged app、deny-list membership、caller UID 2000 條件經 `VendorProtectedPackagesCallback` fan-in 後，在 enabled-state mutation persistence 前拒絕。Phase 6PX 已補上 resource direct evidence：PS7331 `fireos-res.apk` 的 `raw/package_manager_deny_list` JSON 明列 `com.amazon.firelauncher`，並由 `Resources.getSystem().openRawResource(0x7e05000a)`（resource ID `0x7e05000a`）讀入。這證實 resource seed membership；不等於已讀出 `/data/system/PackageManagerDenyList` 的 live persisted set。

DPM/Profile Owner、Backup preferred restore、公共 HOME setter 都能在受信任條件下寫 preferred state，但現有結果沒有形成 Fire User-0 disable 或可靠的 HOME replacement。OOBE/OTA 能寫 OOBE component/setup state，是 protected system lifecycle，沒有普通 caller 路徑。Arcus 是 deny-list replacement writer，不是 HOME writer。Play/PackageInstaller metadata/APK 只找到 generic package/component writers，無 bounded Fire literal、preferred-HOME writer 或 bypass。

## Writer-to-scope matrix

完整去重矩陣在 [CSV](./luna_worker_fire_state_writer_followup_20260810.csv)。欄位依要求為 `writer, source/method, target package/component, user scope, caller gate, identity handling, sink, existing runtime result, status, next safe step`。

| writer family | 可寫 scope | Fire/Tahoe target | HOME sink | 判定 |
|---|---|---|---|---|
| KFT tx3 / child lifecycle | supplied child/profile `UserInfo.id` | Tahoe enable；Fire、Launcher3 disable | 否；child state only | static writer，shell boundary |
| PMS protected callback | requested user gate | Fire/Tahoe membership-dependent | 否 | pre-write rejection gate |
| Arcus seed/refresh | device-protected deny-list consumed by PMS | resource seed includes Fire；refresh payload unknown | 否 | package protection only |
| DPM / Profile Owner | managed owner user | no Fire-specific input found | persistent preferred possible | trusted owner-gated |
| Backup restore | trusted backup `userId` | serialized preferred data | preferred record possible | trusted system lifecycle |
| OOBE/OTA | framework receiver context | OOBE Home only | transient OOBE resolver candidate | protected lifecycle |
| Play/PackageInstaller metadata | internally derived package/user | no bounded Fire literal | no | generic writers only |
| MigrationService | broadcast running-user propagation | Fire notification target | no | non-writer |

## Phase 6PX resource seed direct evidence

- `artifacts/phase6ap/denylist-resource-closure-20260805-01/res/raw/package_manager_deny_list.json`：host extracted JSON directly contains `com.amazon.firelauncher`，SHA-256 `16086ecbfce20a0c0b37535e25d690635d398b30d582fa6d231736dc9bdf710`。
- `artifacts/phase6ap/denylist-resource-closure-20260805-01/resource-table-targets.json`：`0x7e05000a` maps to `amazon.fireos:raw/package_manager_deny_list`，SHA-256 `ee0aa73a5dfcb11893145fa5a3ac4a263bcd94a815954ed240dcc3aaf9ec896d`。
- PS7331 VDEX/smali `DenyListArcusHelper.processJSON()` reads that raw resource and key `packages_deny_list`; `extractListFromResorces()` only seeds when `DenyListKeyPackages` is absent, then commits the set to device-protected `PackageManagerDenyList`.
- Live persisted contents were intentionally not read. The saved metadata (`system:system`, mode `0660`) and prior protected-package rejection are runtime corroboration, not direct persisted membership proof.

## Runtime and security interpretation

Existing runtime results are read-only or previously preserved evidence: User 0 currently resolves `com.amazon.firelauncher/.Launcher` at priority 50; shell attempts to disable protected Fire/Tahoe targets were rejected before state change; Amazon private service lookup was denied before Binder dispatch; KFT induced-delta stopped before lifecycle execution. No row supports a claim that a static writer is an exploitable vulnerability.

The safe continuation is host-side provenance work or passive observation of a naturally occurring trusted lifecycle (for example, official OTA or child lifecycle), with no replay, mutation, provisioning, property change, or service guessing.

## Evidence basis

- `findings/phase-6ai-denylist-flow-closure.md` and `output/tables/phase6ai-denylist-flow.csv`
- `findings/phase-6kq-kft-tahoe-component-protection-boundary.md` and `output/tables/phase6kq-kft-component-protection.csv`
- `findings/phase-6ec-kft-tx3-reachability-boundary.md` and `output/tables/phase6ec-kft-tx3-reachability.csv`
- `findings/phase-6s-ipc-focus-review.md`
- `findings/phase-6pw-broad-privilege-followup.md`
- `findings/phase-6px-provenance-closure.md`, `findings/phase-6px-evidence-index.md`, and `output/tables/phase6px-provenance-closure.csv`
- `findings/phase-6iz-ps7331-vdex-writer-inventory-closure.md`
- `findings/phase-6kr-pms-writer-baseline.md`, `phase-6hu-user0-residual-writers-closure.md`, `phase-6mb-vending-permission-and-state-writer-audit.md`

