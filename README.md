# Fire OS 7 Framework Launcher Analysis

本專案分析研究者本人擁有或獲授權分析的 Amazon Fire HD 10 2021（KFTRWI）裝置，目標是以可重現證據釐清 Fire OS 7 的 HOME resolver、Home 鍵處理與 Fire Launcher 套件限制。

## 安全邊界

- 所有裝置腳本都要求明確 `--serial`。
- `--dry-run` 不執行 ADB 命令。
- baseline 腳本只執行唯讀命令。
- Home 事件腳本的 `input keyevent`、`am start` 與 `logcat -c` 必須通過互動式人工核准。
- 套件停用、標準 Home 設定測試、喚醒/解除鎖屏與重開機都屬於受控狀態變更；只有在使用者明確授權、指定 serial 且輸入腳本要求的核准字串後才執行。本輪已完成 `PACKAGE-T01`/`T02`/`T03`/`T04`/`T05`、`HOME-DEFAULT-T01`、`HOME-PREF-T01`、`HOME-PREF-T02`、`HOME-PREF-T03`、解鎖後有效矩陣 `HOME-T14`/`T15`/`T16`、`HOME-PREF-T17`、直接前景矩陣 `HOME-T18`/`T19`、Settings UI probes `HOME-T20`/`T21`/`T22`/`T23` 與 `REBOOT-T02`/`T03`，原始輸出均保留。`PACKAGE-T04` 是修正 `cmd package` 呼叫前的無效命令驗證紀錄，不作因果證據。
- DevicePolicy probe `POLICY-T01` 僅讀取 owner/admin/restriction 與相關套件狀態；Settings picker probes `SETTINGS-T01`/`T02`/`T03` 只切換前景並在結束時返回 Home，沒有選取 Launcher 或寫入預設 App 狀態。新增原始輸出均保留並通過 SHA-256 驗證。
- Component probes `COMPONENT-T01`/`T02` 對 Fire Launcher Home component 執行受控停用測試；`pm` 與 `cmd package` 都被同一 protected-package gate 拒絕，沒有留下 component state 變更。原始輸出均保留並通過 SHA-256 驗證。
- 本專案不執行 Root、DRM/帳號繞過、清除資料、factory reset、sideload 或 flash。
- 原始輸出使用唯一 run ID，已存在的檔案不覆寫。

## 第一輪使用方式

先檢查本機工具：

```sh
tools/scripts/check_tool_versions.sh
```

只查看計畫、不連接裝置採樣：

```sh
tools/scripts/collect_device_baseline.sh \
  --serial G001LT0511550CFT \
  --dry-run

tools/scripts/capture_home_event.sh \
  --serial G001LT0511550CFT \
  --test-id HOME-T01 \
  --duration 5 \
  --output adb/home-key-tests/HOME-T01 \
  --action manual \
  --dry-run
```

live baseline 只在人工確認後執行：

```sh
tools/scripts/collect_device_baseline.sh \
  --serial G001LT0511550CFT
```

Home 測試的 live action 必須另外加 `--approve-state-change`，並在提示時輸入精確核准字串。沒有該核准時，腳本不會執行 Home 事件。

若要控制鎖屏干擾，可在人工核准後加入 `--wake --dismiss-keyguard --prepare PACKAGE/ACTIVITY`；這些選項會將喚醒、滑動解除鎖屏與前景準備都記錄到測試 metadata，並保留 before/after 快照。

受控套件停用、Home preferred activity 與重開機測試：

