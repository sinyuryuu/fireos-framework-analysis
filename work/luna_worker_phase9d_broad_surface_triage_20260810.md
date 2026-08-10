# Phase 9D broad privilege-surface triage

日期：2026-08-10（Asia/Taipei）。本輪只做 host-only、唯讀 broad triage；未執行 adb、Binder transaction、driver open/ioctl、OTA/recovery、root/exploit 或 mutation，且未改寫既有檔案。

## 結論

從公開 Phase 7/8 control-surface ledgers、Phase 7B residual inventory、PS7331 fosservices/boot-fosframework disassembly、OTA controller/recovery artifacts 與保存的 system APK/JAR audit 中去重，保留 10 條非 Launcher 專屬且仍有 caller/gate/identity/scope/downstream 缺口的候選。候選涵蓋 package/component metadata、user/profile/DPM、settings-adjacent/system relay、OOBE/OTA lifecycle 與 native-adjacent privileged surface。

每條都按 `caller → gate → Binder identity → user scope → sink → effect` 記錄於 [CSV](./luna_worker_phase9d_broad_surface_triage_20260810.csv)。`UNKNOWN` 表示證據缺口；exported、permission string、holder、service publication、generic writer 或 static capability 本身不被宣稱為漏洞。

## 候選摘要

| ID | surface | sink/effect | status | missing edge |
|---|---|---|---|---|
| P9D-001 | Amazon PM flags/metadata | `AmazonApplicationFlags` persistence；first PM/HOME consumer unknown | caller unknown | production caller、grant、consumer |
| P9D-002 | Amazon DPM restriction | `UserManager` restriction state | policy caller unknown | permission branches、owner/caller、target user |
| P9D-003 | Amazon Profile initiateLauncher | internal profile flow | reachability unknown | caller registration、component/user args |
| P9D-004 | Amazon Profile startProfilePicker | `startActivityAsUser` picker relay | caller/gate unknown | service binding、permission、user provenance |
| P9D-005 | AMS activity observer | `ComponentName` callback | callback-to-sink unknown | observer registration/consumers |
| P9D-006 | Amazon WMS overscan/PIP | display/window/PIP state | caller/gate unknown | method gates、SELinux/caller/display scope |
| P9D-007 | H2 exported service | adult/child user/profile creation | low-privilege caller unknown | declaration、signature grant、user flow |
| P9D-008 | BOOT_AFTER_SYSTEM_OTA/OOBE | OOBE component + settings flags | ordinary relay unknown | sender, protected membership, Context user |
| P9D-009 | Vending generic writers | package/component enabled-state writers | holder-only | exact caller/input/target |
| P9D-010 | OTA controller/recovery | partition/block-image/post-install capability | privileged capability only | registration/caller/framework relay |

## De-duplication and safety boundary

已排除 Phase 7/8 已閉合或 bounded-negative 的 Fire HOME/preferred setter、KFT tx3 user-scope boundary、prewarm process-only sink、SettingsProvider standard write gate、keyguard duplicates，以及已完成的 driver closure rows。P9D-010 僅保留 OTA/update-state capability 作未閉合 broad surface，不執行 updater/recovery；本表沒有把 native driver capability 或 OTA write capability 推成低權限 caller 可達。

Evidence 主要來自既有 `output/tables/phase6qd-privilege-surface.csv`、`work/luna_worker_ipc_unclosed_sink_inventory_20260810.md` 與其中指向的 PS7331 disassembly/OTA artifacts；各列的既有 evidence SHA-256 直接保留在 CSV。

CSV output SHA-256（固定內容）：`d6ca78f86ad17794e21b51540e6bcaf619f0f4c0bebda725614f8b42efd8901b`

MD output SHA-256 於交付時以檔案完成內容計算並回報；不嵌入自身雜湊，避免自我引用。
