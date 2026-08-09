# Luna worker host inventory

日期：2026-08-10；範圍：只讀取公開 HEAD 與現有工作樹。未連接/修改真機，未執行 ADB、root exploit、未知 Binder/service call、ioctl、OTA、fastboot、reboot，未停用/清除/隱藏 Fire Launcher。

## 1. 工作樹

| path | evidence/hash | test/phase | 結論 |
|---|---|---|---|
| PROJECT_STATUS.md, README.md, findings/, artifacts/, adb/ | HEAD 7342a3f6f95ffbe412598baea12ad835d6420716；工作樹有大量 modified/untracked phase records | git/worktree inventory | HEAD 是 Phase 6MA deny-list/KFT closure；工作樹另含後續未提交 Phase 6BK 輸出。未 reset/clean/revert。 |
| work/luna_worker_inventory.md | 建立前 test -e 回報 REPORT_ABSENT | 本次 | 新增檔案，不覆蓋既有檔案。 |

## 2. 7.3.3.1 kernel/source/boot/OTA

| path | evidence/hash | test/phase | 結論 |
|---|---|---|---|
| firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2 | SHA-256 02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea; 2,563,328,975 bytes | 5DA/5BT | 官方 source bundle，保存且未執行。 |
| firmware/extracted/PS7331-SOURCE-20250617/ | platform.tar SHA 69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd; fireos.tar SHA bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369 | 5DA | source root；platform 124,234 files、fireos 49,301 files；host-only provenance，不等於簽署 Image。 |
| firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/ | rtmutex.c SHA 6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde; futex.c SHA ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96 | 5BE/5BT/5DA | build-selected MT8183 4.4/trona_defconfig/arm64；pre-fix current->pi_blocked_on 靜態 pattern；不證明 runtime exploitability/root。 |
| firmware/extracted/.../arch/arm64/configs/trona_defconfig | SHA 09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac | 5DA | 精確 trona config；不是最終簽章 kernel hash。 |
| firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin | SHA-256 9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5; 1,301,005,356 bytes | 5BH/5CI/6BP | Amazon 官方導向的 PS7331.4463N full BLOCK OTA；不是 PS7330 exact-match。 |
| firmware/manifests/OTA-20260803-01/README.md, sha256sums.txt | 同上 OTA SHA；README 有官方 redirect/support URL 與 VERSION_MISMATCH | 5BH | OTA provenance 已索引。 |
| firmware/extracted/PS7331/boot.img | SHA-256 cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b | 5AO/5BA/5DB | PS7331 adjacent-version boot；不能單獨替換 PS7330。 |
| artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.Image | SHA-256 10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d | 5AO | 保存的 signed kernel Image；與 source pre-fix marker 一致，但非 exact installed PS7330 Image。 |
| artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/, artifacts/phase6bp/ota-path-audit-20260805-02/ | 既有 sha256sums.txt、updater-script、members.tsv、ota-path-audit.json | 5BD/6BP | 固定 27-entry package、system/vendor block-image、boot/preloader/LK/TEE/SPMFW/SSPM/camera VPU targets；無 symlink/traversal/dynamic post-install。未執行 updater/recovery。 |
| artifacts/phase5/phase5da-ps7331-source-tree-index-20260804-01/ | metadata: file_count 173535、focused 1094、offline_only=true、source_executed=false、device_touched=false | 5DA | 可作 evidence index；未全量反編譯/build。 |

補充：PS7330 source archive firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2 SHA-256 569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665。PS7330 與 PS7331 資產不可交叉標為 exact-match。

## 3. Phase 3–6 已完成結果

| path | evidence/hash | test/phase | 結論 |
|---|---|---|---|
| tools/test-launcher/, tools/test-launcher/dist/20260803-jdk26/ | APK、phase3a-launcher-source.tar.gz、build-manifest 與既有 SHA manifests | 3A–4 | Launcher/HOME/foreground artifacts 已保存；測試 launcher/Lock Task 不等於正式 HOME resolver replacement。 |
| findings/phase-6bn-fire-alt-enabled-state-boundary.md; adb/phase6bn/... | state 2/3/4 與 Fire component state 均 protected rejection | 6BN | User 0 shell 無法 disable、disable-until-used 或 component-state 移除 Fire；HOME 仍 Fire priority 50。 |
| findings/phase-6ea-fire-uninstall-user0-protected-boundary.md; adb/phase6ea/... | logcat: Attempted to delete protected package: com.amazon.firelauncher | 6EA | uninstall 在 PMS gate 前拒絕；Fire 未變，無 User-0 replacement。 |
| findings/phase-6ai-denylist-flow-closure.md; artifacts/phase6ai/denylist-flow-20260805-02/; findings/phase-6az-denylist-resource-closure.md | /data/system/PackageManagerDenyList system:system 0660 size 2645，content 不可讀；resource seed 含 Fire literal | 6AI/6AZ/6DK | ControlProtectedPackagesCallback 接到 VendorProtectedPackagesCallback；條件含 system/privileged、deny-list membership、UID 2000。Arcus refresh 不等於 package/HOME writer。 |
| findings/phase-6bk-report.md; findings/phase-6bk-evidence-index.md; artifacts/phase6bk/ipc-ota-closure-20260810-02/ | fosservices/disassembly.log SHA ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c；lines 54297–54325, 370295–370344, 371789–371861 | 6BK | createChildUser -> enableKftLauncher -> component helper 可對 child user 啟用 Tahoe、將 Fire/Launcher3 state 設 2；是 static system-service capability，非 shell User-0 route。 |
| findings/phase-6ec-kft-tx3-reachability-boundary.md; adb/phase6ec/... | service check not found；binder_transaction_sent=false；dispatch_attempted=false | 6EC | tx3 static writer 已閉合，但 shell/service-manager/SELinux 在 Binder handle 前停止；非 confirmed vulnerability。 |
| findings/phase-6cb..., phase-6cc..., phase-6dz... | User 10/11 Tahoe Profile Owner、child HOME priority 975；User 0 Fire priority 50 | 6CB/6CC/6DZ | child KFT/Tahoe state 與 static model strong correspondence；未證實 User-0 restoration。 |
| findings/phase-6bo-binder-contract-and-reachability-audit.md; artifacts/phase6bo/binder-contracts-20260805-04/ | 49 services/360 AIDL rows；無 shell handle for hidden launcher services | 6BO | Amazon Binder/permissions/caller markers host-side 閉合；無未知 transaction。 |
| findings/phase-6bp-ota-post-install-path-audit.md; artifacts/phase6bp/ota-path-audit-20260805-02/; findings/phase-6ag... | updater/path audit 與 BootAfterSystemOTAReceiver source | 6AG/6BP/6BK | OTA/OOBE 是 guarded privileged lifecycle，不是普通 HOME selector；無已證實 low-privilege write chain。 |
| findings/phase-6ct-ota-compatibility-exported-boundary.md; findings/phase-6dq-ota-compatibility-runtime-boundary.md | controller permission signature|privileged；Activity 未安全啟動 | 6CT/6DQ | exported privileged OTA surface confirmed；普通 app/shell 可達性及安全利用未驗證。 |