```sh
tools/scripts/test_package_disable.sh \
  --serial G001LT0511550CFT \
  --package com.amazon.firelauncher \
  --user 0 \
  --output adb/package-tests/PACKAGE-T01 \
  --approve-state-change

# `--command cmd` tests the equivalent `cmd package` shell entrypoint.
tools/scripts/test_package_disable.sh \
  --serial G001LT0511550CFT \
  --package com.amazon.firelauncher \
  --user 0 \
  --command cmd \
  --output adb/package-tests/PACKAGE-T05 \
  --approve-state-change

tools/scripts/test_component_disable.sh \
  --serial G001LT0511550CFT \
  --component com.amazon.firelauncher/com.amazon.firelauncher.Launcher \
  --user 0 \
  --command cmd \
  --output adb/component-tests/COMPONENT-T02 \
  --approve-state-change

tools/scripts/test_home_activity.sh \
  --serial G001LT0511550CFT \
  --test-id HOME-DEFAULT-T01 \
  --target com.microsoft.launcher/.Launcher \
  --restore com.amazon.firelauncher/.Launcher \
  --approve-state-change

tools/scripts/reboot_verify.sh \
  --serial G001LT0511550CFT \
  --run-id REBOOT-T02 \
  --approve-state-change

tools/scripts/probe_alexa_mode.sh \
  --serial G001LT0511550CFT \
  --output adb/probes/ALEXA-MODE-T01

tools/scripts/probe_device_policy.sh \
  --serial G001LT0511550CFT \
  --test-id POLICY-T01 \
  --output adb/probes/POLICY-T01

tools/scripts/probe_home_settings.sh \
  --serial G001LT0511550CFT \
  --test-id HOME-T21 \
  --output adb/home-settings-tests/HOME-T21 \
  --approve-state-change

tools/scripts/probe_launcher_app_info.sh \
  --serial G001LT0511550CFT \
  --test-id HOME-T22 \
  --output adb/home-settings-tests/HOME-T22 \
  --approve-state-change

# Optional: tap only the visible Home-app row; do not select a candidate.
tools/scripts/probe_launcher_app_info.sh \
  --serial G001LT0511550CFT \
  --test-id HOME-T23 \
  --output adb/home-settings-tests/HOME-T23 \
  --tap-home-row --tap-x 600 --tap-y 1197 \
  --approve-state-change

# Optional: test whether the retained picker can be reached through an
# internal Settings route. This only changes foreground state and does not
# select a launcher.
tools/scripts/probe_settings_home_picker.sh \
  --serial G001LT0511550CFT \
  --test-id SETTINGS-T03 \
  --route advanced \
  --fragment com.android.settings.applications.defaultapps.DefaultHomePicker \
  --output adb/settings-tests/SETTINGS-T03 \
  --approve-state-change
```

`--dry-run` 可用於上述所有腳本。所有測試都會寫入 command manifest、原始輸出、摘要與 SHA-256 清單；不要把 `REBOOT-T01` 當作有效 post-boot 證據，因為它在 PackageManager service ready 前就擷取了快照。

## 證據標籤

- `Confirmed`：原始輸出直接支持的觀察。
- `Probable`：至少兩類獨立證據支持，但呼叫鏈仍有未確認環節。
- `Hypothesis`：待靜態或動態證據驗證的推論。
- `Disproved`：與可重現原始證據矛盾的假說。

腳本只產生原始輸出、狀態摘要與證據索引，不會自動宣稱 Amazon 的實作原因。

## 可重現分析索引

下列腳本只讀取已保存的輸出或反編譯文字，不會連接裝置；它們拒絕覆寫既有輸出，且支援 --dry-run：

- tools/scripts/extract_home_candidates.py
- tools/scripts/index_decompiled_classes.py
- tools/scripts/extract_method_signatures.py
- tools/scripts/compare_aosp_fireos.py
- tools/scripts/build_evidence_index.py
- tools/scripts/analyze_settings_home_ui.py
- tools/scripts/probe_device_policy.sh
- tools/scripts/probe_settings_home_picker.sh
- tools/scripts/test_component_disable.sh
- tools/scripts/generate_call_graph.py
- tools/scripts/render_final_report.py

第一輪已生成 output/tables/、output/call-graphs/ 與 output/rendered/ 中的結果。已取得官方 AOSP Android 9 `android-9.0.0_r1` 與 `android-9.0.0_r61` 的選定參考檔，並保留 `diff/reports/aosp-r1-vs-fireos-jadx/` 與 `aosp-r61-vs-fireos-jadx/` 的結構索引；這些索引不是 Amazon patch 的充分證據，且不能替代逐方法比對。

已取得官方相鄰版 Fire OS 7.3.3.1 / PS7331 OTA，位於 `firmware/original/`，並以 `VERSION_MISMATCH` 標示，因目前設備是 PS7330.4104N。PS7331 的解包、ext4 路徑擷取與 VDEX/ODEX 分析輸出僅作跨版本參考，不得當作目前設備的精確韌體證據。

