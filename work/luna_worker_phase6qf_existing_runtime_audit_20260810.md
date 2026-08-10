# Phase 6QF Worker C：既有實機 runtime evidence audit

日期：2026-08-10  
基準：`aca16f12daa7807e435fcbc259e5af067cab6b12`（Phase 6QE broad privilege surface verification）、Phase 6QE existing-tests/evidence index。  
範圍：只讀整理既有 `adb/`、`artifacts/`、`findings/`、`tools/scripts/`；本次未接觸裝置、未重跑測試、未修改任何裝置狀態。

## 結論

七個指定面向都有既有路徑可核對，但尚未閉合的 runtime edge 不是同一類問題：

- **已有直接 runtime evidence**：Fire package/component gate、KFT child/profile 的既有結果、Accessibility bind/foreground fallback 邊界、service visibility，以及 QE exact-device driver metadata。
- **仍是 runtime unknown**：User-0 Fire restoration caller、合法 DPM/Profile relay、官方 OTA 後 native updater/fosinit handoff、private service method behavior、未開啟 driver node 的行為。
- **可無 mutation 最小重現**：只限讀取既有 HOME/package/user/DPM/service/metadata；不能用只讀命令重現一個本身需要 writer、profile lifecycle、Accessibility 設定、OTA 或 node open 的行為。

完整欄位（raw evidence/hash、前提、最小重現與停止條件）見 [CSV](./luna_worker_phase6qf_existing_runtime_audit_20260810.csv)。

## 逐項判定

| ID | 面向 | 既有 evidence 判定 | 尚未核對的 runtime edge | 無 mutation 最小重現 |
|---|---|---|---|---|
| QF-C-01 | Fire package/component gate | 已確認拒絕發生在 state change 前；User-0 Fire 仍為 HOME winner。 | User-0 restoration writer 的 production caller provenance。 | 可讀取既有 dumps/resolve/activity；不可重送 writer。 |
| QF-C-02 | KFT child/profile | 已有 child/profile Tahoe HOME、Fire per-user state、switch-back User-0 Fire。 | tx3 合法 caller 與 User-0 restoration side effect。 | 可做 `pm list users`、`dumpsys user/package`、每 user HOME resolve；不能重跑 lifecycle。 |
| QF-C-03 | DPM/Profile | owner/admin/UID gate 與 passive backup evidence 已保存。 | 合法 Profile Owner relay、active backup/native callback。 | 可讀 `dumpsys device_policy` 與既有 logs；不能 provision 或送 transaction。 |
| QF-C-04 | Accessibility fallback | 6DE bind-but-empty；6IQ/6CX 為有限 foreground fallback，不是 HOME。 | 其他 GUI/persistence 狀態；6PD PendingIntent 變體 runtime 未測。 | 只核對既有輸出；不重新 enable、改 secure setting 或安裝 APK。 |
| QF-C-05 | Service visibility | `service list` 可見不等於 shell 可取得 handle；private service check/find 已有 denial。 | private service method-level behavior、完整 registration map。 | 可 read-only list/check/dumpsys/logcat；不呼叫未知 Binder。 |
| QF-C-06 | OOBE/OTA | OOBE/receiver gate 與 fixed block-image updater static boundary 已有 evidence。 | 官方 OTA 後 native/fosinit/post-install runtime。 | 可核對 baseline/static capture；只能等待自然官方 OTA evidence。 |
| QF-C-07 | Driver metadata | node metadata/labels/SELinux metadata 已直接保存；未開 node。 | 未開 node 的 driver/ioctl/native client 行為及 handoff。 | 可讀 stat/label/property；不開 node、不 ioctl。 |

## Evidence 與停止規則

`adb/phase6qe/PHASE6QE-DEVICE-READONLY-20260810-02/metadata.json` 的 hash 為 `5afaf05e9d2bec715d9142250f053441b31383ffe9624cb3d80f03cff6e16a0d`；其 metadata 明確記錄 12 個命令、未開 device node、未讀 driver data、未呼叫 Binder transaction、未做 settings/package mutation、未 reboot、未 OTA/recovery、未 root/exploit。代表 QE 的 exact-device snapshot 可作為本 audit 的只讀 runtime anchor。

重要 raw hashes：

- QE `node_metadata.stdout.txt`: `fd8a1b871b5e65e948b44a9d121a0e4368e0c702c07accc756c6bbff9eb28e82`。
- QE `home_resolve.stdout.txt`: `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`。
- QE `selinux.stdout.txt`: `4fefafd0dcddf54b31a0fef448083e7b77576d86a9ec97c14bfd92479c404290`。
- Q `service_list.stdout.txt`: `1bed100e5cb128fed02bd197964792a6ecc1ea461818772747d1d543f334e6ba`。
- 6FA protected force-stop `command-output.txt`: `06ba554adbc33bed568224f73b2c311dce63df2af5893946cf464849392cc9b9`。

所有停止條件都以「不改狀態」為硬邊界：遇到 package/component writer、force-stop、user lifecycle、DPM owner、secure setting、APK install/update、未知 Binder、OTA/recovery/partition、driver open/ioctl、root/remount 或為測試而 reboot，立即停止。Phase 6QF 不把 mutation capture 的存在誤標為可重現授權。

## 未新增測試

未執行 `tools/scripts/` 中任何 probe/capture/run script；其中腳本只作路徑索引與既有 provenance 參照。未重跑 Phase 6QE 已排除的 priority APK、set-home、preferred/force-stop、KFT tx3、DPM/Backup raw transaction、Accessibility package update、OOBE/OTA replay、driver ioctl 或 root 類測試。

## 交付

- 本報告：`work/luna_worker_phase6qf_existing_runtime_audit_20260810.md`
- 矩陣：`work/luna_worker_phase6qf_existing_runtime_audit_20260810.csv`
