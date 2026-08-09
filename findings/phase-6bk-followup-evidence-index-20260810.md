# Phase 6BK follow-up evidence index — 2026-08-10

| Evidence ID | Source | Observation | Interpretation | Confidence |
|---|---|---|---|---|
| `6BK-FU-UI-001` | `adb/child-profile-tests/CHILD-TEST-20260810-01/`, `CHILD-TEST-20260810-02/` | 官方 Tahoe Add Child Activity 可啟動，表單可進入並完成前景提交操作 | UI 入口存在且可由合法前景流程到達 | 已證實 |
| `6BK-FU-UI-002` | `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/users.stdout.txt`, `current_user.stdout.txt`, `home_user0.stdout.txt` | 提交後仍為 User 0；既有 User 10 保留；User 0 HOME 仍為 Fire priority 50 | 本次 UI 提交沒有形成可見的新 Android user 或 User-0 HOME replacement | 已證實 |
| `6BK-FU-UI-003` | `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/logcat_all.stdout.txt:1930,1959-1979,2125-2150,2231,2274-2280` | 觀察到 CreateAndroidUser、delegated-account、household model 與 HOUSEHOLD_UPDATED workflow | Tahoe 應用層建立／同步 workflow 確實被執行 | 高可信推論 |
| `6BK-FU-UI-004` | `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/logcat_all.stdout.txt:2667-2684` | DCP/ADM 回報 NoNetworkException，無法 register `com.amazon.tahoe` | 本地 user 建立未完成的可能阻斷點；不能單獨證明完整 rollback 原因 | 高可信推論 |
| `6BK-FU-UI-005` | `adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/firelauncher_package.stdout.txt` | Fire Launcher User 0 維持預設 enabled state；未出現停用／隱藏／suspend／uninstall mutation | KFT UI 提交沒有改變 User-0 Fire package state | 已證實 |
| `6BK-FU-BC-001` | `artifacts/phase6bk/protected-broadcast-union-20260810-02/summary.json` | 45 APK、0 AAPT failure；目標 protected broadcast 只有 1 個命中，來源為 `android.amazon.perm` | 在明確掃描集合中確認唯一來源及 system UID metadata | 已證實（掃描集合內） |
| `6BK-FU-BC-002` | `artifacts/phase6bk/protected-broadcast-union-20260810-02/summary.json`, `sha256sums.txt` | `device_contacted=false`、`binder_transaction_sent=false`、`broadcast_sent=false`、`ota_executed=false`、`partition_written=false` | 聯集掃描是 host-only，沒有裝置狀態副作用 | 已證實 |
| `6BK-FU-BC-003` | `artifacts/phase6bk/protected-broadcast-union-20260810-02/summary.json` | scope limitation 明確寫明只掃描 supplied APKs，不是完整 runtime inventory | 不可把單一命中擴張為所有 runtime package 的全域否定 | 已證實 |
| `6BK-FU-SAFE-001` | `tools/scripts/capture_phase6bk_child_profile_submission.py`; captures `05-POST-RO`、`06-POST-RO` | 腳本拒絕覆寫、支援 dry-run，capture 本身不建立 user、不切換 user、不改 package/settings | 後續狀態採集可重現且不增加裝置 mutation | 已證實 |

## Hash anchors

- 7.3.3.1 GPL source tar：`02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`
- PS7331 `boot.img`：`cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`
- `android.amazon.perm.apk`：`5b72bdfcfb91b28d2c751e548f60d406de5c3cbb235e47e232014abdebcdc058`
- protected-broadcast union manifest：`artifacts/phase6bk/protected-broadcast-union-20260810-02/sha256sums.txt`
- child-profile post capture manifest：`adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/sha256sums.txt`