AOSP 結構比對輸出位於 `diff/reports/aosp-r1-vs-fireos-jadx-phase3/` 與 `diff/reports/aosp-r61-vs-fireos-jadx-phase3/`，包含 `class_similarity.csv`、`method_signature_diff.csv`、`confidence_score.txt` 與 manual-review queue。score 只表示結構配對輔助值，不表示 Amazon 修改可信度。

## 第一輪結果

目前的初版結論與證據索引在：

- `findings/phase-1-report.md`
- `findings/evidence-index.md`
- `findings/home-flow.md`
- `findings/package-protection.md`
- `output/call-graphs/home-flow-phase1.txt`
- `output/call-graphs/home-flow-preliminary.txt`

核心結果是：HOME resolver 目前選 Fire Launcher 的可重現原因是 priority 50；解鎖後 Home key 仍走 Amazon hook 後的標準 resolver；`pm disable-user` 與只停用 `com.amazon.firelauncher/.Launcher` component 都由 PackageManager protected-package 路徑直接拒絕，並非本輪觀察到的 watchdog 恢復。Settings 的主要 Default apps XML 移除了 `default_home` row，但保留 controller/picker；Fire App info 的 Home row 只會導回沒有 Home selector 的頁面。裝置雖有 parental-controls Profile Owner，但其可見程式碼是 Fire Launcher 的 application restrictions，不是本次 package disable 例外的原因。Amazon 另有 `LauncherHijackPreventer` 控制 Home-task 可見性，但目前沒有證據顯示它直接啟動 Fire Launcher。

## Phase 2

Phase 2 located the protected-package gate and separated the AOSP base behavior from the Fire OS vendor extension:

- `PackageManagerService.setEnabledSetting()` calls `ProtectedPackages.isPackageStateProtected()` before enabled-state mutation.
- Fire OS adds `VendorProtectedPackagesCallback`; Amazon registers `ControlProtectedPackagesCallback`, which applies a system-app + deny-list + shell-UID rule.
- Fire Launcher’s HOME filter declares priority `50` in its manifest. Microsoft Launcher remains a query candidate at priority `0`.
- `set-home-activity` can write a preferred record but did not change the effective HOME result in the preserved PS7330.4104N test.

See `findings/phase-2-report.md`, `findings/evidence-index-phase2.md`, and `PUBLIC_REPOSITORY_SCOPE.md` for the evidence boundary of the public copy.

## Phase 3B: HOME selection control layer

Phase 3B is based on public commit `64a52ee` and does not repeat the Phase 3A
priority, `set-home-activity`, or five-APK experiments. The canonical device
baseline is `adb/phase3b/PHASE3B-BASELINE-20260803-02`; the clean path samples
are `HOME-PATH-EXPLICIT-02` and `HOME-PATH-KEYEVENT-02`. The earlier parallel
pilot samples remain archived but are not treated as independent evidence.
`PHASE3B-BASELINE-20260803-01` is also retained as a superseded pilot; all
conclusions use `-02`.

The Phase 3B tool inventory is recorded in `tools/tool_versions.phase3b.txt`.
Generate the Phase 3B derived reports offline:

```sh
python3 tools/scripts/analyze_phase3b.py --root . --force
```

The generator does not invoke ADB or write to a device. It produces:

- `findings/phase-3b-report.md`
- `findings/phase-3b-evidence-index.md`
- `findings/home-resolution-call-path.md`
- `findings/phase-3b-home-resolver-method-analysis.md`
- `findings/fire-launcher-privilege-matrix.csv` (machine-readable copy under `output/tables/`)
- `findings/aosp-vs-fireos-home-diff.md`
- `findings/framework-static-analysis.md`
- `findings/overlay-and-config-analysis.md`
- `findings/preferred-record-decision-tree.md`
- `output/call-graphs/home-resolution-phase3b.mmd`
- `output/call-graphs/home-resolver-method-flow-phase3b.mmd`

The Phase 3B result is intentionally bounded: Fire's effective priority 50
beats the priority-0 Microsoft candidate through an AOSP-shaped resolver
decision, while Amazon adds real ActivityStackSupervisor and Home-key callback
boundaries. The preserved data does not prove that a callback returns Fire, that
a persistent preferred HOME record is active, or that a background watchdog
rewrites the preferred record.

Phase 3B device collection is read-only except for clearing logcat buffers and
bringing the foreground to HOME for path observation. It does not disable Fire
Launcher, clear its data, modify settings/overlays/partitions, reboot, root, or
flash the device.