## 4. 尚未驗證但值得追蹤的 host-only 線索

| path/clue | evidence/hash | test/phase | 結論/限制 |
|---|---|---|---|
| decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325,54415-54478,55094-55118 | KFT helper、child predicate、identity-clear | 6BK/6EC | 只追蹤自然發生 child lifecycle 與 exact attribution；不要 replay tx3/forged UserInfo。 |
| Phase 6AI resource 0x7e05000a / packages_deny_list | resource seed includes Fire；live persisted set inaccessible | 6AI/6AZ | 可做 resource naming/content correlation；不能稱 live membership 已直接觀察。 |
| Amazon profile service VDEX lines 76246–77266, 78949–78966 | explicit profile UI / Amazon guards | 6BK/6DJ | 追蹤 Profile Owner/backup-restore caller chain；尚無 User-0 preferred HOME writer。 |
| output/tables/phase6bo-binder-contracts.csv 與 Phase 6BO artifacts | 49 service rows/360 methods | 6BO | 可做 matrix consistency/caller provenance；service-list visibility 不等於 Binder handle。 |
| artifacts/phase6u/bootafter-ota-scope-20260805-01/ 與 Phase 6BP audit | guarded receiver predicates/fixed OTA targets | 6U/6BP | 只做 static sender/receiver/state model；不要 crafted OTA、broadcast replay、recovery/updater。 |
| firmware/extracted/PS7331-SOURCE-20250617/platform/ 與 phase5DA focus-paths.tsv | 173535-file index/1094 focus hashes | 5DA/5BE | 精確搜尋未覆蓋 kernel/user-surface provenance；不要全量反編譯/build/執行。 |
| kernel.Image、boot.img | hashes above; source/Image pre-fix correspondence | 5AO/5BA/5BT | 可做 marker/format/provenance comparison；不能推導 exact PS7330 Image、KASLR/credential offsets、root。 |

## 5. 最終證據分類

- Confirmed：HEAD identity；PS7331 source/OTA/boot paths and hashes；trona/MT8183 source selection；fixed OTA targets；Fire User-0 PMS protected boundaries；deny-list callback flow；KFT internal child writer；Amazon Binder matrix/handle boundary；child Tahoe state與User-0 Fire priority 50。
- Strong evidence：PS7331 source/Image pre-fix semantic correspondence；User 10/11 state corresponds to KFT model；resource seed contains Fire；OTA/OOBE is guarded lifecycle。
- Probable：live persisted deny-list contains Fire（resource seed plus rejection，live literal 未讀）；exact KFT method caused each existing profile state。
- Hypothesis：trusted Profile Owner/backup-restore/post-OTA lifecycle 可能揭示 authorized User-0 writer；目前無 caller-controlled route。
- Disproved：ordinary shell User-0 Fire disable/disable-until-used/component-state/uninstall；shell KFT tx3 route；standalone PS7331 boot as equivalent PS7330 upgrade；audited OTA traversal/dynamic post-install；Arcus refresh as direct launcher writer。
- Unknown：exact PS7330 matching 7.3.3.1 package；live deny-list literal；unreviewed trusted User-0 HOME writer；runtime exploitability/root；dynamic OTA configuration/private Binder callers。

## 6. 本次檢查過的命令

```sh
pwd
git status --short --branch
git rev-parse HEAD
git log -1 --oneline --decorate
rg --files
rg --files | rg 'kernel|boot|ota|OTA|source|manifest|launcher|deny|kft|user10|binder'
rg -n -i '7\.3\.3\.1|kernel source|kernel\.Image|boot\.img|SHA-256|OTA'
test -e work/luna_worker_inventory.md
ls -lh firmware/original firmware/extracted/PS7331 firmware/extracted/PS7331-SOURCE-20250617
sha256sum firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2
sha256sum firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2
sha256sum firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin
sha256sum firmware/extracted/PS7331/boot.img
sha256sum artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.Image
sed -n '<精確 line-range>' PROJECT_STATUS.md README.md findings/*.md
```

最後一行代表本次實際使用多個精確 line-range 的 sed -n 讀取既有報告；沒有執行全量反編譯、source build、ADB 或任何真機命令。
