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
- 本專案不執行未經精確 Level 3 核准的 Root、DRM/帳號繞過、清除資料、factory reset、sideload 或 flash；已核准的 Root control 嘗試仍禁止自行擴張操作範圍。
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

## Phase 3C: HOME selection state mutation experiments

Phase 3C builds on the Phase 3B public evidence and does not repeat the Phase
3A priority APK matrix. It adds an explicit, plan-driven state snapshot and
rollback workflow:

```sh
tools/scripts/capture_phase3c_state.sh \
  --serial G001LT0511550CFT \
  --test-id PHASE3C-BASELINE-YYYYMMDD-01 \
  --output adb/phase3c/PHASE3C-BASELINE-YYYYMMDD-01

tools/scripts/run_phase3c_preferred_experiment.sh \
  --serial G001LT0511550CFT \
  --test-id PHASE3C-PREFERRED-P0-XX \
  --apk tools/test-launcher/dist/20260803-jdk26/org.fireosresearch.home.p0.apk \
  --output adb/phase3c/PHASE3C-PREFERRED-P0-XX \
  --lock-unlock --reboot --approve-state-change
```

The mutation runner accepts only the p0 research launcher, writes only an
ordinary preferred HOME record, and restores Fire Launcher as the preferred
component before removing the test package. `restore_phase3c_state.sh` uses an
explicit plan rather than replaying all settings; it rejects Fire Launcher
package/component state changes. `compare_phase3c_state.py` compares saved
snapshots without contacting the device, and `analyze_phase3c.py` generates
the derived reports and matrices offline.

The canonical Phase 3C baseline is
`adb/phase3c/PHASE3C-BASELINE-20260803-02`; the corrected controlled experiment
is `adb/phase3c/PHASE3C-PREFERRED-P0-02`. `PHASE3C-PREFERRED-P0-01` is retained
as a harness-error record and is not causal evidence. Raw outputs and
supplemental final SHA-256 manifests are preserved under `adb/phase3c/`.
`PHASE3C-PREFERRED-P0-03` is a same-scope repeat made only to add event-level
logcat capture; it has the same restored result and is included as
`P3C-LOGCAT-001`.

Observed result: the p0 package could be installed and an exact
MAIN+HOME+DEFAULT `mAlways=true` preferred record survived one reboot, but
resolver, Home key, explicit HOME, lock/unlock, and foreground state remained
with `com.amazon.firelauncher/.Launcher`. The record was then restored to Fire
Launcher and p0 was removed. HOME role output and `device_config` were
unavailable on this build; no related mutable overlay or shell-writable setting
was justified for mutation. This is evidence that the ordinary preferred
record is writable but ineffective against the observed priority-50 Fire
candidate, not proof of a unique Amazon resolver patch.

Phase 3C outputs:

- `findings/phase-3c-report.md` and `findings/phase-3c-evidence-index.md`
- `findings/phase-3c-settings-key-analysis.md`
- `findings/phase-3c-preferred-activity-analysis.md`
- `findings/phase-3c-home-callback-analysis.md`
- `findings/phase-3c-overlay-analysis.md`
- `findings/phase-3c-fallback-analysis.md`
- `findings/phase-3c-workaround-classification.md`
- `findings/phase-3c-risk-register.md`
- `findings/phase-3c-settings-key-inventory.csv`
- `output/tables/phase-3c-settings-matrix.csv`
- `output/tables/phase-3c-experiment-matrix.csv`
- `output/call-graphs/phase-3c-home-state-flow.mmd`

No Root, Fire Launcher disable/hide/suspend/uninstall, Fire data clear,
partition write, framework injection, Device Owner setup, or crash-loop
fallback test was performed in Phase 3C.

## Phase 4: core hypothesis validation and reversible controls

Phase 4 starts from public commit `b3d85d7`/Phase 3C. It does not repeat the
five-APK priority matrix or ordinary `set-home-activity` persistence test.
The AOSP Android 9 model and Fire method comparison are generated offline:

```sh
python3 tools/scripts/model_aosp9_home_resolution.py --scenario fire-vs-p0 --pretty
python3 -m unittest tests/test_aosp9_home_resolution.py
python3 tools/scripts/generate_phase4_reports.py --force
```

The model implements the Android 9 top-field gate: when the leading HOME
candidates differ in `priority`, `preferredOrder`, or `isDefault`,
`chooseBestActivity()` returns the first result before ordinary preferred
lookup. This reproduces the Phase 3C Fire-versus-p0 observation. The Fire OS
artifact also has an Amazon pre-PM resolve callback and a resolver-index filter
callback; their current HOME return values remain unresolved.

The one live Phase 4B candidate-composition run is
`adb/phase4/PHASE4-ALIAS-T04`. It installs one multi-activity/alias APK,
captures candidates, explicitly starts its components, observes implicit HOME
and Home key, then removes the APK. It never calls `set-home-activity` or
mutates Fire Launcher. The raw evidence and rollback diff are preserved with a
SHA-256 manifest. The result remained Fire and the test package was absent
after rollback.

The source-only user-consented Accessibility approximation is documented under
`tools/phase4-accessibility/` and is driven by
`tools/scripts/run_phase4_accessibility_experiment.sh`. The live T03 run
required manual Settings consent, recorded 30 explicit redirect attempts, and
observed 0/30 resumed/focused handoffs; Fire remained the resumed activity.
It is therefore **已排除** as a reliable Home-key workaround for this
implementation/build, not a true HOME replacement. The service was manually
disabled and both test APKs were removed; the verified rollback is under
`adb/phase4/PHASE4-ACCESSIBILITY-T03/`.

Device Owner/provisioning, Fire package mutation, unknown Binder calls, core
overlay changes, and deliberate HOME crash/fallback tests are explicitly
rejected in `findings/phase-4-risk-register.md`.

## Phase 5: low-level and MTK compatibility boundary

Phase 5 records a read-only low-level inventory for the exact device and
separates it from any bootloader or MTK operation. The canonical baselines are
`adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-01` and the post-root-test
recheck `adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-02`; their per-command
output, errors, metadata, summaries, and SHA-256 manifests are preserved. The
collection script is:

```sh
tools/scripts/capture_phase5_low_level_baseline.sh \
  --serial G001LT0511550CFT \
  --test-id PHASE5-LOWLEVEL-BASELINE-20260803-01 \
  --output adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-01
```

The script is observational only. It does not reboot, enter bootloader mode,
unlock, remount, invoke an exploit, or write Android state or a partition. It
also supports `--dry-run` and refuses to overwrite an existing evidence
directory.

The device baseline is `KFTRWI/trona`, MT8183, Fire OS 7.0 / Android 9,
PS7330.4104N, security patch 2024-02-01, `flash.locked=1`, verified boot
`green`, unlocked kernel `false`, RPMB state `2`, and SELinux enforcing. Fire
Launcher is a privileged system APK at
`/system/priv-app/com.amazon.firelauncher/`.

The reports distinguish the Amazon PackageManager deny-list callback from the
LauncherHijackPreventer task-visibility callbacks. They also document the
literal Fire references in the special KFT/child-user path without treating
that path as proof of the normal User 0 HOME resolver cause:

- `findings/phase-5-low-level-inventory.md`
- `findings/phase-5-amazon-hijack-preventer-analysis.md`
- `findings/phase-5-mtk-compatibility-review.md`
- `findings/phase-5-evidence-index.md`
- `output/tables/phase5-low-level-compatibility.csv`

The exact bootloader/MTK compatibility evidence is incomplete. The repository
contains PS7331 preloader/LK artifacts, while the device is PS7330; those files
are marked `VERSION_MISMATCH` and must not be flashed. No exploit, DA upload,
seccfg change, bootloader unlock, fastboot write, or partition operation was
executed.

The two-stage metadata check was subsequently executed under separate explicit
approval: `adb reboot bootloader`, read-only `fastboot getvar product`, the
locked-hardware rejection responses for other getvars, and
`fastboot reboot`. The device returned to Android with the same fingerprint,
green verified boot, and `flash.locked=1`. No unlock, write, erase, payload,
DA, or flash command was run. Raw evidence is under
`adb/phase5/PHASE5-BOOTLOADER-TRANSITION-20260803-01/`,
`PHASE5-FASTBOOT-GETVAR-20260803-01/`, and
`PHASE5-FASTBOOT-REBOOT-20260803-01/`.

The adjacent OTA's boot-chain boundary is additionally documented in
`findings/phase-5-exact-ota-and-boot-chain-evidence.md`. Its updater script
contains writes for preloader, LK, boot, TEE, SPMFW, SSPM and VPU partitions;
its preloader strings include RPMB anti-rollback and DA authentication paths.
The offline reproduction script is
`tools/scripts/inspect_phase5_boot_chain_artifact.sh`, with derived output in
`artifacts/phase5/PS7331-preloader-review/`. These are PS7331 artifact-scoped
observations and do not authorize use on the installed PS7330 build.

The public-method compatibility review is in
`findings/phase-5-public-method-compatibility.md`; it separates exact-device
evidence from historical Fire Toolbox/LauncherHijack reports and generic MTK
tool capability.

### Additional ADB package-state routes

Three distinct user-0 routes were tested once each, without repeating the
previous component-disable experiment:

- `pm suspend --user 0 com.amazon.firelauncher` was blocked by missing
  `SUSPEND_APPS`.
- `pm hide --user 0 com.amazon.firelauncher` was blocked by missing
  `MANAGE_USERS`.
- `pm uninstall --user 0 com.amazon.firelauncher` returned
  `DELETE_FAILED_INTERNAL_ERROR` and logged an explicit protected-package
  deletion warning.

All three left Fire Launcher, HOME, foreground focus, and ADB intact. Evidence
is in `findings/phase-5-adb-surface-tests.md`,
`adb/mutation-tests/PM-SUSPEND-FIRE-T01/`,
`PM-HIDE-FIRE-T01/`, and `PM-UNINSTALL-FIRE-T01/`. The uninstall route's
idempotent `pm install-existing --user 0 com.amazon.firelauncher` rollback was
verified.

### `mtk-easy-su` audit

The public `KoCleo/mtk-easy-su` repository was reviewed at pinned commit
`8c6871ac7c15b8e98a47e25c35ab93b87e260475`. A staged, non-root APK test was
subsequently completed and rolled back; the exploit control and LFS payload
were not run. Its source extracts `mtk-su`/Magisk assets and runs a
data-partition shell script, but its own warning treats post-March-2020
firmware as potentially blocked and its tested-device table has no KFTRWI,
trona, or MT8183 entry. The device is PS7330 with a 2024-02 patch, enforcing
SELinux, locked boot state, and green verified boot. This remains a historical
lead rather than a supported root path.

Audit artifacts and the explicit Level 3 rejection are in:

- `findings/phase-5-mtk-easy-su-review.md`
- `findings/phase-5-mtk-easy-su-apk-test.md`
- `artifacts/phase5/mtk-easy-su-audit-20260803/`
- `findings/phase-5-evidence-index.md` (`P5-WEB-007`, `P5-WEB-008`, `P5-APK-001`–`P5-APK-003`)

The user-provided HackMD vulnerability index was also triaged against the
device's exact hardware and kernel. Qualcomm-only chains, listed OPlus/fenrir
device-specific boot-chain projects, and Dirty Pipe were rejected by hardware
or kernel prerequisites; no exploit code was run. The evidence is in
`artifacts/phase5/hackmd-vulnerability-review-20260803/` and the proposed
`mtk-easy-su` APK operation is explicitly gated by
`findings/phase-5-mtk-easy-su-level3-approval.md`.
The exact staged APK record is in `adb/phase5/MTK-EASY-SU-APK-T01/`, with
read-only pre/post snapshots under the corresponding `-PRE` and `-POST`
directories. The local APK binary remains ignored; its release digest and
static inspection outputs are publishable.

The first Root-control attempt is recorded in
`findings/phase-5-mtk-easy-su-root-test.md`: it stopped at the visible
superuser warning and was rolled back. A later device-side observation is
recorded in `findings/phase-5-mtk-easy-su-root-followup.md`. It shows the APK
reached its ordinary-user device preflight, but no UID-0, successful `su`, or
`/sbin/su` signal was captured; the practical result is failed/no confirmed
root. The device returned to Fire Launcher and the package was absent.

The offline payload inspection is reproducible with
`tools/scripts/inspect_mtk_easy_su_payload.sh`; it never executes extracted
assets. The resulting hashes and selected static review are under
`artifacts/phase5/mtk-easy-su-audit-20260803/payload-inspection-20260803/`
and summarized in `findings/phase-5-mtk-easy-su-payload-analysis.md`. A
further device-side retry would require a new exact Level 3 scope.

### Phase 5B — failed root boundary and MTK next route

The failed Root-control result and the new shell-readable preloader/LK
identity properties are summarized in
`findings/phase-5b-root-failure-and-route-matrix.md`. The device exposes
`ro.boot.pl_build_desc=d1a4a4b-20231011_072631` and
`ro.boot.lk_build_desc=79172a1-20231008_072039`, but no matching PS7330
preloader, DA/auth state, or recovery set has been found. The bootreason
`wdt_by_pass_pwk` is unchanged from the earlier baseline and is retained as
metadata only.

The public `amonet` chain targets Fire HD 8 (2018)/KFKAWI, not this
KFTRWI/trona tablet. The public MTKClient MT8183 alias remains a generic
compatibility lead; its documented root/unlock paths include boot/vbmeta writes,
seccfg changes, and userdata/metadata erasure. No BROM probe, DA upload,
payload, unlock, erase, or partition write was executed. The proposed boundary
is documented in `findings/phase-5b-brom-identification-level3-report.md` and
is not approval-ready.

### Phase 5C — exact-version source and loader search

The public Amazon S3 source archive
Fire_HD10-7.3.3.0-20240730.tar.bz2 was identified and inspected through a
bounded HTTP range. It is a 2.59 GB source/build-material archive, not an OTA,
preloader, LK image, DA, or recovery package. The retained prefix and exact
headers are under
artifacts/phase5/exact-source-search-20260803/; the repeatable collector is
tools/scripts/inspect_phase5_exact_source_metadata.sh. The archive README
references kernel, BusyBox, U-Boot and AOSP android-9.0.0_r1 build flows, but
the bounded inspection does not establish a signed PS7330 boot-chain set.

Historical update-endpoint redirects and the current public trona metadata
sequence were also checked. The retained snapshots contain PS7319, PS7322,
PS7323, PS7326, PS7328 and PS7331 targets, while the independent metadata
sequence contains PS7319, PS7321–PS7324, PS7326–PS7329 and PS7331; no PS7330
URL was recovered. This is a search boundary, not proof that Amazon never
published a PS7330 package. No new BROM, DA, payload, unlock, write, erase or
partition operation was executed.

A bounded tail sample of that exact-version source archive recovered the
MT8183 kernel tree, including `mt8183_defconfig`,
`mt8183_debug_defconfig`, and `mt8183.dts`. The sample did not yield an exact
MTK preloader or LK source path; the only exact `kernel/` u-boot paths were
generic AVR32 references. The range hash, commands, limits, and compact
results are under `artifacts/phase5/exact-source-search-20260803/tail-sample-*`.
The repeatable host-only collector is
`tools/scripts/inspect_phase5_exact_source_tail.sh`. This does not change the
device and does not create a flashable image.

### Phase 5D — Amazon LK unlock surface and public-route review

After the failed `mtk-easy-su` root-control test, a host-only review pinned
`lkpatcher`, `pwnage24mtk`, and `fenrir` and compared them with the adjacent
PS7331 bootloader artifacts. The PS7331 LK contains Amazon-specific strings
for `amzn_verify_unlock`, temporary unlock code/certificate handling,
`flash:tucert`, `getvar:unlock_status`, and a reboot-count-limited temporary
unlock state. This is a real artifact-scoped bootloader surface, not a public
unlock credential or an ADB setting.

The public `lkpatcher` default needles matched the adjacent LK zero times;
`pwnage24mtk` did not find a CERT1/CERT2 target in the available LK/preloader
pair; and `fenrir` has no `trona`/`KFTRWI`/MT8183 device profile. A bounded read
of the installed PS7330 LK through the Android shell returned `Permission
denied`, so the exact installed LK cannot currently be matched without a
privileged or low-level route. The IDME HAL is listed by `lshal`, but no shell
`idme` command or `dumpsys idme` service is available.

The review is under
`findings/phase-5d-amazon-unlock-surface.md` and
`artifacts/phase5/public-lk-route-review-20260803/`. No BROM, DA, certificate,
unlock, `seccfg`, reboot, erase, or partition operation was executed. A future
Amazon certificate test needs a separate exact Level 3 report with a matched
PS7330 LK, signed credential, protocol, and recovery plan.

### Phase 5E — CVE-2020-0069 / MTK-CMDQ surface review

The exact PS7330 device exposes `/dev/mtk_cmdq` with the
`mtk_cmdq_device` SELinux label; the shell's read-permission check passes but
its write-permission check fails. No open or ioctl was attempted. This is a
driver-surface observation, not proof that the historical
CVE-2020-0069 ioctl flaw remains present. The device is on a 2024-02-01 patch
with a 4.4.146+ kernel, and the archived `mtk-su64` binary contains generic
unsupported-firmware strings without an exact PS7330/trona marker.

The read-only collector is
`tools/scripts/capture_phase5e_cmdq_surface.sh`; evidence is under
`artifacts/phase5/cve-2020-0069-surface-20260803/`, and the analysis is in
`findings/phase-5e-cve-2020-0069-surface.md`. The exact operation
`MTK-SU-CMDQ-T03` was later approved and executed once through
`tools/scripts/run_mtk_su_cmdq_t03.sh`. The verified payload exited with
`Failed critical init step 3`, produced no root marker, and left the device in
the same ADB/SELinux/HOME state. Its temporary directory was removed and the
before/after evidence manifest is under
`adb/phase5/MTK-SU-CMDQ-T03/`. This is evidence against that archived payload
on PS7330, not proof that CVE-2020-0069 is absent from the kernel; any further
exploit variation requires a new exact Level 3 approval.

The direct-test report is `findings/phase-5e-mtk-su-t03-result.md`, and the
new evidence rows are `P5E-CMDQ-007` through `P5E-CMDQ-012` in
`findings/phase-5-evidence-index.md`.

The host-only static mapping of the direct error is in
`findings/phase-5e-mtk-su-t03-static-init.md`. It identifies `Failed critical
init step 3` as the payload's failed `CMDQ_IOCTL_ALLOC_WRITE_ADDRESS`
initialization branch (`0x40087807`), while keeping the exact driver errno and
kernel CVE status explicitly unknown. Reproduce the analysis with
`tools/scripts/analyze_mtk_su64_init_failure.py`; it never executes the payload
or invokes ADB. Derived disassembly, strings, JSON findings, and hashes are in
`artifacts/phase5/mtk-su64-static-init-analysis-20260803/`.

### Phase 5F — exact CMDQ source follow-up

The host-only follow-up extracted compact, line-numbered members from the
official Fire HD 10 7.3.3.0 source archive. The exact `mt8183_defconfig`
selects CMDQ, the top-level CMDQ Makefile selects `v3/` for mt8183, and the
retained v3 dispatcher has no `CMDQ_IOCTL_ALLOC_WRITE_ADDRESS` (#7) case; it
returns `-ENOIOCTLCMD` for unknown requests. The archived T03 payload requests
that v2 operation and fails at its step-3 initialization branch. This is the
leading source-scoped explanation, not proof of the installed kernel's exact
compiled driver or of CVE-2020-0069 status.

The public compact evidence, hashes, and bounded-range metadata are under:

- `findings/phase-5f-exact-cmdq-source-followup.md`
- `artifacts/phase5/exact-source-search-20260803/cmdq-source-members-20260803-v5/`
- `artifacts/phase5/exact-source-search-20260803/cmdq-range-2450m-2535m-summary.md`
- `tools/scripts/scan_phase5_exact_source_cmdq.sh`
- `tools/scripts/extract_phase5_source_members.py`

A subsequent read-only runtime capture read `/proc/config.gz`, module lists,
device-node metadata, and IRQ metadata. It confirmed the installed kernel's
`CONFIG_MTK_PLATFORM="mt8183"`, `CONFIG_MTK_CMDQ=y`, and
`CONFIG_MTK_CMDQ_TAB=y`; the raw capture and manifest are under
`adb/phase5/PHASE5F-CMDQ-RUNTIME-20260803-02/`, with the interpretation in
`findings/phase-5g-runtime-cmdq-corroboration.md`. This raises the v2/v3
payload mismatch to a high-confidence inference, while the compiled driver
identity and CVE status remain unverified.

The bounded low-level discriminator is documented in
`findings/phase-5h-cmdq-ioctl-compat-level3-report.md` and its result is in
`findings/phase-5h-cmdq-ioctl-result.md`. The host-built AArch64 probe at
`artifacts/phase5/cmdq-compat-probe-build-20260803-03/cmdq_compat_probe` with
SHA-256
`e0077240040bce55099b8b1b28d9d10723357ef3d3b9640282bd6f6bef2f11fb`. It
performed one approved `count=0` ioctl #7 call and returned raw `-25`
(`-ENOTTY`), matching the exact MT8183 CMDQ v3 unsupported-request path. The
run did not allocate a non-zero buffer, obtain Root, or change device state;
raw output and before/after captures are under
`adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/`. The approval is consumed;
any follow-up ioctl, v3-aware payload, kernel-memory primitive, BROM/DA action,
or boot-chain write remains a new Level 3 task.

No exploit, v3-aware payload, kernel-memory primitive, BROM/DA action, or
boot-chain write was performed. The one bounded CMDQ compatibility probe is
the separately recorded P5H-CMDQ-003 run; any follow-up ioctl or lower-level
operation remains a new Level 3 task.

### Phase 5I — MT8183 IMS / ATCI applicability triage

Phase 5I added a read-only runtime triage for the public MediaTek IMS findings
that list MT8183 and Android 9 software families. The exact device remained
`Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`,
SELinux Enforcing, green verified boot, and ADB `device` throughout.

The normal runtime enumeration found no `ims` or `atcid` Binder service, IMS
package, or IMS/ATCI process. It found `imms` (MMS) and
`telephony.registry`. Shell-readable vendor init files define
`atcid-daemon-u` and `audio-daemon` as disabled/oneshot services; `atcid` is
conditionally started only by explicit `persist.vendor.service.atci.*`
property triggers. Shell attempts to hash or pull the relevant vendor
executables were denied by the device's visibility boundary. These results do
not establish whether the vendor binaries are patched or vulnerable.

Raw, independently hashed evidence is under:

- `adb/phase5/PHASE5I-IMS-TRIAGE-20260803-01/`
- `adb/phase5/PHASE5I-IMS-TRIAGE-FOLLOWUP-20260803-01/`
- `adb/phase5/PHASE5I-IMS-TRIAGE-FOLLOWUP-20260803-02/`
- `adb/phase5/PHASE5I-IMS-TRIAGE-FOLLOWUP-20260803-04/`

The reproducible collector is
`tools/scripts/capture_phase5i_ims_triage.sh`; use `--dry-run` for host-only
validation. The interpretation and explicit safety boundary are in
`findings/phase-5i-ims-atci-triage.md`, with evidence rows `P5I-IMS-001`–
`P5I-IMS-005` and `P5I-WEB-001` in `findings/phase-5-evidence-index.md`.

No ATCI property was written, no vendor daemon was started, no AT command or
unknown Binder transaction was sent, and no new exploit or boot-chain action
was performed. Any such follow-up requires a new exact risk report and
authorization; the consumed `CMDQ-IOCTL-V3-COMPAT-T01` approval does not
extend to IMS/ATCI.

### Phase 5J — Bluetooth / MT8183 Android 9 applicability triage

Phase 5J is a read-only review of the exact PS7330 Bluetooth surface. The
device-side snapshot reported Bluetooth disabled, never enabled, zero crashes,
and `Bluetooth Service not connected`; raw process, service, property, init,
package, and HOME outputs are retained. The exact `com.android.bluetooth`
APK, ARM64 ODEX/VDEX, system Bluetooth libraries, permission XML, and init
configuration were pulled without crossing the shell visibility boundary.
Vendor HAL and kernel-module pulls failed with permission denied and are kept
as failed evidence.

The exact VDEX contains Amazon-specific
`AmazonBtPolicyManagerAdapter` and `FosGattService` classes. They add BTPM/LE
policy and GATT callback paths protected by Bluetooth/admin/privileged checks;
the focused slice contains no Fire Launcher, PackageManager, HOME, or shell-UID
privilege transition. The Bluetooth manifest uses shared UID
`android.uid.bluetooth`/UID 1002 and receives high privileges, but this is not
an ADB shell route or root evidence. Public MediaTek MT8183/Android 9 CVE
scope is recorded as external applicability only; exact PS7330 patch status
and exploit reachability remain unknown.

The host-only focused extractor is
`tools/scripts/extract_phase5j_bluetooth_focus.py`; it supports `--dry-run`,
refuses overwrite, and never executes device or binary code. Derived class and
call-site slices are under
`artifacts/phase5/phase5j-bluetooth-static-analysis-20260803/`. The report and
new evidence index are:

- `findings/phase-5j-bluetooth-mtk-android9-triage.md`
- `findings/phase-5j-evidence-index.md`

No Bluetooth enable/start/stop, HCI/AT command, private Binder call, vendor
binary execution, exploit payload, alternate CMDQ ioctl, root, BROM/DA,
remount, or boot-chain operation was performed. The one-shot CMDQ approval is
consumed and does not authorize any of these follow-ups.

### Phase 5K — public kernel source and GhostLock offset applicability

The public IonStack/GhostLock article and pinned public source were reviewed
against the exact device's `Linux 4.4.146+` / MT8183 identity. The CVE
identifier was corrected: GhostLock is `CVE-2026-43499`, not
`CVE-2026-3499`; `CVE-2026-43503` is a separate `sk_buff` issue. The upstream
4.4.146 source snapshot contains the pre-fix `current->pi_blocked_on` pattern,
while later stable source clears `waiter_task->pi_blocked_on` on the proxy path.
That is strong upstream-source evidence, not proof that Amazon's PS7330 binary
is unpatched or exploitable.

The public `auto_extract_offsets` tool was pinned and reviewed. It supports
GKI/Android 6.6 and 6.12 layouts and has no validated KFTRWI/trona/MT8183
4.4.146 profile, so it was not run against the version-mismatched PS7331 boot
image. The public NebuSec GhostLock source likewise contains Pixel/Android 17
GKI target profiles, not this tablet. No exploit, trigger, crash reproducer,
alternate ioctl, BROM/DA action, or boot-chain operation was executed.

The report is `findings/phase-5k-public-kernel-cve-offset-review.md`; evidence
rows `P5K-SRC-001` through `P5K-SAFETY-001` are in
`findings/phase-5-evidence-index.md`. The host-only source path collector is
`tools/scripts/inspect_phase5_exact_source_cve_paths.sh` and supports
`--dry-run`. Exact PS7330 boot/vmlinux acquisition and any exploit execution
remain separate Level 3 operations requiring a new operation-specific report
and approval.

### Phase 5L — source-derived kernel layout calculation

Phase 5L validates the narrower claim that public kernel source can calculate
useful offset information. Using the captured PS7330 arm64 config and a pinned
Linux v4.4.146 `struct rt_mutex_waiter` schema, the host-only calculator derives
the compile-time member layout (`task=0x30`, `lock=0x38`, `prio=0x40`,
`sizeof=0x48`) for the non-debug configuration. It does not calculate
`task_struct.pi_blocked_on`, symbol addresses, KASLR, physical-map addresses,
gadget locations, or an exploit target header.

The report is `findings/phase-5l-source-offset-calculation.md`; the reproducible
tool is `tools/scripts/calculate_phase5_rtmutex_source_layout.py`; the pinned
schema is `tools/configs/phase5/linux-v4.4-rtmutex-waiter-layout.json`; and the
hashed generated output is under
`artifacts/phase5/source-layout-review-20260804-01/`. No device mutation or
kernel exploit execution occurred. Boot/LK extraction and exploit execution
remain separate Level 3 operations.

### Phase 5M — MTK surface and public-source ABI review

Phase 5M adds a read-only MT8183 surface inventory and a host-only static review
of the exact device's pulled ION userspace libraries. The current baseline is
the locked, green-verified-boot `KFTRWI` / `trona` / `PS7330.4104N` Android 9
device with a `4.4.146+` arm64 kernel and `2024-02-01` security patch.

The read-only snapshot lists `/dev/ion` and `/dev/mtk_cmdq`; it does not open
either node. It does not show `/dev/sramrom` or `/dev/geniezone` in the bounded
filtered `/dev` listing. Bluetooth is OFF and reports `Bluetooth Service not
connected`; no HCI traffic or exploit test was run.

The host-only analyzer
`tools/scripts/analyze_phase5m_ion_userspace_static.py` disassembles already
pulled AArch64 libraries with host `objdump`/`nm`/`strings` only. It recovers
the `0xc0104906` ION custom ioctl shape from `libion_mtk.so`, which matches the
public Android `ION_IOC_CUSTOM` UAPI. This is ABI/attack-surface evidence, not
proof of shell access or a vulnerability. Raw shared objects remain local-only;
remote hashes, metadata and derived disassembly are retained.

Phase 5M outputs:

- `findings/phase-5m-mtk-surface-and-candidate-review.md`
- `findings/phase-5m-evidence-index.md`
- `output/tables/phase-5m-mtk-cve-matrix.csv`
- `adb/phase5/PHASE5M-RECON-20260804-01/`
- `adb/phase5/PHASE5M-MTK-SURFACE-20260804-01/`
- `adb/phase5/PHASE5M-BT-SURFACE-20260804-01/`
- `adb/phase5/PHASE5M-MTK-LIBS-20260804-01/` (metadata/hashes public; `.so` inputs local-only)
- `artifacts/phase5/mtk-ion-static-analysis-20260804-03/`

The earlier CMDQ/`mtk-su` route remains excluded for the tested payload/path;
GhostLock/CVE-2026-43499, CVE-2026-43503, SRAMROM/GenieZone and Bluetooth CVEs
remain source/applicability hypotheses only. No new ioctl, kernel trigger,
Bluetooth activation, root, BROM/DA, fastboot, remount, partition operation or
boot-chain action was performed. Any such follow-up needs its own exact
operation-specific Level 3 report and approval.

### Phase 5N — exact Amazon kernel source and GhostLock review

Phase 5N extended the bounded official Fire HD 10 7.3.3.0 source review into
the archive tail and recovered the exact `kernel/locking/rtmutex.c` member. Its
SHA-256 is identical to the pinned Linux stable v4.4.146 snapshot, and the
source retains the pre-fix `remove_waiter()` proxy-path pattern described by
GhostLock/CVE-2026-43499. The exact `futex.c` source contains the PI requeue
and proxy-lock paths, while the captured config has `CONFIG_FUTEX=y` and
`CONFIG_RT_MUTEXES=y`.

This is strong source/config applicability evidence only. It does not prove
the signed PS7330 kernel binary is unpatched, does not calculate runtime
kernel/KASLR offsets, and does not authorize a live exploit. The bounded
source-derived layout remains `task=0x30`, `lock=0x38`, `prio=0x40`, and
`sizeof(struct rt_mutex_waiter)=0x48` for the non-debug AArch64 model.

The exact MT8183 source/config review also confirms ION and MTK_ION build
surfaces, but no ION node was opened and no ioctl or kernel trigger was sent.
GenieZone source is present in the sampled tree, while the MT8183 defconfig
has `CONFIG_MTK_ENABLE_GENIEZONE` unset; source presence is not runtime
reachability.

New outputs:

- `findings/phase-5n-exact-source-ghostlock-review.md`
- `findings/phase-5n-evidence-index.md`
- `artifacts/phase5/exact-kernel-source-review-20260804-02/`
- `tools/scripts/extract_phase5_exact_kernel_members.py`
- `tools/scripts/compare_phase5_exact_rtmutex_source.py`
- `artifacts/phase5/exact-source-layout-review-20260804-01/`

No device mutation, exploit compilation/execution, root, BROM/DA, fastboot,
bootloader, remount, or partition operation was performed in Phase 5N.

### Phase 5O — exact futex/scheduler comparison and public Android implementations

Phase 5O compared the full recovered Amazon `kernel/mediatek/4.4/kernel/futex.c`
and `include/linux/sched.h` members with pinned Linux stable v4.4.146 snapshots.
The exact `futex.c` differs in only three MTK FPSGO timer-hook hunks; no change
was observed in the PI requeue/proxy code. The exact `sched.h` is materially
different because Android/MTK/WALT fields affect `task_struct`; the source line
for `pi_blocked_on` is recorded, but its compiled offset is not inferred from an
upstream-only model. The exact Kconfig uses `CONFIG_FUTEX` selecting
`RT_MUTEXES`; no literal `CONFIG_FUTEX_PI` symbol is present in this old tree,
which is not evidence that PI operations are disabled.

The public Android review found detector-only, generic target-generator, and
device-specific native ports. The closest methodology is a MediaTek Android 12
5.10 port, not a KFTRWI/trona/MT8183 profile. No reviewed public project was
compiled or installed. Public source can calculate source/ABI layout, but it
does not by itself produce a signed-PS7330 runtime exploit target.

Phase 5O outputs:

- `findings/phase-5o-exact-futex-sched-review.md`
- `findings/phase-5o-android-public-poc-review.md`
- `findings/phase-5o-evidence-index.md`
- `artifacts/phase5/exact-futex-sched-review-20260804-04/`
- `artifacts/phase5/android-public-poc-review-20260804-01/`
- `tools/scripts/analyze_phase5_exact_futex_sched.py`

This phase was host-only. No device state changed; no root exploit, kernel
trigger, ioctl, bootloader/BROM/DA, fastboot, remount, or partition operation
was performed.

### Phase 5P — nearest Android old-kernel port and read-only runtime gates

Phase 5P adds a pinned review of the closest public Android implementation,
`NothingFumo/ghostlock-aresin`, at commit
`1895a89c52dc7d7355f14babe5009c2932dcdb6a`. That project targets a POCO F3 GT
(MT6893 / Android 13 / Linux 4.14.186), not this Fire HD 10
(MT8183 / Android 9 / Linux 4.4.146). Its device-specific target profile and
boot/vmlinux workflow are retained as methodology evidence only.

The pinned v4.4.146 and v4.14.186 headers show a common `rt_mutex_waiter`
prefix but a version-specific `deadline` field and size difference. The public
aresin README also contains an internal warning inconsistency about `plist_node`
versus the `rb_node` layout shown by its target header; the pinned headers are
the source of truth for this comparison.

The device gate capture is read-only. It records shell UID 2000, SELinux
enforcing, no effective capabilities, restricted `/proc/kallsyms`/sysctl
visibility, and the existing runtime config. It never opens `/dev/ion` or
`/dev/mtk_cmdq`, triggers futex PI, changes a sysctl, reboots, or writes device
state.

Phase 5P outputs:

- `findings/phase-5p-android-nearby-port-review.md`
- `findings/phase-5p-evidence-index.md`
- `artifacts/phase5/android-nearby-port-review-20260804-01/`
- `adb/phase5/PHASE5P-FUTEX-GATES-20260804-01/`
- `adb/phase5/PHASE5P-RUNTIME-20260804-01/`
- `tools/scripts/capture_phase5p_futex_gates.sh`

GhostLock remains **CVE-2026-43499**; CVE-2026-43503 is an unrelated Linux
networking issue. No Android exploit, APK, native payload, root attempt,
kernel panic trigger, bootloader, fastboot, remount, or partition operation was
performed in Phase 5P. A live device-specific trigger would require a separate
operation-specific Level 3 report and approval.

### Phase 5Q — Android CMDQ implementation and Fire v2/v3 ABI comparison

Phase 5Q records the Android-side implementation of CVE-2020-0069 without
repeating a live ioctl. The official AOSP implementation is a native CTS
`cc_test`/`poc.c`, not a normal APK. Its historical CMDQ v2 request contract
uses the write-address/free/command paths. The recovered exact Fire source
shows that MT8183 selects the v3 dispatcher: the v2 excerpt has the write-
address case, while the v3 dispatcher has no such case and returns
`-ENOIOCTLCMD` for an unknown request. The already archived single request #7
runtime result is raw `-ENOTTY`, which corroborates the ABI mismatch for that
tested request.

This is a source/runtime-scoped diagnosis, not proof that every v3 ioctl is
safe or that the signed PS7330 kernel is free of every CMDQ issue. No PoC was
compiled, installed, or run; no device node was opened in Phase 5Q.

Phase 5Q outputs:

- `findings/phase-5q-android-cmdq-implementation-review.md`
- `findings/phase-5q-evidence-index.md`
- `tools/scripts/analyze_phase5q_android_cmdq_implementation.py`
- `artifacts/phase5/android-cmdq-implementation-review-20260804-01/`

The analyzer is host-only, supports `--dry-run`, refuses to overwrite derived
outputs, and reads only recovered source excerpts plus the prior archived
runtime stdout.

### Phase 5R — current MTK root-route revalidation

Phase 5R rechecked the user-provided KoCleo fork and the MediaTek boot-chain
projects referenced by the supplied HackMD index. The pinned KoCleo
`mtk-su64` Git LFS object has SHA-256
`328632e853ff6427af9f35cb83a91d9e960f35d01188ee66d46ae9c7ce7c7827`;
the repository pointer actually resolves to the same hash as the binary that
was already executed once in `MTK-SU-CMDQ-T03`. Therefore rerunning the fork
would be a duplicate payload test, not a new experiment.

The reviewed `fenrir` and `lkpatcher` projects operate at the MediaTek
secure-boot/LK image layer and do not list `trona/KFTRWI` as an exact target.
The workspace lacks a matching PS7330 LK/recovery set and only contains a
PS7331 version-mismatched boot-chain artifact. No preloader, LK, DA, fastboot
write, or boot-chain exploit was run in Phase 5R.

Phase 5R outputs:

- `findings/phase-5r-mtk-root-route-review.md`
- `findings/phase-5r-evidence-index.md`
- `artifacts/phase5/mtk-easy-su-current-review-20260804-01/`

### Phase 5S — MTK CVE candidate screen

Phase 5S screened newer MediaTek preloader information and GitHub repository
searches for MT8183-related candidates. The November 2025 MediaTek bulletin's
`CVE-2025-20730` affected-chipset list does not include MT8183, and the public
advisory requires high privileges. Searches for public repositories matching
`CVE-2021-0904`, `CVE-2021-0676`, `CVE-2022-21767 Android`, and `MT8183 exploit`
returned no repository results in the recorded query scope.

This is a candidate screen, not proof that the signed PS7330 build is free of
all vulnerabilities. No new kernel trigger, Bluetooth/HCI input, device-node
ioctl, preloader/LK operation, BROM/DA operation, or partition write was
performed.

Phase 5S outputs:

- `findings/phase-5s-mtk-cve-candidate-screen.md`
- `findings/phase-5s-evidence-index.md`

### Phase 5T — PS7330 OTA/boot metadata capture

Phase 5T adds a new serial-gated, read-only collector for OTA and boot-chain
metadata. It confirms `trona_fireos_ship_7330`, PS7330/4104, the MediaTek branch,
and the Android-exported preloader/LK descriptors. Shell cannot list `/cache`,
`/data/ota`, or `/data/ota_package`, and no exact PS7330 payload was exposed;
the collector did not attempt a block-device read or update operation.

Phase 5T outputs:

- `tools/scripts/capture_phase5t_ota_metadata.sh`
- `adb/phase5/PHASE5T-OTA-METADATA-20260804-01/`
- `findings/phase-5t-ota-metadata-review.md`
- `findings/phase-5t-evidence-index.md`

### Phase 5U — Android CVE applicability and GhostLock Level 3 boundary

Phase 5U records a host-only comparison of the official GhostLock fix with the
Fire 4.4 source and a defconfig gate for CVE-2026-43503. The Fire source/config
family is a source-level GhostLock candidate, but no signed-kernel layout or
exact Android payload is available. The documented packet-duplication/nft path
for CVE-2026-43503 is unset in the captured MT8183 defconfig. No exploit or
kernel trigger was executed.

Phase 5U outputs:

- `tools/scripts/analyze_phase5u_cve_surfaces.py`
- `artifacts/phase5/cve-2026-43499-43503-review-20260804-02/`
- `findings/phase-5u-android-cve-applicability.md`
- `findings/phase-5u-ghostlock-level3-report.md`
- `findings/phase-5u-evidence-index.md`

### Phase 5V — MT8183/Android 9 Bluetooth CVE and implementation review

Phase 5V reviews the exact PS7330 `com.android.bluetooth` APK/ODEX/VDEX and
Amazon GATT extension against the official MediaTek and Android February 2022
bulletins. The published scope includes MT8183/Android 9 for Bluetooth
CVE-2022-20025 through CVE-2022-20028 and related 20041–20046 issues. The
device is now on the 2024-02-01 patch level, so a patched exact binary is a
high-confidence inference but not a binary-level confirmation because the
Amazon vendor patch mapping is not public in the preserved artifacts.

The recorded GitHub search found no exact Android repository for the four
searched CVEs and no `KFTRWI/trona/PS7330` implementation. The exact runtime
snapshot had Bluetooth disabled and the service disconnected. No Bluetooth
activation, HCI/AT input, private Binder call, vendor binary, exploit, kernel,
boot-chain or partition operation was performed.

Phase 5V outputs:

- `tools/scripts/analyze_phase5v_bluetooth_cves.py`
- `artifacts/phase5/bluetooth-cve-screen-20260804-01/`
- `findings/phase-5v-bluetooth-cve-review.md`
- `findings/phase-5v-bluetooth-evidence-index.md`
- `findings/phase-5v-bluetooth-level3-report.md`
- `output/tables/phase5v-bluetooth-cve-matrix.csv`

### Phase 5W — Android implementation and preloader applicability review

Phase 5W maps the public Android implementation boundary for the current CVE
families. GhostLock is a Linux futex/rtmutex issue reached through a native
syscall; CVE-2022-20053/20054 split between the AOSP IMS binding contract and
MediaTek's vendor IMS/ATCI layer; CVE-2022-20055/20056 are preloader USB issues
before Android userspace; and the CMDQ/ION cases are Android native ABI to
vendor-driver paths. The mapping does not turn any public Android test or
adjacent boot image into a Fire HD 10 root payload.

The only boot-chain files available locally are PS7331 images and are marked
`VERSION_MISMATCH` against the installed PS7330. Their host-only strings show
authentication, anti-rollback, USB download and Amazon unlock-related markers,
but no live preloader/BROM/DA interaction was performed. The existing IMS/ATCI
snapshot remains the boundary: no property write, daemon start, socket use or
AT command was attempted.

Phase 5W outputs:

- `tools/scripts/analyze_phase5w_android_implementations.py`
- `artifacts/phase5/android-implementation-preloader-review-20260804-02/`
- `findings/phase-5w-android-implementation-review.md`
- `findings/phase-5w-evidence-index.md`
- `findings/phase-5w-preloader-level3-report.md`
- `output/tables/phase5w-android-implementation-matrix.csv`

No device state changed. No exploit, native trigger, malformed ioctl,
Bluetooth/HCI input, IMS/ATCI command, preloader/BROM/DA handshake, fastboot,
remount, reboot, image write or partition operation was performed in Phase 5W.

### Phase 5X — Android implementation and MTK route-surface recheck

Phase 5X adds a new read-only exact-device capture and a host-only compatibility
matrix for the Android implementation boundaries raised by the current CVE
discussion. The capture confirms the device remains `KFTRWI/trona`, MT8183,
Android 9/API 28, PS7330.4104N, shell UID 2000, and HOME
`com.amazon.firelauncher/.Launcher` at priority 50.

The new runtime surface review observes kernel AEE worker threads but no
userspace AEE process/package/service/init endpoint; `/dev/sspm` is recorded only
as metadata and is never opened; and the Android 9 runtime has no observed APEX
property, APEX directories/packages, or `apexservice`. This does not prove the
inaccessible binaries are absent or patched; it establishes that none of these
routes is a shell-reachable, exact-device root path in the captured normal
runtime.

The public review also pins the current KoCleo `mtk-easy-su` and LauncherHijack
heads. Neither provides a new exact PS7330 implementation. LauncherHijack's
documented default-launcher corruption route remains explicitly risk-rejected.
`CVE-2025-20765` is retained as an MT8183/AEE external-scope candidate, not as an
executable root claim. GhostLock remains `CVE-2026-43499`; `CVE-2026-43503` is a
separate networking issue, and `CVE-2026-3499` is not used as a GhostLock alias.

Phase 5X outputs:

- `tools/scripts/capture_phase5x_route_surface.sh`
- `tools/scripts/analyze_phase5x_public_routes.py`
- `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-03/`
- `artifacts/phase5/public-route-review-20260804-01/`
- `findings/phase-5x-android-implementation-and-route-review.md`
- `findings/phase-5x-evidence-index.md`
- `output/tables/phase5x-candidate-matrix.csv`

No package, setting, HOME, process, node, partition, bootloader or firmware
state changed in Phase 5X. No AEE/ATF/APEX/futex/network trigger, exploit,
root payload, BROM/DA, fastboot, remount, reboot or partition operation was
performed.

### Phase 5Y — AEE device-node follow-up

An earlier read-only `/dev` snapshot contained `aed0` and `aed1`, so Phase 5Y
corrects the scope of the Phase 5X AEE statement. The exact PS7330 runtime has
`/dev/aed0` and `/dev/aed1` with `root:root` mode `0600` and SELinux type
`aed_device`, plus root-only `/dev/atf_log`. Shell `test -r` and `test -w`
returned zero for all three nodes. No node was opened; no AEE daemon, package,
service, or init endpoint was observed.

Phase 5Y outputs:

- `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06/`
- `findings/phase-5y-aee-device-node-followup.md`
- `findings/phase-5y-evidence-index.md`
- `output/tables/phase5x-aee-node-matrix.csv`
- `artifacts/phase5/public-route-review-20260804-03/`

The finding narrows the AEE route to a root-only vendor device interface; it
does not create a shell-readable root primitive. AEE `open`/`read`/`write`/
`ioctl`, crash/race triggering, permission changes, SELinux changes, boot-chain
operations and partition writes remain out of scope.

### Phase 5Z — Android AEE implementation map

Phase 5Z documents the Android-side implementation rather than treating a
public kernel PoC as a Fire root method. Public MediaTek Android source shows
that `aed0` and `aed1` are kernel misc devices with `read`/`write`/`ioctl`
operations, `/proc/aed` reporting, and an `aed_init()` registration path. MTK
SELinux references show that the userspace reader is normally a privileged
`aee_aed`/`aee_aedv`-style daemon/domain. The exact Fire PS7330 runtime has the
same AEE device surface, but the nodes are `root:root 0600`, SELinux-labeled
`aed_device`, and shell read/write checks are both zero. No node was opened and
no AEE daemon or crash trigger was executed.

The GhostLock Android boundary is separate: native/Bionic futex PI reaches the
Linux futex/rtmutex path. The cited public report says Android-specific
exploitation is future work; the captured public AArch64 target tree contains
other Google build profiles, not `KFTRWI/trona/MT8183/PS7330`.

Phase 5Z outputs:

- `tools/scripts/inspect_phase5y_exact_source_aee_paths.sh`
- `tools/scripts/analyze_phase5z_android_aee.py`
- `artifacts/phase5/exact-source-aee-paths-20260804-01/`
- `artifacts/phase5/android-aee-implementation-review-20260804-04/`
- `findings/phase-5z-android-aee-implementation-review.md`
- `findings/phase-5z-evidence-index.md`
- `output/tables/phase5z-android-aee-implementation.csv`
- `output/call-graphs/phase5z-android-aee-flow.mmd`

The AEE node ABI, daemon-domain integration and exact Fire shell boundary are
now separated. Exact daemon binary/patch status and complete source-member
inventory remain unresolved. Node open/read/write/ioctl, malformed AEE input,
race/crash, root payload, BROM/DA, fastboot, remount and partition operations
remain explicitly rejected.

### Phase 5AA — Public Android implementation recheck

Phase 5AA records the Android-side implementation of the public routes discussed
after Phase 5Z. `mtk-easy-su` is confirmed as a Kotlin wrapper around Git-LFS
precompiled MTK/Magisk assets; its pinned `mtk-su64` is the same payload already
tested and failed on the exact PS7330 build. The public GhostLock Android ports
are target-specific native implementations: `popsicle` targets Snapdragon/
Android 16/6.12.23, while `aristotle` targets MediaTek/XIG04/Android 12/5.10.136
and explicitly says it was not hardware-validated. The Android detector and
Pixel Dirty Pipe projects are not portable root methods, and their own warnings
make installation or triggering inappropriate for this device.

The review also separates Qualcomm/Xiaomi service candidates from MTK, and
preloader/secure-boot projects from Android userspace. No external APK, native
payload, exploit, BROM/DA, device node, boot image, preloader, fastboot or
partition operation was performed.

Phase 5AA outputs:

- `tools/scripts/analyze_phase5aa_android_implementations.py`
- `artifacts/phase5/android-implementation-public-review-20260804-01/`
- `findings/phase-5aa-android-implementation-review.md`
- `findings/phase-5aa-evidence-index.md`
- `output/tables/phase5aa-android-implementation-matrix.csv`

The only remaining safe research value is offline comparison against a
verifiable exact PS7330 signed kernel/boot artifact. Without that artifact,
there is no evidence for a new exact Android root implementation or a safe
payload adaptation; no equivalent public payload should be rerun.

### Phase 5AB — Android PendingIntent implementation review

Phase 5AB adds the Android implementation detail that was missing from the
earlier foreground-redirect comparison. The fixed LauncherHijack source uses
an Accessibility/event observer and then constructs an explicit
ACTION_MAIN + CATEGORY_LAUNCHER intent. Its HomePress implementation dispatches
that intent through the public Android 9-compatible
PendingIntent.getActivity(...).send() API. This is a foreground redirect, not
a HOME resolver mutation and not a privileged PackageManager operation.

The local Phase 4 redirect harness now has a separate source-level
PendingIntent variant. It retains the manual Accessibility consent, visible
toggle, Fire-package filter, cooldown, loop guard and explicit research target;
it deliberately has no overlay, device-admin, network permission or private
Binder call. The historical T03 APK and its 0/30 direct-start result remain
preserved and are not overwritten.

Phase 5AB outputs:

- tools/scripts/analyze_phase5ab_android_implementation.py
- tools/phase4-accessibility/src/org/fireosresearch/phase4/redirect/LauncherRedirectService.java
- findings/phase-5ab-launcherhijack-pendingintent-review.md
- findings/phase-5ab-evidence-index.md
- artifacts/phase5/launcherhijack-pendingintent-review-20260804-01/
- output/tables/phase5ab-android-implementation-matrix.csv

The source variant passed static token validation and dry-run checks. It was
later compiled with the host's OpenJDK 17 and installed only as a preparation
run in Phase 5AC; Accessibility was not enabled. The direct measurement is
still pending manual consent. No root payload, ioctl, reboot, fastboot or
partition operation was performed.

The result is therefore: LauncherHijack's Android implementation is confirmed
as a public event-observation plus explicit-Activity/PendingIntent technique;
the new local PendingIntent variant is a 待驗證 approximation, and there is
still no evidence of a true, persistent, no-Root HOME replacement or a new
exact PS7330 Android root implementation.

### Phase 5AC — MTKClient compatibility and safe Android preparation

Phase 5AC fixed the current public mtkclient revision and reviewed its
MediaTek BROM configuration offline. MT8183 appears in a shared
MT6771/MT8385/MT8183/MT8666 profile with dacode 0x6771; there is no independent
0x8183 key in the inspected source. This is a source-level compatibility lead,
not proof that Amazon's trona preloader, DA, SLA/DAA, SBC, rollback or seccfg
chain is supported.

The phase also built the PendingIntent variant with OpenJDK 17, verified the
APK signature, captured a complete before snapshot, and installed only the
two research APKs. The Accessibility service list remained empty and the HOME
resolver remained com.amazon.firelauncher/.Launcher. The researcher must
manually enable the service in Settings before measurement; ADB never writes
the Accessibility setting.

Phase 5AC outputs:

- tools/scripts/analyze_phase5ac_mtkclient_compat.py
- artifacts/phase5/mtkclient-android-route-review-20260804-01/
- findings/phase-5ac-mtkclient-and-android-route-review.md
- findings/phase-5ac-evidence-index.md
- output/tables/phase5ac-mtkclient-android-route-matrix.csv
- adb/phase5/PHASE5AB-PENDINGINTENT-T01/

No mtkclient BROM/payload/crash/preloader/DA/seccfg/read/write/erase command,
kernel trigger, ioctl, fastboot, boot image, partition or bootloader write
was performed. The exact mtk-su payload was not rerun.

### Phase 5AD — Historical mtk-su target screen

Phase 5AD rechecked historical Fire rooting material against the exact device.
The public tutorial demonstrates Fire HD 10 2017 / Fire OS 5.6.4.0 and marks
Fire HD 10 2019 / Fire OS 7.3.1.0 as untested; it does not provide a 2021
KFTRWI/PS7330 target. The fixed KoCleo payload has already failed at exact
PS7330 step 3, so historical instructions are not rerun.

Phase 5AD outputs:

- artifacts/phase5/public-target-screen-20260804-01/
- findings/phase-5ad-historical-mtk-su-target-screen.md
- findings/phase-5ad-evidence-index.md

No new payload, BROM, DA, device-node, fastboot or partition operation was
performed.

### Phase 5AE — Android KEYCODE_HOME/PendingIntent implementation

Phase 5AE adds a second Android implementation boundary to the local harness:
after the researcher manually enables Accessibility and the visible toggle,
`AccessibilityService.onKeyEvent()` handles only `KEYCODE_HOME` and dispatches
an explicit research Activity through `PendingIntent.getActivity().send()`.
The service requests the public `FLAG_REQUEST_FILTER_KEY_EVENTS` capability and
returns `false` when the toggle is off or the target cannot be dispatched, so
the normal HOME path remains available. It does not read window text, write
settings, modify Fire Launcher, or use overlay/private Binder/root APIs.

Phase 5AE preparation installed the newly built redirect APK and alias APK,
but intentionally did not enable Accessibility. The key-event measurement is
therefore still 待驗證 and must not be described as a working workaround until
manual consent and a separately identified measurement produce evidence.

Phase 5AE outputs:

- findings/phase-5ae-keyevent-pendingintent-review.md
- output/tables/phase5ae-android-keyevent-matrix.csv
- output/tables/phase5ae-android-keyevent-evidence.csv
- artifacts/phase5/android-keyevent-implementation-review-20260804-01/
- adb/phase5/PHASE5AE-KEYEVENT-PENDINGINTENT-T01/

The APK was built locally with OpenJDK 17, Android platform API 35 and Build
Tools 35.0.0; its v3 signature and SHA-256 are recorded in the report. The
service is never enabled by ADB. No root payload, kernel trigger, ioctl,
reboot, fastboot or partition operation was performed.

### Phase 5AE follow-up — exact-target public-source recheck

The current `KoCleo/mtk-easy-su` `master` still resolves to
`8c6871ac7c15b8e98a47e25c35ab93b87e260475`, the same revision already audited
and tested unsuccessfully on the exact PS7330 device. No new
KFTRWI/trona/MT8183 payload or profile was found. The supplied HackMD examples
are Qualcomm/Xiaomi-specific, while GhostLock is a target-specific kernel
futex/rtmutex implementation and DirtyClone is a separate Linux networking
bug; neither has an exact PS7330 Android implementation in the reviewed
sources.

Phase 5AE follow-up outputs:

- findings/phase-5ae-followup-public-target-review.md
- output/tables/phase5ae-public-target-matrix.csv
- artifacts/phase5/public-target-followup-20260804-01/

No third-party APK/native payload, BROM/DA operation, boot image, partition
write, or kernel trigger was executed.

The same follow-up reviewed the fixed public `Mujeebb/mtkclient-1` revision
`b30d65c706fdda93dcb44674aeb0ff796b27b2bc`. Its README documents broad MTK
BROM/DA boot/vbmeta write and `seccfg unlock` workflows, but no exact
KFTRWI/trona/PS7330 profile. Those routes remain rejected without matching
preloader/DA/recovery/rollback evidence.

- artifacts/phase5/public-mtkclient-followup-20260804-01/

### Phase 5AF — Android CVE implementation and public PoC exact-target review

Phase 5AF separated the user-supplied CVE identifiers and mapped the public
implementations to Android layers. `CVE-2026-3499` is a WordPress CSRF record,
not GhostLock. GhostLock (`CVE-2026-43499`) is a native futex/rtmutex kernel
path; DirtyClone (`CVE-2026-43503`) is a separate Linux `net/skbuff` /
XFRM/ESP path. Public Android GhostLock projects are device/build-specific,
and public DirtyClone repositories are Linux C research reproducers; none has
an exact KFTRWI/trona/MT8183/PS7330 profile.

The new read-only capture found no visible user-namespace sysctl, no
`xt_TEE`/ESP/XFRM module surface, and no `/proc/net/xfrm_stat` endpoint. The
captured exact MT8183 defconfig also lacks the principal DirtyClone
duplicate/TEE options. `/dev/ion` metadata is visible to shell, but no ION node
was opened and no ioctl was called. AEE/ATF/SPM nodes remain shell-inaccessible.

Phase 5AF outputs:

- tools/scripts/capture_phase5af_android_cve_surface.sh
- adb/phase5/PHASE5AF-ANDROID-CVE-SURFACE-20260804-02/
- findings/phase-5af-android-cve-and-poc-review.md
- findings/phase-5af-evidence-index.md
- output/tables/phase5af-android-cve-poc-matrix.csv
- artifacts/phase5/android-cve-poc-review-20260804-01/

No third-party exploit code was downloaded, compiled, installed or executed.
No device node, block device, kernel trigger, root payload, BROM/DA, fastboot,
boot image or partition operation was performed.

### Phase 5AG — Android implementation and MT8183/PS7330 public-source follow-up

Phase 5AG reviewed the fixed LauncherHijack Android implementation and separated
foreground redirect from formal HOME resolver replacement. The source uses
Accessibility/event observation, an explicit `ACTION_MAIN` plus
`CATEGORY_LAUNCHER` component, and `PendingIntent.getActivity().send()`; it does
not write the HOME resolver. Its historical default-launcher corruption route
was not tested because the public documentation warns of per-user recovery risk.

The phase also rechecked the supplied CVE identifiers and official MediaTek
bulletin scope against the exact `KFTRWI/trona/MT8183/PS7330.4104N` device. No
reviewed public implementation matches Android 9, this build, and a shell-to-root
entry. No third-party payload was downloaded or executed, and no device state was
changed.

Phase 5AG outputs:

- `findings/phase-5ag-launcherhijack-and-mtk-bulletin-followup.md`
- `findings/phase-5ag-evidence-index.md`
- `output/tables/phase5ag-mtk-bulletin-matrix.csv`
- `output/tables/phase5ag-android-implementation-matrix.csv`
- `artifacts/phase5/launcherhijack-and-mtk-bulletin-followup-20260804-01/source-manifest.csv`
- `tools/scripts/validate_phase5ag_review.py`

### Phase 5AH — HackMD/MTK route and exact KFTRWI public-target recheck

Phase 5AH rechecked the supplied HackMD list, the pinned `mtk-easy-su` and
`mtkclient` sources, and public searches for `KFTRWI/trona/MT8183/PS7330`.
The HackMD entries are Qualcomm/Xiaomi-specific and do not provide an Amazon
MTK implementation. No verified exact PS7330 root, bootloader-unlock, or
custom-ROM implementation was found in the reviewed public sources. Existing
`mtk-easy-su` runtime evidence remains a no-confirmed-root result.

Phase 5AH outputs:

- `findings/phase-5ah-public-target-recheck.md`
- `findings/phase-5ah-evidence-index.md`
- `output/tables/phase5ah-public-route-matrix.csv`
- `adb/phase5/PHASE5AH-DEVICE-READONLY-20260804-01/`
- `artifacts/phase5/public-target-recheck-20260804-01/source-manifest.csv`
- `tools/scripts/capture_phase5ah_device_readonly.sh`
- `tools/scripts/validate_phase5ah_public_routes.py`

No Qualcomm command, unknown APK/native payload, BROM/DA handshake, fastboot
write, bootloader unlock, partition write, or destructive device operation was
performed in this phase.

### Phase 5AI — PS7330 exact boot/preloader artifact search

Phase 5AI checked whether a complete, verifiable `PS7330.4104N` boot/preloader/
DA/recovery set is available. The workspace still contains only the adjacent
PS7331 full OTA; the Amazon public update page currently exposes the 11th-gen
Fire OS 7.3.3.1 update row but no PS7330 filename in the reviewed page. The
PS7331 images remain `VERSION_MISMATCH` and were not used as recovery or live
inputs.

Phase 5AI outputs:

- `findings/phase-5ai-exact-ps7330-artifact-search.md`
- `findings/phase-5ai-evidence-index.md`
- `output/tables/phase5ai-artifact-search.csv`
- `artifacts/phase5/exact-ps7330-artifact-search-20260804-01/source-manifest.csv`
- `tools/scripts/validate_phase5ai_artifact_search.py`

No OTA sideload, BROM/DA handshake, fastboot write, bootloader unlock, seccfg
operation, partition write, or unknown payload execution was performed.

### Phase 5AJ — MT8183/Android 9 CVE and public Android implementation review

Phase 5AJ maps the user-supplied CVEs to their real Android/Linux layers and
keeps exact-target evidence separate from public affected-scope records.
`CVE-2026-3499` is a WordPress CSRF record, GhostLock is
`CVE-2026-43499` in Linux futex/rtmutex, and `CVE-2026-43503` is a separate
Linux skb/XFRM/ESP path. The exact MT8183 defconfig lacks the documented
DirtyClone packet-duplication/TEE entry symbols. MediaTek Bluetooth
`CVE-2022-20025..20028` and `CVE-2022-21767..21768` have historical MT8183/
Android 9 scope, but the exact PS7330 vendor vulnerable/fixed binary mapping is
not public.

The Android implementation review confirms the AOSP `GattService` Binder,
permission and JNI boundary, and the exact Fire `FosGattService`,
`FosBluetoothGattBinder` and `AmazonBtPolicyManagerAdapter` extension. It does
not establish a shell-to-root primitive. Bounded public-source searches found
no exact `KFTRWI/trona/MT8183/PS7330` Android root implementation. No exploit,
Bluetooth activation, crafted input, kernel trigger, device-node operation,
BROM/DA, fastboot or partition operation was performed.

Phase 5AJ outputs:

- `findings/phase-5aj-mtk-android9-cve-poc-review.md`
- `findings/phase-5aj-evidence-index.md`
- `output/tables/phase5aj-cve-poc-matrix.csv`
- `output/call-graphs/phase5aj-android-cve-implementation.mmd`
- `artifacts/phase5/phase5aj-mtk-android9-cve-poc-review-20260804-01/`
- `tools/scripts/validate_phase5aj_cve_poc_review.py`

The validator is host-only and supports `--dry-run`; it never connects to the
device, downloads source, compiles a payload or executes a binary.

### Phase 5AK — Android implementation state and safe redirect boundary

Phase 5AK captured the current installed Android redirect artifacts and device state
without changing Settings or package state. The APK implementation is limited to a
manually enabled `AccessibilityService`: it can observe `KEYCODE_HOME` and Fire
Launcher window-state events, then send an explicit research `CATEGORY_LAUNCHER`
activity through `PendingIntent`. It does not call the HOME resolver, write a
preferred activity, or mutate Fire Launcher. The capture found Accessibility
`services:{}` and HOME still resolving to `com.amazon.firelauncher/.Launcher` at
effective priority 50, so no redirect success rate is claimed.

The Android/CVE review also keeps GhostLock (`CVE-2026-43499`) at the native
syscall/kernel boundary and DirtyClone (`CVE-2026-43503`) at its separate Linux
networking boundary. No third-party root/CVE source or binary was downloaded,
compiled, installed, or executed.

Phase 5AK outputs:

- `tools/scripts/capture_phase5ak_android_implementation_state.sh`
- `findings/phase-5ak-android-implementation-and-state-review.md`
- `findings/phase-5ak-evidence-index.md`
- `output/tables/phase5ak-android-implementation-matrix.csv`
- `output/call-graphs/phase5ak-android-implementation.mmd`
- `adb/phase5/PHASE5AK-ANDROID-IMPLEMENTATION-STATE-20260804-01/`
- `artifacts/phase5/phase5ak-android-implementation-review-20260804-01/`

The next measurement requires the researcher to enable the service in Android
Settings and turn on the visible app toggle. The shell collector intentionally
does not automate that consent.

### Phase 5AL — MTK Android 9 exact-device CVE surface triage

Phase 5AL compared official MediaTek bulletin scope with a fresh, read-only
capture from the exact `KFTRWI/trona/MT8183/PS7330.4104N` device. The closest
public candidates are `CVE-2022-20053/20054` (IMS/AT), but no IMS package,
IMS service, CCCI/modem/AT node, or matching daemon was observed; only the
basic `IMms` and `telephony.registry` services were present. `CVE-2022-20067`
has MT8183/Android 9 scope but requires system execution privileges. Preloader
rows were rejected as Android-version/boot-chain inputs, and Wi-Fi rows were
not root-impact vulnerabilities.

Phase 5AL outputs:

- `tools/scripts/capture_phase5al_mtk_cve_surface.sh`
- `findings/phase-5al-mtk-cve-surface-review.md`
- `findings/phase-5al-evidence-index.md`
- `output/tables/phase5al-mtk-cve-surface-matrix.csv`
- `output/call-graphs/phase5al-mtk-cve-surface.mmd`
- `adb/phase5/PHASE5AL-MTK-CVE-SURFACE-20260804-02/`
- `artifacts/phase5/phase5al-mtk-cve-surface-review-20260804-01/`

The collector supports `--dry-run` and does not open a device node, call
ioctl, send AT/modem traffic, trigger a kernel race, reboot, or write any
partition.

### Phase 5AM — Android Bluetooth implementation boundary and CVE index correction

Phase 5AM adds a host-only parser over the exact Bluetooth VDEX focus artifacts. It
records the Android `GattService` Binder/permission boundary, Amazon
`FosGattService` and extended binder, and the private native
`AmazonBtPolicyManagerAdapter` BTPM boundary. It also explicitly distinguishes DEX
method-pool indices such as `#20025` from CVE identifiers such as
`CVE-2022-20025`; the former are not evidence of the latter.

Phase 5AM outputs:

- `tools/scripts/analyze_phase5am_bluetooth_boundaries.py`
- `findings/phase-5am-bluetooth-implementation-boundary.md`
- `findings/phase-5am-evidence-index.md`
- `output/tables/phase5am-bluetooth-boundaries.csv`
- `output/call-graphs/phase5am-bluetooth-implementation.mmd`
- `artifacts/phase5/phase5am-bluetooth-implementation-20260804-02/`

The analyzer is host-only, supports `--dry-run`, refuses to overwrite an existing
output, and performs no device I/O, Binder invocation, native-library loading,
Bluetooth activation, crafted input, kernel trigger, or root operation. GhostLock
remains a separate Linux futex/PI-rtmutex kernel path; the Bluetooth Android map
does not establish a relation to that kernel CVE or a shell-to-root primitive.

### Phase 5AN — GhostLock exact target gate and boot metadata

Phase 5AN preserves a new read-only exact-device capture and separates source-level
applicability from executable exploit compatibility. The Fire HD 10 is
`KFTRWI/trona/MT8183`, running the signed `PS7330.4104N` build and Linux
`4.4.146+`. The matching Amazon kernel source retains the old futex PI/rtmutex
`remove_waiter()` pattern, and the live read-only config exposes `FUTEX`,
`RT_MUTEXES`, and `PREEMPT`; this is a source/config candidate, not proof of a
runtime root path.

The shell-visible boot symlink resolves to `mmcblk0p16`, but an exact boot pull is
denied with `Permission denied`. The only locally available boot image is a
PS7331 image and is explicitly marked `VERSION_MISMATCH`; it is not used as an
exploit, recovery, or flashing input. Public GhostLock target headers reviewed in
the pinned source snapshot target Pixel/Android 17 builds, not this Amazon device.

No futex race, reproducer, root/ROP stage, kernel memory write, BROM/DA action,
bootloader operation, partition read/write, or device-state mutation was performed.

Phase 5AN outputs:

- `tools/scripts/capture_phase5an_boot_metadata.sh`
- `findings/phase-5an-ghostlock-exact-target-review.md`
- `findings/phase-5an-evidence-index.md`
- `output/call-graphs/phase5an-ghostlock-source-to-target.mmd`
- `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/`

The collector requires an explicit serial, refuses an existing output directory,
supports `--dry-run`, records command results and SHA-256 values, and only attempts
the optional read-only boot pull to document the permission boundary.

### Phase 5AO — PS7331 boot image and GhostLock offset capability

Phase 5AO parsed the locally preserved PS7331 `boot.img` entirely on the host. The
image is a `trona`/MT8183 Android boot image with a 2048-byte page, kernel field
offset `0x800`, gzip-compressed ARM64 Linux `4.4.146+`, a 2025-05-03 kernel banner,
and embedded MT8183/Amazon build strings. It is useful for offline provenance and
partial symbol inspection, but it is not the installed PS7330 kernel.

The review distinguishes image offsets and selected symbol markers from C type
layout, runtime KASLR/physmap addresses, and exploit gadget/credential targets.
The public GhostLock fix is later than this build, so an unbackported old source
pattern is plausible; Amazon backports cannot be ruled out without exact PS7331
source or comparable patch evidence.

Phase 5AO outputs:

- `tools/scripts/inspect_android_boot_image.py`
- `findings/phase-5ao-ps7331-boot-analysis.md`
- `findings/phase-5ao-evidence-index.md`
- `output/tables/phase5ao-offset-capability.csv`
- `output/call-graphs/phase5ao-boot-to-offsets.mmd`
- `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/boot-image-metadata.json`

No PS7331 image was flashed, no partition was written, and no GhostLock race or
root payload was run.

### Phase 5AP — PS7330 kernel symbol visibility

Phase 5AP performed a new read-only exact-device capture. The ADB shell can read
the kernel version and module list, but `/proc/kallsyms` and
`/proc/sys/kernel/kptr_restrict` return `Permission denied`; `perf_event_paranoid`
is readable as `3`. This confirms that the current shell path cannot obtain a live
PS7330 symbol-address profile. No procfs bypass, pointer leak, futex race, ioctl,
root payload, reboot, or partition operation was attempted.

Phase 5AP outputs:

- `tools/scripts/capture_phase5ap_kernel_symbol_surface.sh`
- `findings/phase-5ap-kernel-symbol-surface.md`
- `findings/phase-5ap-evidence-index.md`
- `output/tables/phase5ap-kernel-symbol-surface.csv`
- `adb/phase5/PHASE5AP-KERNEL-SYMBOL-20260804-01/`

### Phase 5AQ — PS7331/PS7330 embedded kernel-config comparison

Phase 5AQ extracted the embedded IKCONFIG from the PS7331 ARM64 Image and
captured the exact PS7330 `/proc/config.gz` with a corrected `adb exec-out`
command. Across 3,705 keys, only three differences were found, all unrelated
to GhostLock: netfilter accounting, conntrack timestamps, and MTK WPA3 support.
The futex/rtmutex, preemption, ARM64 VA39, KALLSYMS, KASLR, SELinux, seccomp and
other focus gates are identical. This confirms a common config family, but does
not prove that the PS7331 `rtmutex.c` code was not privately backported.

Phase 5AQ outputs:

- `tools/scripts/extract_embedded_kernel_config.py`
- `tools/scripts/capture_phase5aq_device_config.sh`
- `tools/scripts/compare_kernel_configs.py`
- `findings/phase-5aq-ps7331-ps7330-config-comparison.md`
- `findings/phase-5aq-evidence-index.md`
- `output/tables/phase5aq-config-diff.csv`
- `output/call-graphs/phase5aq-config-to-ghostlock.mmd`
- `adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02/`

### Phase 5AR — PS7331 compiled `rtmutex` review

Phase 5AR extends the earlier PS7331 boot-image/config review with a host-only,
address-sanitized inspection of the reconstructed PS7331 ARM64 kernel Image.
The recovered symbol table contains `remove_waiter` and the proxy-lock symbols;
the inspected `remove_waiter` path reads the AArch64 current-task source and
clears the blocked-on field through that task, while the proxy error path calls
`remove_waiter`. This is direct compiled evidence for the old GhostLock
root-cause pattern in the inspected function path. It is not evidence of a
working root exploit and does not establish the same compiled result for the
installed PS7330 image.

The exact current-device PS7330 source remains the 7.3.3.0 Amazon archive listed
in Phase 5N. The supplied source-notice backup page confirms that archive for the
11th-generation device but does not list an 11th-generation 7.3.3.1 source
archive in its 2025-02-26 snapshot. Software-version availability and source-
notice availability are kept separate.

Phase 5AR/5AS outputs:

- `tools/scripts/analyze_phase5ar_ps7331_rtmutex_binary.py`
- `findings/phase-5ar-ps7331-compiled-rtmutex-review.md`
- `findings/phase-5as-source-notice-archive-review.md`
- `findings/phase-5ar-evidence-index.md`
- `output/tables/phase5ar-rtmutex-binary-evidence.csv`
- `output/call-graphs/phase5ar-rtmutex-flow.mmd`
- `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/`
- `artifacts/phase5/technically-competent-source-notice-review-20260804-01/`

The analyzer supports `--dry-run`, refuses to overwrite an existing output,
uses only host `nm`/`objdump`, and omits absolute addresses, branch targets,
gadget data and exploit offsets. No device state changed; no futex race, native
payload, ioctl, bootloader action, partition operation or image write was run.

### Phase 5AT — PS7330 exact artifact follow-up

Phase 5AT followed the exact `PS7330.4104N` artifact gap through the official
Amazon update endpoint and public firmware metadata. The current official 11th-
generation entry redirects to the adjacent `PS7331.4463N` OTA. The public 11th-
generation firmware history reviewed here lists PS7331, PS7329 and earlier
builds, but no PS7330 record. The source-notice archive still provides the exact
7.3.3.0 source family used by Phase 5N; source availability is not the same as
a signed boot/Image or boot-chain recovery set.

Phase 5AT does not claim that PS7330 never existed publicly. It records a
bounded, reproducible search result and keeps the exact signed-binary question
open. No partial OTA response was treated as an artifact, and no device state
changed.

Phase 5AT outputs:

- `findings/phase-5at-ps7330-artifact-followup.md`
- `findings/phase-5at-evidence-index.md`
- `artifacts/phase5/ps7330-artifact-followup-20260804-01/metadata.md`

### Phase 5AU — PS7330 OTA residue and update-service read-only review

Phase 5AU captured the exact PS7330.4104N runtime and inspected OTA package,
settings, service, storage-path and bounded file-search surfaces without
triggering an update. The shell-visible shared Download directory had no OTA
bin/zip; private cache and OTA data paths were permission denied. The OTA debug
dashboard requires the Amazon privileged permission
com.amazon.dcp.permission.DISPLAY_DEBUG_UI and was not bypassed.

The existing OTA APK was reviewed offline with JADX 1.5.6. Its data model has
PublishedUpdates.RemoteURI and PendingUpdates.LocalURI, but the live app
database is private and was not read through a permission bypass. No exact
PS7330 download URL or pending URI was recovered.

Phase 5AU outputs:

- `tools/scripts/capture_phase5au_ota_residue.sh`
- `findings/phase-5au-ota-residue-review.md`
- `findings/phase-5au-evidence-index.md`
- `artifacts/phase5/ota-apk-static-review-20260804-01/`

### Phase 5AV — GhostLock upstream-fix boundary

Phase 5AV pins the upstream GhostLock fix and follow-up:
3bfdc63936dd changes remove_waiter() to operate on waiter->task, and
40a25d59e85b3 handles the subsequent not-enqueued waiter regression.
The exact Amazon 7.3.3.0 rtmutex source member remains normalized-byte-identical
to stable v4.4.146 and shows the pre-fix current-based semantics. Runtime config
confirms futex/rtmutex support, but the exact signed PS7330 boot/vmlinux and
compiled offsets remain unavailable to shell.

No GhostLock reproducer, exploit binary, ioctl, BROM/DA, fastboot or partition
operation was run. Public Android/MTK ports remain target-mismatched.

Phase 5AV outputs:

- `findings/phase-5av-ghostlock-upstream-fix-review.md`
- `output/tables/phase5av-ghostlock-evidence.csv`

### Phase 5AX — PS7330 boot/LK/recovery read-only boundary

A new exact-device read-only probe can enumerate the boot, LK and recovery
symlinks, but blockdev and dd are denied by the Android shell/SELinux boundary.
The target remains PS7330.4104N, green verified boot, flash locked and normal
Fire Launcher foreground. No block data, root payload, ioctl or boot operation
was performed.

Phase 5AX outputs:

- `tools/scripts/capture_phase5ax_boot_readonly.sh`
- `findings/phase-5ax-boot-readonly-boundary.md`
- `output/tables/phase5ax-boot-readonly.csv`

The raw device capture remains local-only because it contains device-specific
identifiers. The capture script requires an explicit serial, refuses to
overwrite an output directory, supports --dry-run, and records SHA-256 hashes.
No package, settings, OTA, reboot, root or partition state changed.

### Phase 5AY — DeviceSoftwareOTA URI and update-source static review

Phase 5AY follows the preserved PS7330 OTA APK offline. The APK's default
update-query endpoint is `https://softwareupdates.amazon.com/software/inventory2`,
but the value is read through the OTA Arcus remote-configuration key
`getUpdatesUrlPathAndMethod`. The query is an authenticated JSON POST whose
response supplies `AvailableUpdatesContainer.url`; that URL becomes the private
`PublishedUpdates.RemoteURI` database field and is later passed through
`AmazonDownloadManager`. The exact PS7330 binary URL is therefore not a fixed
string in the APK and was not recovered from shell-visible storage.

The exact `Fire_HD10-7.3.3.0-20240730.tar.bz2` source archive remains valuable
as source/config/build context for GhostLock, but it is not a signed boot image
or a root/recovery input. No OTA check, download, install, private-data bypass,
GhostLock race, root payload, reboot or partition operation was run.

Phase 5AY outputs:

- `tools/scripts/analyze_phase5ay_ota_uri_static.py`
- `findings/phase-5ay-ota-uri-source-review.md`
- `findings/phase-5ay-evidence-index.md`
- `output/tables/phase5ay-ota-uri-flow.csv`
- `output/call-graphs/phase5ay-ota-uri-flow.mmd`
- `artifacts/phase5/ota-uri-static-review-20260804-04/`

The analyzer supports `--dry-run`, refuses to overwrite an existing output,
uses a temporary JADX directory, records the APK hash, and performs no device
or network I/O.

### Phase 5AZ — GhostLock／MTK exact-target compatibility matrix

Phase 5AZ consolidates the exact PS7330 source/config evidence, the already
sealed MTK-SU failure, adjacent PS7331 compiled-kernel evidence and public
route screens. It does not run a futex race, root payload, ioctl, BROM/DA,
fastboot, bootloader or partition operation. The result is a source/config
candidate for GhostLock, not a signed PS7330 binary or root confirmation.

Phase 5AZ outputs:

- `tools/scripts/build_phase5az_compatibility_matrix.py`
- `findings/phase-5az-ghostlock-mtk-compatibility.md`
- `findings/phase-5az-evidence-index.md`
- `output/tables/phase5az-root-route-matrix.csv`

### Phase 5BA — PS7331 source／boot image and upgrade assessment

Phase 5BA records the user-provided official 7.3.3.1 source URL, the local
PS7331 OTA and `boot.img`, and a host-only compiled `remove_waiter()` review.
The PS7331 signed Image shows the old current-task cleanup pattern associated
with GhostLock; its focus kernel configuration also matches PS7330 in the
relevant futex/rtmutex/ARM64 gates. Therefore PS7331 is not currently shown to
be a GhostLock remediation, and no upgrade or image flash was performed.

PS7331 `boot.img` is retained as an adjacent-version analysis artifact only. It
must not be written alone to a PS7330 device; an official update, if ever
considered, must be treated as a potentially non-reversible full OS mutation.

Phase 5BA outputs:

- `tools/scripts/compare_phase5_ps7330_ps7331_kernel.py`
- `tools/scripts/capture_phase5ba_device_postcheck.sh`
- `findings/phase-5ba-ps7331-upgrade-assessment.md`
- `findings/phase-5ba-evidence-index.md`
- `output/tables/phase5ba-upgrade-matrix.csv`
- `output/call-graphs/phase5ba-upgrade-evidence.mmd`
- `artifacts/phase5/phase5ba-ps7331-upgrade-comparison-20260804-01/`
- `adb/phase5/PHASE5BA-DEVICE-POSTCHECK-20260804-01/`

### Phase 5BB — PS7331 GhostLock follow-up and upgrade decision

Phase 5BB adds the official NVD patch-semantic reference to the existing
PS7331 compiled review and records the remaining nested-source boundary. The
PS7331 `remove_waiter()` inspection still shows the pre-fix current-task
cleanup pattern, while the PS7330/PS7331 focus configs remain equal. This is
not evidence that every PS7331 security change is absent; it means PS7331 is
not demonstrated to remediate GhostLock and is not recommended solely for
that purpose.

The current device was not upgraded. The 7.3.3.1 `boot.img` remains a
host-only adjacent-version artifact and must not be written by itself. A full
official update, if considered for a separate A/B study, is a potentially
non-reversible system mutation and requires a frozen PS7330 baseline plus a
verified recovery/update path.

Phase 5BB outputs:

- `findings/phase-5bb-ghostlock-ps7331-followup.md`
- `findings/phase-5bb-evidence-index.md`
- `output/tables/phase5bb-ps7331-upgrade-decision.csv`
- `tools/scripts/index_phase5_nested_platform_members.sh`
- `tools/scripts/extract_phase5_nested_kernel_members.sh`

The nested source scan found both the build-selected `mt8183/4.4` tree and a
legacy `4.4` tree. The selected `mt8183/4.4/rtmutex.c` still clears
`current->pi_blocked_on` in `remove_waiter()` and has no `waiter->task` fix; the
legacy tree is byte-identical to the old v4.4.146 reference but is not the path
named by the build script. Selected source comparison artifacts are preserved
locally under `artifacts/phase5/` and are summarized by the Phase 5BB evidence
index. No source was built and no device state changed.

### Phase 5BC — GhostLock semantic boundary

Phase 5BC adds a deterministic, source-only semantics checker. It confirms that
the build-selected PS7331 `remove_waiter()` still clears
`current->pi_blocked_on`, retains the proxy rollback call, and contains no
`waiter->task` remediation. It also records the absence of an exact
KFTRWI/trona/MT8183 public Android target in the reviewed route matrix.

The subsequent source provenance check found the exact
`kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` member in the
official PS7331 archive. It is recorded as a build input only; the PS7331
boot-embedded focus config remains equal to the preserved PS7330 runtime focus
config, and no upgrade was performed.

Phase 5BC outputs:

- `findings/phase-5bc-ghostlock-semantic-boundary.md`
- `findings/phase-5bc-evidence-index.md`
- `tools/scripts/check_phase5_ghostlock_source_semantics.py`
- `tools/scripts/compare_phase5_defconfig_focus.py`
- `artifacts/phase5/exact-kernel-source-review-7331-trona-defconfig-member-20260804-01/metadata.tsv`
- `artifacts/phase5/phase5bc-defconfig-focus-20260804-01/`
- `adb/phase5/PHASE5BC-DEVICE-POSTCHECK-20260804-01/`

### Phase 5BD — PS7331 OTA boundary and redirect follow-up

Phase 5BD records a metadata-only inspection of the preserved official PS7331
full block OTA. Its updater script writes system/vendor/boot and multiple
boot-chain and firmware partitions; the standalone `boot.img` is therefore not
treated as an equivalent upgrade path. A user-consented PendingIntent
Accessibility redirect was measured 30 times and produced 0/30 stable
foreground handoffs; the visible toggle was restored off and formal HOME
remained Fire Launcher.

Phase 5BD outputs:

- `findings/phase-5bd-ota-and-redirect-followup.md`
- `findings/phase-5bd-evidence-index.md`
- `output/tables/phase5bd-ota-partition-risk.csv`
- `tools/scripts/inspect_phase5_ps7331_ota.py`
- `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/`
- `adb/phase5/PHASE5BD-ACCESSIBILITY-PENDINGINTENT-T01/`

### Phase 5BE — PS7331 build patch／overlay boundary

Phase 5BE streams the official 7.3.3.1 source bundle and lists the complete
nested `platform.tar` path set without retaining or executing the source. The
precise `.patch`/`.diff`/`series` subset contains only four Mali hrtimer patch
paths; no rtmutex/futex/GhostLock patch path appears. The visible Amazon build
script only extracts the platform tar, runs `trona_defconfig` and `make`, then
copies and validates ARM64 images; it contains no visible `git apply`, `patch`,
or rtmutex overlay step.

Together with the build-selected `mt8183/4.4/rtmutex.c` source semantics and the
PS7331 signed Image review, this does not support upgrading solely to remediate
GhostLock. PS7331 may still contain other security changes. If a general
security A/B study is later desired, use the complete official full-block OTA
as a potentially non-reversible system mutation; never write the extracted
boot image alone.

Phase 5BE outputs:

- `findings/phase-5be-ps7331-build-overlay-review.md`
- `findings/phase-5be-evidence-index.md`
- `tools/scripts/index_phase5_ps7331_nested_build_patches.sh`
- `artifacts/phase5/ps7331-nested-build-patch-index-20260804-01/`

### Phase 5BF — GhostLock source/config reachability boundary

Phase 5BF adds a deterministic host-only analyzer for the exact PS7331
build-selected `mt8183/4.4` source, the captured device config, and a fixed
reference `remove_waiter()` implementation. It confirms the source-level
pre-fix current-task cleanup pattern, the PI requeue/proxy path, and the
`CONFIG_FUTEX=y`/`CONFIG_RT_MUTEXES=y` observations. It deliberately does not
execute a reproducer, derive addresses or offsets, compile code, connect to
ADB, or claim root.

The result is a source/config reachability candidate, not an exploitability
result. The PS7331 source and inspected signed Image do not currently prove a
GhostLock remediation, so the project does not recommend upgrading solely for
that CVE. The official PS7331 full-block OTA remains a separate, potentially
non-reversible general-security A/B candidate; the extracted boot image must
not be written alone.

Phase 5BF outputs:

- `findings/phase-5bf-ghostlock-reachability.md`
- `findings/phase-5bf-evidence-index.md`
- `tools/scripts/analyze_phase5bf_ghostlock_reachability.py`
- `artifacts/phase5/ghostlock-reachability-review-20260804-04/`

### Phase 5BG — PS7331 source-to-inspected-Image semantic comparison

Phase 5BG combines the preserved PS7331 source semantics, the sanitized
instruction-pattern summary from the PS7331 boot Image, and a fixed
`waiter->task` reference. The three-way machine result is
`PS7331_INSPECTED_IMAGE_CONSISTENT_WITH_PRE_FIX_SOURCE`. This strengthens the
version-scoped conclusion that PS7331 is not demonstrated to remediate
GhostLock, while still keeping exact PS7330 signed-binary and runtime
exploitability claims out of scope.

Phase 5BG outputs:

- `findings/phase-5bg-ps7331-source-binary-semantic.md`
- `findings/phase-5bg-evidence-index.md`
- `tools/scripts/compare_phase5bg_ps7331_semantics.py`
- `artifacts/phase5/ps7331-source-binary-semantic-20260804-01/`

### Phase 5BH — official PS7331 OTA source mapping

The official Amazon update page for Fire HD 10 (11th Generation) maps to the
preserved PS7331 OTA; the HTTP content length matches the local archive. This
confirms PS7331 as a valid general security A/B candidate, but the Phase 5BG
semantic result still does not demonstrate a GhostLock fix. The OTA remains a
full-block update touching multiple system, boot-chain and firmware members;
the extracted boot image is not an equivalent upgrade.

Phase 5BH outputs:

- `findings/phase-5bh-ps7331-official-ota-source.md`
- `findings/phase-5bh-evidence-index.md`
- `artifacts/phase5/ps7331-official-update-source-20260804-01/`

## Phase 5BI status

Phase 5BI rechecked the public MTK routes against the exact KFTRWI/trona/MT8183
PS7330 evidence and the preserved official PS7331 artifacts. The pinned
KoCleo `mtk-su64` object is the same payload already tested and failed at the
critical initialization boundary, so it was not re-executed. The reviewed
public exploit survey contains vendor-specific MTK boot-chain examples but no
exact Amazon target profile.

PS7331 remains a valid host-only adjacent-version comparison and a possible
general security-update A/B candidate. It is not a demonstrated GhostLock fix:
the preserved source and inspected Image remain consistent with the pre-fix
rtmutex pattern. The official package is a full-block OTA touching boot-chain
and firmware members; the standalone `boot.img` is not an equivalent or
reversible upgrade operation. The device remains PS7330 and no upgrade or
device mutation was attempted.

Phase 5BI outputs:

- `findings/phase-5bi-mtk-public-route-recheck.md`
- `findings/phase-5bi-evidence-index.md`
- `artifacts/phase5/mtk-public-route-recheck-20260804-01/`

## Phase 5BJ status

Phase 5BJ added a host-only semantic checker for the upstream GhostLock fix. It
compares the preserved PS7330 source family, the PS7331 build-selected MT8183
source, and a fixed reference. Both Fire source inputs retain the
`current->pi_blocked_on` cleanup and `current` chain-walk argument; the fixed
reference uses `waiter->task`.

The result strengthens the decision that PS7331 is not a demonstrated
GhostLock remediation. It remains a possible general security-update A/B
candidate, but no boot image was written and the device remains PS7330.

Phase 5BJ outputs:

- `findings/phase-5bj-ghostlock-fix-application.md`
- `findings/phase-5bj-evidence-index.md`
- `tools/scripts/compare_phase5bj_ghostlock_fix.py`
- `artifacts/phase5/phase5bj-ghostlock-fix-application-20260804-01/`
- `adb/phase5/PHASE5BJ-DEVICE-READONLY-20260804-01/`

## Phase 5BK status

Phase 5BK records the preserved build metadata delta: PS7330 is at security
patch `2024-02-01`, while the official PS7331 OTA metadata is at `2024-08-01`
for the same `trona` product family. This makes PS7331 a credible general
security-update candidate, but it remains separate from the GhostLock result:
Phase 5BJ found the PS7331 rtmutex function marker still pre-fix. No OTA or
device state change was performed.

Phase 5BK outputs:

- `findings/phase-5bk-ps7331-security-delta.md`
- `findings/phase-5bk-evidence-index.md`
- `output/tables/phase5bk-security-delta.csv`
- `tools/scripts/compare_phase5bk_security_delta.py`
- `artifacts/phase5/phase5bk-security-delta-20260804-02/`

## Phase 5BL status

Phase 5BL captured the exact PS7330 futex applicability gates using a
serial-qualified, read-only ADB script. The device remains Linux 4.4.146+ /
Android 9 / PS7330.4104N with SELinux Enforcing and shell UID 2000. Shell cannot
read `/proc/kallsyms` or most selected kernel sysctls; ION and CMDQ node metadata
was listed without opening either node. No futex PI trigger, ioctl, exploit,
reboot or device mutation was performed. This improves the runtime evidence
boundary but does not prove or disprove GhostLock exploitability.

Phase 5BL outputs:

- `findings/phase-5bl-futex-runtime-gates.md`
- `findings/phase-5bl-evidence-index.md`
- `tools/scripts/analyze_phase5bl_futex_gates.py`
- `adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/`
- `artifacts/phase5/phase5bl-futex-gates-analysis-20260804-01/`
- `output/tables/phase5bl-runtime-gates.csv`

## Phase 5BM status

Phase 5BM created a host-only provenance ledger for the GhostLock binary
question. It confirms that exact PS7330 runtime/source evidence exists, but no
verified exact PS7330 signed boot/vmlinux or complete boot-chain set is present
in the workspace. The complete local OTA and boot image are PS7331 and remain
`VERSION_MISMATCH`; the installed PS7330 boot read probe returned
`Permission denied`. No files were deleted and no device operation was run.

Phase 5BM outputs:

- `findings/phase-5bm-ps7330-artifact-provenance.md`
- `findings/phase-5bm-evidence-index.md`
- `tools/scripts/build_phase5bm_artifact_ledger.py`
- `artifacts/phase5/phase5bm-artifact-ledger-20260804-01/`

## Phase 5BN status

Phase 5BN independently rechecked the GhostLock `remove_waiter()` markers and
revalidated the official PS7330/PS7331 source archive headers. Both preserved
source families remain classified as pre-fix; the fixed reference uses
`waiter->task`. The result is source/binary-provenance evidence only. No device
I/O, exploit, upgrade, bootloader operation, or partition mutation was run.

Phase 5BN outputs:

- `findings/phase-5bn-ghostlock-current-verdict.md`
- `findings/phase-5bn-evidence-index.md`
- `artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/`

## Phase 5BO status

Phase 5BO downloaded and verified the complete official PS7330 source archive,
then extracted the actual `mt8183/4.4` build-selected kernel members. The exact
PS7330 `rtmutex.c` and `futex.c` are byte-identical to the corresponding PS7331
source members and still show the pre-fix GhostLock marker. This remains
source-level evidence; no signed PS7330 boot image or live root test was created.

Phase 5BO outputs:

- `findings/phase-5bo-ps7330-full-source-build-path.md`
- `findings/phase-5bo-evidence-index.md`
- `tools/scripts/extract_phase5_ps7330_nested_members.py`
- `artifacts/phase5/ps7330-full-source-members-20260804-01/`
- `artifacts/phase5/phase5bo-exact-build-source-marker-20260804-01/`
- `adb/phase5/PHASE5BO-DEVICE-POSTCHECK-20260804-01/`

## Phase 5BP status

Phase 5BP inspected the kernel build scripts preserved in the official PS7330
source archive. The scripts select the exact `kernel/mediatek/mt8183/4.4`
subtree, `trona_defconfig`, `arm64`, and the expected Image outputs. They
reference the AOSP GCC prebuilt branch `llvm-r383902b` and recommend a
separately supplied Clang 6.0.2-compatible compiler. A static scan found no
visible executable patch, overlay, or signing step in these two files. This
strengthens source/build-path provenance but cannot prove signed production
boot-image provenance or the absence of release-CI changes. The scripts were
not executed; no toolchain was cloned, no image was built, and no device state
changed.

Phase 5BP outputs:

- `findings/phase-5bp-ps7330-build-script-analysis.md`
- `findings/phase-5bp-evidence-index.md`
- `tools/scripts/analyze_phase5bp_build_scripts.py`
- `output/tables/phase5bp-build-script-controls.csv`
- `artifacts/phase5/ps7330-build-scripts-20260804-01/`

## Phase 5BQ status

Phase 5BQ refreshed the GhostLock/public-route evidence without changing the
device. A serial-qualified read-only postcheck still reports PS7330.4104N,
security patch `2024-02-01`, ADB state `device`, and HOME resolved to
`com.amazon.firelauncher/.Launcher`. The current public `mtk-easy-su` and
LauncherHijack heads were pinned for reproducibility; neither supplies an
exact `KFTRWI/trona/MT8183/PS7330` implementation, and no unknown APK was
installed. Exact PS7330 source and inspected PS7331 source/Image remain
consistent with the GhostLock pre-fix semantic. No exploit, root payload,
unknown ioctl, reboot, OTA, fastboot, boot write, or partition operation was
performed.

Phase 5BQ outputs:

- `findings/phase-5bq-ghostlock-next-verdict.md`
- `findings/phase-5bq-evidence-index.md`
- `output/tables/phase5bq-route-matrix.csv`
- `adb/phase5/PHASE5BQ-DEVICE-POSTCHECK-20260804-01/`
- `artifacts/phase5/phase5bq-public-route-review-20260804-01/`

## Phase 5BR status

Phase 5BR performed a bounded public search for an exact
`PS7330.4104N`/`KFTRWI`/`trona` signed boot, kernel Image, or `vmlinux`. The
returned results contained device/build metadata but no matching binary. This
is explicitly a bounded search miss, not a global nonexistence claim. The
installed PS7330 boot read remains denied, while the locally available boot
artifact is adjacent PS7331 and remains `VERSION_MISMATCH`. No firmware was
downloaded or executed and no device state changed.

Phase 5BR outputs:

- `findings/phase-5br-exact-artifact-search.md`
- `findings/phase-5br-evidence-index.md`
- `artifacts/phase5/phase5br-exact-artifact-search-20260804-01/`

## Phase 5BS status

Phase 5BS focuses only on PS7331 GhostLock evidence. It re-ran the exact
`mt8183/4.4` source semantic check and added a host-only verifier that cross-
checks the PS7331 boot-image hash, preserved sanitized Image markers, source
classification, fixed-reference classification, and prior source-to-Image
comparison. All checks pass: PS7331 source and inspected Image remain
pre-fix-consistent. This establishes patch-status evidence, not live
exploitability or root. No ELF, Image, exploit, ADB, fastboot, OTA, or device
operation was executed.

Phase 5BS outputs:

- `findings/phase-5bs-ps7331-ghostlock-verdict.md`
- `findings/phase-5bs-evidence-index.md`
- `tools/scripts/verify_phase5bs_ps7331_ghostlock_evidence.py`
- `artifacts/phase5/phase5bs-ps7331-source-semantic-recheck-20260804-01/`
- `artifacts/phase5/phase5bs-ps7331-evidence-verification-20260804-01/`

## Phase 5BT status

Phase 5BT validates the complete local PS7331 source archive and rechecks the
build-selected kernel path using only host-side read-only processing. The
archive is `2563328975` bytes, its local MD5 equals the preserved S3 ETag, and
its SHA-256 is
`02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`.

The same archive's top-level build scripts select
`kernel/mediatek/mt8183/4.4`, `trona_defconfig`, and `arm64`. The extracted
build-selected `rtmutex.c` retains `current->pi_blocked_on` cleanup in
`remove_waiter()` and the `futex.c` PI requeue path still feeds the proxy-lock
API. The saved PS7331 boot Image marker review remains pre-fix-consistent. The
public path inventory found only four named Mali hrtimer patches and no named
GhostLock patch; release-CI transformations remain outside the captured
scripts.

This establishes **PS7331 static patch-status evidence**, not a live GhostLock
trigger, root, or privilege-transition proof. No source/build script was
executed, and no ADB, fastboot, OTA, exploit, boot-image write, or partition
operation was performed. The project therefore does not recommend PS7331
solely as a GhostLock remediation.

Phase 5BT outputs:

- `findings/phase-5bt-ps7331-full-source-audit.md`
- `findings/phase-5bt-evidence-index.md`
- `tools/scripts/index_phase5_ps7331_local_nested_build_inputs.sh`
- `tools/scripts/extract_phase5_ps7331_nested_members.py`
- `tools/scripts/extract_phase5_ps7331_outer_members.py`
- `artifacts/phase5/phase5bt-ps7331-source-archive-validation-20260804-01/`
- `artifacts/phase5/ps7331-local-nested-build-index-20260804-02/`
- `artifacts/phase5/ps7331-full-source-members-20260804-01/`
- `artifacts/phase5/ps7331-top-level-build-members-20260804-01/`
- `artifacts/phase5/phase5bt-build-script-controls-20260804-01.csv`
- `output/tables/phase5bt-ps7331-source-binary-status.csv`
- `output/call-graphs/phase5bt-ghostlock-source-path.mmd`

## Phase 5BU status

Phase 5BU adds the PS7331 boot-embedded `IKCONFIG` to the source/Image
cross-check. The preserved PS7331 kernel config contains
`CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`, `CONFIG_PREEMPT=y`, ARM64 VA39/4K,
`CONFIG_RANDOMIZE_BASE=y`, and `CONFIG_KALLSYMS=y`. The build-selected source
contains the `FUTEX_REQUEUE_PI`/`futex_requeue()`/`rt_mutex_start_proxy_lock()`
path, while the inspected Image contains matching function and pre-fix cleanup
markers.

This strengthens the classification to **PS7331 source/config/Image
reachability candidate**. It still does not prove a live race, kernel control,
root, or privilege transition. No futex race, memory access, exploit payload,
ADB mutation, bootloader operation, or partition write was executed.

Phase 5BU outputs:

- `findings/phase-5bu-ps7331-embedded-config-reachability.md`
- `findings/phase-5bu-evidence-index.md`
- `artifacts/phase5/phase5bu-ps7331-embedded-config-reachability-20260804-01/`
- `output/tables/phase5bu-ps7331-config-reachability.csv`
- `output/call-graphs/phase5bu-ps7331-reachability.mmd`

## Phase 5BV status

Phase 5BV adds a bounded semantic regression model for the GhostLock cleanup
mismatch. With a synthetic proxy waiter whose `task` differs from `current`,
the PS7331 pre-fix operation clears the wrong task's `pi_blocked_on`, while the
fixed operation clears the waiter task. The non-proxy same-task control passes
without a mismatch. Four host-only unit tests pass.

This is a reproducible semantic model, not a kernel reproducer, exploit,
address calculation, root test, or privilege-transition proof. No device,
kernel memory, ioctl, bootloader, or partition was touched.

Phase 5BV outputs:

- `findings/phase-5bv-ghostlock-semantic-model.md`
- `findings/phase-5bv-evidence-index.md`
- `tools/scripts/model_phase5bv_ghostlock_semantics.py`
- `tests/test_phase5bv_ghostlock_semantics.py`
- `artifacts/phase5/phase5bv-ghostlock-semantic-model-20260804-01/`

## Phase 5BW status

Phase 5BW cross-checks PS7331 against the public GhostLock fix semantics. The
build-selected PS7331 `remove_waiter()` remains in the pre-fix shape:
`current->pi_blocked_on` cleanup and `current` as the priority-chain task. The
preserved fixed reference binds and uses `waiter->task` for those operations.
The host-only checker reports `PS7331_SOURCE_MATCHES_PRE_FIX_SEMANTICS`.

This is a static PS7331 defect-status result, not a live race, memory
corruption, root, or privilege-transition proof. No kernel code, exploit,
unknown ioctl, device state, boot chain, or partition was touched.

Phase 5BW outputs:

- `findings/phase-5bw-ghostlock-fix-applicability.md`
- `findings/phase-5bw-evidence-index.md`
- `tools/scripts/compare_phase5bw_ghostlock_fix.py`
- `tests/test_phase5bw_ghostlock_fix.py`
- `artifacts/phase5/phase5bw-ghostlock-fix-applicability-20260804-01/`

## Phase 5BX status

Phase 5BX re-runs the host-only reachability analyzer against the build-selected
PS7331 source extracted from the complete 7.3.3.1 archive. It records the exact
source chain `FUTEX_*_REQUEUE_PI` → `futex_requeue()` →
`rt_mutex_start_proxy_lock(..., this->task)` → `remove_waiter()` and confirms
the pre-fix `current->pi_blocked_on` semantics. The result remains
`SOURCE_AND_CONFIG_REACHABILITY_CANDIDATE`, not a live exploit or root result.

Phase 5BX outputs:

- `findings/phase-5bx-ps7331-ghostlock-path-audit.md`
- `findings/phase-5bx-evidence-index.md`
- `output/tables/phase5bx-ghostlock-path.csv`
- `output/call-graphs/phase5bx-ghostlock-path.mmd`
- `artifacts/phase5/phase5bx-ps7331-exact-path-audit-20260804-01/`

## Phase 5BY status

Phase 5BY records the public follow-up fix review for CVE-2026-53163. The
PS7331 source returns early from `task_blocks_on_rt_mutex()` before assigning
`waiter->task`, while its proxy wrapper conditionally calls `remove_waiter()`;
the source is still pre-primary-fix and must not be treated as a complete modern
fix reference. The host-only checker classifies it as
`PRE_PRIMARY_FIX_WITH_EARLY_RETURN_GUARD_REVIEW`.

Phase 5BY outputs:

- `findings/phase-5by-ghostlock-fix-chain.md`
- `findings/phase-5by-evidence-index.md`
- `output/tables/phase5by-ghostlock-fix-chain.csv`
- `output/call-graphs/phase5by-ghostlock-fix-chain.mmd`
- `tools/scripts/analyze_phase5by_ghostlock_fix_chain.py`
- `tests/test_phase5by_ghostlock_fix_chain.py`
- `artifacts/phase5/phase5by-ps7331-ghostlock-fix-chain-20260804-02/`

## Phase 5BZ status

Phase 5BZ normalizes the preserved PS7331 binary markers and records the
address-sanitization boundary. The three saved markers for the primary pre-fix
relationship are present: `remove_waiter` reads the current-task source,
clears through that current-task register, and the proxy path calls
`remove_waiter`. The embedded config independently confirms the futex/rtmutex
path and relevant ARM64, preemption, ASLR, and seccomp settings.

The follow-up guard cannot be classified from the saved binary output because
raw branch/return disassembly and the reconstructed ELF were intentionally not
kept. The result is therefore
`PRIMARY_PRE_FIX_MARKERS_CONFIRMED_FOLLOW_UP_BINARY_UNRESOLVED`, not a claim
that the guard is present or absent. Runtime exploitability, kernel control and
root remain unproven.

Phase 5BZ outputs:

- `findings/phase-5bz-ps7331-binary-evidence-boundary.md`
- `findings/phase-5bz-evidence-index.md`
- `tools/scripts/analyze_phase5bz_ps7331_binary_boundary.py`
- `tests/test_phase5bz_ps7331_binary_boundary.py`
- `artifacts/phase5/phase5bz-ps7331-binary-evidence-boundary-20260804-01/`
- `output/tables/phase5bz-ps7331-binary-evidence.csv`
- `output/tables/phase5bz-ps7331-config-observations.csv`
- `output/call-graphs/phase5bz-ps7331-fix-boundary.mmd`

## Phase 5CA status

Phase 5CA maps the public CVE-2026-53163 follow-up patch onto the exact PS7331
4.4 source. The upstream semantic requirements are independent: skip
`remove_waiter()` for an unqueued waiter, and use a negative-only return check in
the proxy wrapper. PS7331 has neither shape in the inspected source: it returns
`-EDEADLK` at line 973 before assigning `waiter->task` at line 977, and retains
`if (unlikely(ret))` at line 1683. The futex PI requeue path reaches the proxy
call at lines 1963–1965.

This is a source-level patch applicability result only. It does not establish a
live crash, kernel control, temporary root, or privilege transition. No device
I/O or image mutation was performed.

Phase 5CA outputs:

- `findings/phase-5ca-ps7331-followup-patch-mapping.md`
- `findings/phase-5ca-evidence-index.md`
- `tools/scripts/analyze_phase5ca_ps7331_followup_patch.py`
- `tests/test_phase5ca_ps7331_followup_patch.py`
- `artifacts/phase5/phase5ca-ps7331-followup-patch-mapping-20260804-01/`
- `output/tables/phase5ca-followup-patch-mapping.csv`
- `output/call-graphs/phase5ca-ghostlock-fix-chain.mmd`

## Phase 5CB status

Phase 5CB confirms the exact PS7331 source-level futex syscall → PI requeue →
proxy-lock path and records that no direct capability/security hook was seen in
the bounded scoped functions. This is an entry-path candidate only; Android
userspace policy, runtime scheduling and exploitability are unresolved. No
device syscall, futex trigger, exploit, or root operation was performed.

## Phase 5CC status

Phase 5CC confirms source-level identity separation: the futex queue binds its
stored task to the waiting `current`, the PI requeue path passes that stored task
as an explicit proxy parameter, and PS7331 cleanup uses `current` for
`pi_blocked_on`. No scoped equality assertion was observed. This does not prove
a live mismatch or race.

## Phase 5CD status

Phase 5CD maps what cleanup writes/removes and which normal rtmutex paths later
read related state. It identifies candidate second consumers and a potential
state transition, while explicitly leaving runtime persistence, crash, memory
effect and root unproven. The work is host-only source analysis with no device
mutation.

## Phase 5CE status

Phase 5CE reviews the public `ghostlock-emerald` project as a target-profile
reference only. It targets a different Poco/MediaTek device, Android release
and kernel generation, and contains hard-coded build/layout metadata. It is not
a drop-in Fire PS7331 binary. No exploit build, installation, execution or
device mutation was performed.

## Phase 5CF status

The current explicit-serial read-only baseline reports the connected Fire tablet
as `PS7330.4104N`, not PS7331. It records MT8183, verified boot green, flash
locked, SELinux Enforcing, and the privileged Fire Launcher path. PS7331 source
and boot artifacts remain offline evidence until the device actually runs that
build; no exploit or boot/partition operation was performed.

## Phase 5CG status

Phase 5CG adds a reproducible, host-only abstract model for the exact PS7331
`ret`/early-return cleanup chain. It confirms that the `owner == task` early
return in `task_blocks_on_rt_mutex()` precedes `waiter->task = task`, that the
proxy wrapper retains a broad nonzero cleanup guard, and that `remove_waiter()`
writes `current->pi_blocked_on`. In an explicitly assumed identity-mismatch
row, the model shows why the target task's state is not directly cleared. These
are source-level and conditional results; runtime mismatch, persistent state,
crash, controlled memory effect and root remain unproven.

No futex syscall, race trigger, unknown ioctl, kernel address/payload work,
exploit execution or device mutation was performed.

Phase 5CG outputs:

- `findings/phase-5cg-ps7331-cleanup-semantics-model.md`
- `findings/phase-5cg-evidence-index.md`
- `tools/scripts/model_phase5cg_ps7331_cleanup_semantics.py`
- `tests/test_model_phase5cg_ps7331_cleanup_semantics.py`
- `output/tables/phase5cg-cleanup-semantics.csv`
- `output/call-graphs/phase5cg-cleanup-semantics.mmd`
- `artifacts/phase5/phase5cg-ps7331-cleanup-semantics-20260804-01/`

## Phase 5CI status

Phase 5CI documents Amazon's official PS7331 manual-update procedure and
matches it against the locally preserved full OTA. The package is a valid
Amazon metadata-compatible `BLOCK` OTA for `trona`, but it has not been pushed
to or installed on the tablet. The official flow is MTP file transfer followed
by Settings → Device Options → System Updates → Update; it is not a standalone
boot-image or fastboot procedure.

Output:

- `findings/phase-5ci-official-manual-update-procedure.md`

## Phase 5CJ status

The official Amazon PS7331 full OTA was applied through the native System
Updates UI. The post-update device identity is PS7331.4463N with incremental
`0031575863172` and security patch `2024-08-01`; Verified Boot remains green,
the bootloader remains locked, and SELinux remains Enforcing. The temporary
post-update OOBE resolver state is documented separately and is not treated as
a launcher replacement.

Output:

- `findings/phase-5cj-ps7331-update-and-ghostlock-boundary.md`

## Phase 5CK status

Phase 5CK is a PS7331 read-only runtime-gate capture. It records shell identity,
capability visibility, selected sysctl results, procfs restrictions, and ION/CMDQ
node metadata without opening nodes or invoking ioctl. It does not claim live
GhostLock exploitability or root.

Output:

- `findings/phase-5ck-ps7331-runtime-gates.md`

## Phase 5CL status

Phase 5CL defines the evidence gate for moving GhostLock from static analysis to
dynamic validation. A real, reproducible `waiter->task != current` observation
is required for D1, but it is not by itself proof of a persistent kernel
invariant violation or root. The stock PS7331 shell snapshot has not produced
D1 evidence and no futex trigger or kernel instrumentation was installed.

Output:

- `findings/phase-5cl-identity-mismatch-validation-gate.md`

## Phase 5CM status

Phase 5CM confirms the PS7331 runtime kernel config exposes FUTEX, RT_MUTEX,
seccomp, SELinux, debugfs, and kallsyms support, while ordinary shell access to
debugfs/tracefs remains denied. This is a feature/visibility boundary only; no
futex trigger, tracing write, device-node open, ioctl, or root operation was
performed.

Output:

- `findings/phase-5cm-ps7331-config-and-tracing-boundary.md`

## Phase 5CN status

Phase 5CN separates PS7331's futex/rtmutex feature gate from the dynamic
identity-mismatch threshold. The selected source maps the PI opcode gate,
proxy-task handoff, and `remove_waiter()` cleanup semantics; the actual device
config confirms FUTEX and RT_MUTEX support. The available source subset does
not include the complete ARM64 futex header/Kconfig expansion, and no evidence
observes `waiter->task != current`. D0 is confirmed; D1–D4 remain unobserved or
unproven. This phase is host-side/read-only and executes no futex trigger,
kernel instrumentation, ioctl, memory access, exploit or root payload.

Outputs:

- `findings/phase-5cn-futex-feature-gate.md`
- `findings/phase-5cn-evidence-index.md`
- `output/tables/phase5cn-futex-feature-gate.csv`
- `output/call-graphs/phase5cn-futex-feature-gate.mmd`

## Phase 5CO status

Phase 5CO resolves the Phase 5CN source-completeness gap for the PS7331 ARM64
futex feature gate. The official source contains the
`HAVE_FUTEX_CMPXCHG` definition, the MT8183 ARM64
`futex_atomic_cmpxchg_inatomic()` implementation, and the source-level runtime
NULL-probe path. The MT8183 ARM64 platform block does not directly select the
symbol; the only MediaTek `select HAVE_FUTEX_CMPXCHG` literal found by the
archive search is under the separate MT8167 ARM block. The embedded PS7331
IKCONFIG and device capture confirm FUTEX and RT_MUTEX support, but do not
directly expose the final `futex_cmpxchg_enabled` value.

This makes runtime PI-gate enablement a strong inference, not a dynamic
identity observation. No evidence observes `waiter->task != current`, a
persistent cleanup invariant violation, a controllable memory effect, or root.
The phase is host-only/read-only and does not execute a futex trigger, race,
kernel instrumentation, ioctl, memory access, exploit or root payload.

Outputs:

- `findings/phase-5co-ps7331-futex-config-resolution.md`
- `findings/phase-5co-evidence-index.md`
- `output/tables/phase5co-futex-config-resolution.csv`
- `output/call-graphs/phase5co-futex-config-resolution.mmd`
- `tools/scripts/extract_phase5cn_futex_arch_members.py`
- `tools/scripts/search_phase5cn_source_literals.py`

## Phase 5CP status

Phase 5CP refines the GhostLock identity question. The PS7331 source shows that
the waiting thread binds `q->task` to its own `current`, while the separate
requeue caller passes the stored `this->task` into
`rt_mutex_start_proxy_lock()`. The proxy API has an explicit task parameter,
but `remove_waiter()` uses the implicit caller `current`. Therefore source-level
cross-context identity separation is confirmed; it does not require assuming a
scheduler race merely to make the two task roles distinct.

The remaining gates are narrower and still unobserved: a non-zero proxy error
return that actually invokes `remove_waiter()`, the post-cleanup task/PI state,
and any later consumer. The phase is host-only/read-only and performs no futex
syscall, race, kernel execution, device I/O, address/payload generation or root
operation.

Outputs:

- `findings/phase-5cp-ps7331-proxy-context-audit.md`
- `findings/phase-5cp-evidence-index.md`
- `output/tables/phase5cp-proxy-context.csv`
- `output/call-graphs/phase5cp-proxy-context.mmd`
- `tools/scripts/audit_phase5cp_proxy_context.py`

## Phase 5CR status

Phase 5CR pulled the exact PS7331 Fire `/system/lib64/libc.so`, `linker64`, and
`app_process64` using an explicit serial and read-only ADB commands. The Fire
libc contains a generic futex wait helper and a separate PI-lock helper. The
condition-variable call sites use the generic wait helper; the PI mutex path
uses the PI-lock helper. A bounded host-side symbol/call-edge audit did not
establish a requeue-PI caller in this libc. This is stronger Fire-specific
userspace evidence, but it still does not observe the kernel proxy error path,
identity mismatch, cleanup residue, memory effect or root.

No pulled ELF was executed. No futex, race, ioctl, device-node, kernel-memory,
payload, settings, package, boot or partition operation was performed.

Outputs:

- `findings/phase-5cr-fire-libc-futex-analysis.md`
- `findings/phase-5cr-evidence-index.md`
- `output/tables/phase5cr-fire-libc-futex.csv`
- `output/call-graphs/phase5cr-fire-libc-futex.mmd`
- `tools/scripts/capture_phase5cr_fire_native.py`
- `tools/scripts/analyze_phase5cr_fire_libc.py`

## Phase 5CQ status

Phase 5CQ adds a bounded Android 9 userspace reachability audit. The official
Android 9 r61 bionic pthread condition-variable reference uses ordinary futex
wait/wake helpers; it does not establish a requeue-PI caller. The AOSP UAPI
header exposes PI/requeue-PI names, but that is only an API-surface observation.
The AOSP syscall table and seccomp files are reference evidence, not proof of
the Fire-specific native policy. Fire PS7331 caller, policy allowance, runtime
identity mismatch, cleanup residue and root remain unobserved/unproven.

This phase is host-only and does not execute a futex syscall, construct a race,
generate addresses or payloads, touch a device node, modify the device, or run a
root operation.

Outputs:

- `findings/phase-5cq-android9-userspace-reachability.md`
- `findings/phase-5cq-evidence-index.md`
- `output/tables/phase5cq-userspace-reachability.csv`
- `output/call-graphs/phase5cq-userspace-reachability.mmd`
- `tools/scripts/audit_phase5cq_userspace_reachability.py`

## Phase 5CS status

Phase 5CS performs a bounded, host-only inventory of already readable Fire
PS7331 native artifacts. The exact Fire `libart.so` contains the diagnostic
`futex cmp requeue failed for` and the `ThreadList::SuspendAllInternal` method;
host disassembly shows that method reaches the libc `syscall` boundary. The
matching AOSP ART source maps that diagnostic to ordinary `FUTEX_CMP_REQUEUE`,
not to a demonstrated PI requeue proxy path. This is a new Fire userspace route
distinction, not GhostLock dynamic validation.

`libandroid_runtime.so` contains seccomp setup references, but the Fire
app-domain policy is not recovered by this capture. The selected Amazon native
libraries have no named requeue-PI caller in a bounded strings/symbol scan;
this remains a negative observation rather than an exhaustive absence claim.
Vendor listings and access denials are preserved; no native binary was executed.

Phase 5CS does not observe `waiter->task != current`, wrong-target cleanup,
persistent state damage, a later consumer, controlled memory effect or root.
No futex trigger, race, ioctl, kernel-memory, payload, boot or partition
operation was performed.

Outputs:

- `findings/phase-5cs-fire-art-futex-analysis.md`
- `findings/phase-5cs-evidence-index.md`
- `output/tables/phase5cs-native-inventory.csv`
- `output/call-graphs/phase5cs-native-futex-flow.mmd`
- `tools/scripts/analyze_phase5cs_native_inventory.py`

## Phase 5CT status

Phase 5CT deepens the public `ghostlock-emerald` review without building or
executing it. The Emerald source has a build-specific target selector, a
coordinated userspace PI-requeue architecture, and target-specific post-trigger
memory/root stages. Fire PS7331 source confirms the defect-family kernel path,
but Fire userspace requeue-PI reachability, runtime identity mismatch, cleanup
residue, memory effect and privilege transition remain unobserved.

The public Emerald profile targets Poco M6 Pro/MT6789/Android 16/6.12.30,
whereas the tablet is PS7331/MT8183/Android 9/4.4. This is a profile mismatch,
not a missing single offset. No exploit source was adapted, compiled, installed
or executed; no futex trigger, kernel memory operation, root payload, boot or
partition operation was performed.

Outputs:

- `findings/phase-5ct-ghostlock-architecture-audit.md`
- `findings/phase-5ct-evidence-index.md`
- `output/tables/phase5ct-ghostlock-architecture.csv`
- `output/call-graphs/phase5ct-ghostlock-architecture.mmd`
- `tools/scripts/build_phase5ct_architecture_matrix.py`

## Phase 5CU status

Phase 5CU captures the PS7331 seccomp boundary using read-only process status,
policy listings and policy pulls. `system_server`, Microsoft Launcher, SystemUI,
OTA and research APK processes report `Seccomp: 2`; `adbd` reports `Seccomp: 0`
but remains UID 2000 with zero capabilities. Selected media/configstore service
policies contain `futex: 1`, but the ordinary app-domain filter was not recovered.

This confirms a userspace policy gate without proving whether PI requeue is
allowed or reachable. No futex operation, exploit, native payload, security
policy change or device mutation was performed.

Outputs:

- `findings/phase-5cu-ps7331-seccomp-reachability.md`
- `findings/phase-5cu-evidence-index.md`
- `output/tables/phase5cu-seccomp-reachability.csv`
- `output/call-graphs/phase5cu-seccomp-reachability.mmd`
- `adb/phase5/PHASE5CT-SECCOMP-20260804-01/`

## Phase 5CV status

Phase 5CV separates the PS7331 return-value domains around the proxy cleanup
path. `ret=1` from the initial lock acquisition returns before cleanup;
`task_blocks_on_rt_mutex()` can return early before assigning `waiter->task`;
an owner-release condition can reset a nonzero result to zero; and only the
remaining nonzero path reaches `remove_waiter()`. The futex requeue caller then
branches on positive, zero and negative proxy results.

This confirms why `if (ret)` and early-return ordering matter, but does not
observe the stock runtime error branch, identity mismatch, cleanup residue,
memory effect or root. No futex trigger, race, exploit or device mutation was
performed.

Outputs:

- `findings/phase-5cv-ps7331-ret-early-return-audit.md`
- `findings/phase-5cv-evidence-index.md`
- `output/tables/phase5cv-ret-early-return.csv`
- `output/call-graphs/phase5cv-ret-early-return.mmd`

## Phase 5CW status

Phase 5CW performs a host-only comparison of the exact PS7331 `rtmutex.c`
against a preserved upstream fixed reference and the documented upstream
follow-up patch. PS7331 is confirmed to retain the primary pre-fix
`current->pi_blocked_on` cleanup and the broad `if (unlikely(ret))` proxy
cleanup condition. Its self-deadlock return also occurs before
`waiter->task = task`. Upstream separately changed cleanup to use
`waiter->task`, then added an un-enqueued-waiter guard and restricted the
wrapper cleanup condition to `ret < 0`.

This makes the static control-flow boundary more precise, but it does not
capture a stock-device `waiter->task != current` identity mismatch, cleanup
residue, a later consumer, a memory effect or root. No futex trigger, race,
exploit, kernel-memory operation, payload, boot or partition operation was
performed.

Outputs:

- `findings/phase-5cw-upstream-followup-fix-diff.md`
- `findings/phase-5cw-evidence-index.md`
- `output/tables/phase5cw-upstream-fix-diff.csv`
- `output/call-graphs/phase5cw-upstream-fix-chain.mmd`
- `tools/scripts/compare_phase5cw_upstream_followup.py`
- `tests/test_phase5cw_upstream_followup.py`

## Phase 5CY status

Phase 5CY captures the current PS7331 runtime observation boundary without
calling futex or enabling tracing. The kernel config includes futex, rtmutex
and generic trace infrastructure, but the device exposes no futex tracepoint to
shell; `/proc/kallsyms` is denied, `/proc/kcore` and `/dev/kmem` are absent, and
the captured process policies do not provide a root-capable shell. The bounded
logcat filter had no futex/rtmutex/requeue/seccomp signal.

The read-only HOME snapshot also found an OOBE/test residue (`user_setup_complete=0`,
OOBE resolver and Phase 4 alias foreground). Fire Launcher was explicitly
started to restore the foreground only; no package, settings, data or
partition state was changed. This state is excluded from GhostLock inference.

No stock runtime `waiter->task != current`, cleanup residue, memory effect or
root was observed.

Outputs:

- `findings/phase-5cy-ps7331-runtime-observation-boundary.md`
- `findings/phase-5cy-evidence-index.md`
- `output/tables/phase5cy-runtime-boundary.csv`
- `tools/scripts/capture_phase5cy_runtime_boundary.sh`
- `tools/scripts/capture_phase5cy_home_boundary.sh`
- local raw captures under `adb/phase5/PHASE5CY-*`

## Phase 5DA status

Phase 5DA fully extracts the official `Fire_HD10-7.3.3.1-20250617.tar.bz2`
source archive locally without executing its contents or touching the tablet.
The outer archive SHA-256 is
`02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`.
Its primary `platform.tar` and `fireos.tar` members are extracted into
separate local directories. The platform build recipe explicitly selects
`kernel/mediatek/mt8183/4.4`, `trona_defconfig`, and `arm64`; the source tree
contains the four trona DTBs and the exact MT8183 futex/rtmutex files used by
the preceding static review.

The local index covers 173,535 files and hashes 1,094 focus files. The public
repository keeps the indexing script, report, evidence index, and summary
table; the multi-gigabyte extracted source remains local and is reproducible
from the preserved archive. The package does not provide Fire Launcher Java
source or a complete `frameworks/`/system-server source tree, so those
conclusions still require the APK/JAR artifacts and AOSP comparison.

Outputs:

- `findings/phase-5da-ps7331-source-tree-index.md`
- `findings/phase-5da-evidence-index.md`
- `output/tables/phase5da-source-tree-summary.csv`
- `tools/scripts/index_phase5da_source_tree.py`
- local index under `artifacts/phase5/phase5da-ps7331-source-tree-index-20260804-01/`

## Phase 5CZ status

Phase 5CZ records the provenance boundary for the futex selftests. The PS7331
source contains requeue-PI selftests and its kernel Makefile describes a
root-run workflow after building, installing, and booting a kernel. A bounded
read-only search of standard device paths found no matching selftest binary;
no selftest was copied, built, or executed. This does not establish or deny a
GhostLock runtime identity mismatch.

Outputs:

- `findings/phase-5cz-selftest-provenance.md`
- `findings/phase-5cz-evidence-index.md`
- `output/tables/phase5cz-selftest-provenance.csv`
- `tools/scripts/capture_phase5cz_selftest_presence.sh`
- local raw capture under `adb/phase5/PHASE5CZ-SELFTEST-PRESENCE-20260804-01/`

## Phase 5DB status

Phase 5DB corrects the historical version-scope ambiguity and records a fresh
read-only exact-target match. The connected `KFTRWI/trona/MT8183` tablet is
`PS7331.4463N/0031575863172`; its fingerprint, incremental, product, and
security patch all match the official PS7331 full OTA metadata. The exact
build-selected MT8183 source and preserved PS7331 boot Image markers both
remain pre-fix-consistent for the GhostLock `current` cleanup semantics.

This closes the PS7331 provenance gate, not the runtime exploitability gate.
No `waiter->task != current` observation, cleanup residue, memory effect, or
privilege transition has been obtained. No futex trigger, root payload, kernel
memory operation, boot write, or partition operation was performed.

Outputs:

- `findings/phase-5db-ps7331-exact-target-ghostlock-chain.md`
- `findings/phase-5db-evidence-index.md`
- `output/tables/phase5db-ghostlock-gates.csv`
- `tools/scripts/capture_phase5db_exact_ps7331_match.sh`
- `tools/scripts/verify_phase5db_ps7331_exact_chain.py`
- local exact-target capture under `adb/phase5/PS7331-EXACT-MATCH-20260804-01/`

## Phase 5DC / Phase 6A boundary

Phase 5DC classifies every `FUTEX_*_REQUEUE_PI` hit in the locally extracted
PS7331 source by role. The exact MT8183 kernel implementation is present, and
direct wrappers are present only in the kernel futex selftests/documentation;
the bounded Fire libc/Amazon native scan found no named shipped userspace
caller. This is a bounded negative observation, not proof that an indirect or
unpulled caller cannot exist. No source, native object, futex operation, race,
kernel memory path, payload or device state was executed.

Outputs:

- `findings/phase-5dc-ps7331-requeue-pi-caller-audit.md`
- `findings/phase-6a-runtime-verification-boundary.md`
- `output/tables/phase5dc-requeue-pi-callers.csv`
- `output/call-graphs/phase5dc-userspace-boundary.mmd`
- `tools/scripts/audit_phase5dc_requeue_pi_callers.py`
- local audit artifact under `artifacts/phase5/phase5dc-requeue-pi-caller-audit-20260804-05/`

Phase 6A remains a runtime-observation design boundary. A stock-device
requeue-PI trigger or race is not part of this repository workflow; any
instrumented emulator/research-kernel result must be labeled `LAB_ONLY` and
must not be presented as PS7331 stock-runtime evidence.

## Phase 5DF status

Phase 5DF extracted the exact PS7331 source-level futex dispatch boundary:
the syscall switch reaches the requeue-PI handlers, the requeue path passes
`this->rt_waiter` and `this->task` into `rt_mutex_start_proxy_lock`, and the
pre-fix cleanup landmarks remain in `rtmutex.c`. This is source reachability
evidence only. It does not prove a shipped userspace caller, a runtime
identity mismatch, cleanup residue, memory corruption, or root.

Outputs:

- `findings/phase-5df-futex-dispatch-boundary.md`
- `findings/phase-5df-evidence-index.md`
- `output/tables/phase5df-futex-dispatch.csv`
- `tools/scripts/audit_phase5df_futex_dispatch_boundary.py`
- local audit under `artifacts/phase5/phase5df-futex-dispatch-boundary-20260804-01/`

## Phase 5DD status

Phase 5DD extends the caller audit to all 16 preserved Fire ELF inputs from
the libc/linker, ART/runtime, Binder/utils and selected Amazon-native captures.
There are no named `REQUEUE_PI` markers. The remaining markers are ordinary
futex/PI-lock helpers, ART compare-requeue diagnostics, or a generic `syscall`
boundary. These are artifact-surface observations, not runtime call proof.

Outputs:

- `findings/phase-5dd-native-futex-surface.md`
- `findings/phase-5dd-evidence-index.md`
- `output/tables/phase5dd-native-futex-summary.csv`
- `tools/scripts/audit_phase5dd_native_futex_surface.py`
- local inventory under `artifacts/phase5/phase5dd-native-futex-surface-20260804-03/`

## Phase 5DI status

Phase 5DI added the preserved services.odex and fosservices.odex to the
native futex surface audit. Both are AArch64 ELF inputs with no visible
futex/rtmutex/requeue-PI or generic syscall marker. This is a bounded
negative observation, not proof that stripped or indirect runtime code cannot
reach futex.

Outputs:

- findings/phase-5di-additional-odex-futex-surface.md
- findings/phase-5di-evidence-index.md
- local inventory under artifacts/phase5/phase5di-additional-odex-futex-surface-20260804-01/

## Phase 5DH status

Phase 5DH compared the Emerald reference prerequisites with the exact PS7331
IKCONFIG and source. PS7331 explicitly enables FUTEX, RT_MUTEXES, CONFIGFS_FS,
SLUB, SECCOMP and RANDOMIZE_BASE, while CONFIG_USERFAULTFD is explicitly not
set. Generic source presence is not evidence of a usable kernel read/write
primitive or a portable root chain.

Outputs:

- findings/phase-5dh-ps7331-reference-surface-gates.md
- findings/phase-5dh-evidence-index.md
- output/tables/phase5dh-reference-surface-matrix.csv
- tools/scripts/audit_phase5dh_ps7331_reference_surfaces.py
- local audit under artifacts/phase5/phase5dh-ps7331-reference-surface-gates-20260804-01/

## Phase 5DG status

Phase 5DG statically audited the public datfooldive/ghostlock-emerald source
at commit ebb355d302629a034d0959e5e579496559e8f84e. It contains an explicit
PI/requeue userspace orchestration followed by target-specific layout,
kernel-memory primitive and credential-transition stages, but targets a
different MT6789/Linux 6.12/Android 16 device. It was not compiled or run.
Its source architecture is evidence for what a complete port would need, not
evidence that PS7331 can be rooted.

Outputs:

- findings/phase-5dg-ghostlock-emerald-architecture.md
- findings/phase-5dg-evidence-index.md
- tools/scripts/audit_ghostlock_reference_architecture.py
- local audit under artifacts/phase5/phase5dg-ghostlock-emerald-architecture-20260804-01/

## Phase 5DE status

Phase 5DE excludes kernel trees and searches the PS7331 source package for
userspace futex operations. It finds only GLib ordinary direct
`syscall(__NR_futex, FUTEX_WAIT/FUTEX_WAKE, ...)` in two external source files;
there are zero `FUTEX_LOCK_PI`, `FUTEX_UNLOCK_PI` or requeue-PI rows. This is
source/build-input evidence, not proof that the code shipped or ran on the
tablet, but it further separates ordinary futex synchronization from the
GhostLock proxy path.

Outputs:

- `findings/phase-5de-userspace-futex-source.md`
- `findings/phase-5de-evidence-index.md`
- `output/tables/phase5de-userspace-futex-summary.csv`
- `tools/scripts/audit_phase5de_userspace_futex_source.py`
- local audit under `artifacts/phase5/phase5de-userspace-futex-source-audit-20260804-03/`

## Phase 6A PI smoke status

PHASE6A-PI-SMOKE-T01 的 benign single-thread PI lock/unlock source 可編譯成
AArch64 relocatable object，但 host 缺少 ld.lld，沒有產生 Android ELF，
沒有 push 或執行。這不是 runtime mismatch 或 exploitability 結果。

Outputs:

- tools/test-phase6a/pi_lock_smoke.c
- tools/scripts/build_phase6a_pi_lock_smoke.sh
- findings/phase-6a-pi-lock-smoke-test.md
- local result under artifacts/phase6a/phase6a-pi-lock-smoke-T01/

## Phase 6A PI smoke T02

The exact PS7331 device completed one benign uncontended PI lock/unlock run
under shell UID 2000 with exit code 0. The temporary binary was removed,
ADB remained connected, and the build fingerprint was unchanged. This is
ordinary PI-futex reachability evidence only; it is not requeue-PI or
GhostLock exploitability evidence.

Outputs:

- findings/phase-6a-pi-lock-smoke-evidence-index.md
- local raw evidence under adb/phase6a/PHASE6A-PI-SMOKE-T02/
- local result under artifacts/phase6a/phase6a-pi-lock-smoke-T02/

## Phase 6B host-only layout model

Phase 6B is limited to PS7331 source/config provenance and a host-side AArch64
record-layout model. It does not execute `FUTEX_CMP_REQUEUE_PI`, create a proxy
waiter, arrange a race, spray ION/pipe objects, calculate a KASLR slide, read or
write kernel memory, or attempt privilege escalation. The stock-device runtime
trigger is recorded as **因風險拒絕測試** in
`findings/phase-6-step4-runtime-gate.md`.

Reproduce the model offline using the preserved PS7331 source and config:

```sh
python3 tools/scripts/model_phase6b_ps7331_layout.py \
  --source-root firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4 \
  --config artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config \
  --output artifacts/phase6b/phase6b-host-layout-YYYYMMDD-NN
```

The script refuses to overwrite an existing output and supports `--dry-run`.
The public model records `task_struct`, `rt_mutex_waiter`, `pipe_buffer`, and
`ion_buffer` layout facts with source hashes. In the inspected requeue-PI path,
`rt_mutex_waiter` is a local kernel-stack object, not a direct kmalloc/SLUB
waiter object; pipe and ION cache classes are allocator facts, not proof of
adjacency, reuse, corruption, or exploitability. The generated artifact and
evidence index are under `artifacts/phase6b/` and `findings/phase-6b-*`.

The exact-source reason for rejecting the stock-device Step 4 harness is
documented in `findings/phase-6-step4-source-safety-analysis.md`: the operation
dispatches into `futex_requeue(..., requeue_pi=1)`, can prepare PI state, and can
reach proxy/cleanup branches. A single-thread or single-call constraint does
not turn that path into a read-only probe.

The host-only semantic comparison is reproducible with
`tools/scripts/compare_phase6b_rtmutex_semantics.py`. It compares the PS7331
source with the preserved legacy v4.4.146 source and a fixed v6.1.175 focused
slice, while treating unavailable functions as `UNAVAILABLE` rather than as
semantic differences. Its derived output is
`artifacts/phase6b/phase6b-rtmutex-semantics-20260804-01/`.

The PS7331 functional selftest role inventory is generated by
`tools/scripts/analyze_phase6b_requeue_selftests.py` and stored under
`artifacts/phase6b/phase6b-requeue-selftests-20260804-01/`. The preserved tests
use waiter/waker, child, or signal coordination and `-pthread`; they are
provenance evidence, not a safe single-thread device probe.

Phase 6C host preparation is recorded under
`findings/phase-6c-lab-readiness.md` and generated by
`tools/scripts/check_phase6c_lab_readiness.py`. The current audit is
`NOT_READY`: QEMU AArch64 is unavailable and the PS7331 config lacks both
KASAN and debug info. No kernel was built or booted; any future instrumented
environment must remain `LAB_ONLY` and separate from the stock tablet.

Phase 6C also contains a source-order identity model at
`findings/phase-6c-identity-state-model.md`, generated by
`tools/scripts/model_phase6c_identity_state.py`. It confirms the ordering of
early deadlock return, waiter-task assignment, proxy argument passing, and
current-task cleanup without claiming that the two task identities differ at
runtime.

Any instrumented kernel, QEMU/KASAN experiment, requeue-PI trigger, race
reproducer, panic test, or privilege-transition payload must be separately
labelled `LAB_ONLY` and must not be copied to or run on the stock tablet.

## Phase 6C runtime boundary snapshot

`PHASE6C-BOUNDARY-RO-20260804-05` is a fresh, selected-serial, read-only
snapshot of the PS7331 tablet. It preserves the complete command outputs and
per-file SHA-256 manifest under
`adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/`. Reproduce it with:

```sh
tools/scripts/capture_phase6c_runtime_boundary.sh \
  --serial G001LT0511550CFT \
  --output adb/phase6c/PHASE6C-BOUNDARY-RO-YYYYMMDD-NN
```

The script refuses to overwrite an existing directory and supports
`--dry-run`. It does not clear logcat, launch activities, send input, change
settings or package state, enable tracing, open device nodes, reboot, invoke
futex, or read/write kernel memory. The resulting evidence is summarized in
`findings/phase-6c-runtime-boundary.md` and
`findings/phase-6c-runtime-boundary-evidence-index.md`.

The snapshot captured `user_setup_complete=0` and a resolver result of the
OOBE Home activity at priority 100, while the current foreground was a
Microsoft Launcher task and Fire Launcher remained in the task/window state.
This is a context-change observation, not new GhostLock or Amazon callback
proof; no requeue-PI operation was attempted.

## Phase 6C host-only re-verification

The preserved PS7331 source was re-audited offline on 2026-08-04. The fresh
landmark audit and identity model confirm the `FUTEX_CMP_REQUEUE_PI` dispatch,
stored waiter/task proxy arguments, broad nonzero cleanup branch, and
`current->pi_blocked_on` cleanup marker. They do not establish a runtime
identity mismatch, cleanup residue, memory effect, or privilege transition.

Outputs:

- `findings/phase-6c-host-reverification.md`
- `findings/phase-6c-host-reverification-evidence-index.md`
- `artifacts/phase6c/phase6c-dispatch-audit-20260804-01/`
- `artifacts/phase6c/phase6c-identity-model-20260804-02/`

The real-device single-thread requeue-PI Step 4 remains **因風險拒絕測試**:
the syscall is stateful and reaches the very proxy path under investigation.
Phase 6A ordinary private PI lock/unlock is not equivalent evidence.

## Phase 6C userspace reachability audit

The preserved Fire/Amazon native ELF set was rescanned offline on 2026-08-04:
16 ELF files, zero named requeue-PI markers, five ordinary/PI-helper-only
surfaces, one generic syscall boundary, and ten files without a named futex
marker. ART's `futex cmp requeue failed for` string is retained as a diagnostic
marker only; it does not establish the `FUTEX_CMP_REQUEUE_PI` opcode or a proxy
waiter.

Outputs:

- `findings/phase-6c-userspace-reachability.md`
- `findings/phase-6c-userspace-reachability-evidence-index.md`
- `artifacts/phase6c/phase6c-userspace-native-scan-20260804-01/`

This is bounded artifact-scan evidence. Stripped, inline, numeric, indirect,
unpulled, or generated callers remain **待驗證**; no device-side trigger was
run.

## Phase 6C futex/policy surface

The PS7331 source/config was audited offline against the preserved userspace
tree and native summary. The config enables FUTEX, RT_MUTEXES, SECCOMP and
SECCOMP_FILTER, while the non-kernel source contains only ordinary WAIT/WAKE
hits and no named requeue-PI hit. No recognizable seccomp/zygote/syscall policy
file was found outside kernel paths in the captured source archive; this is a
coverage limitation, not proof that the installed runtime has no policy.

Outputs:

- `tools/scripts/audit_phase6c_futex_policy_surface.py`
- `findings/phase-6c-futex-policy-surface.md`
- `findings/phase-6c-futex-policy-surface-evidence-index.md`
- `artifacts/phase6c/phase6c-futex-policy-surface-20260804-01/`

The analyzer is host-only, refuses to overwrite outputs, and supports
`--dry-run`.

## Phase 6C installed-artifact policy audit

The preserved PS7331 installed-artifact candidates were audited offline on
2026-08-04. The scan covered the selected framework/APK set, ODEX/VDEX files,
Amazon init/callback XMLs, and preserved zygote/native artifacts. It found no
named `FUTEX_CMP_REQUEUE_PI` or `FUTEX_WAIT_REQUEUE_PI` marker. Generic
`SECCOMP`/`NO_NEW_PRIVS` strings in `linker64` and zygote strings in
`app_process64` are retained as surface clues only; they do not reveal a
futex allowlist or prove runtime policy enforcement.

The raw image files remain unmounted and were not content-scanned in this
pass. This is a coverage boundary, not an absence proof. No device-side
requeue-PI, paired waiter, race, panic, kernel-memory operation, or root
payload was run.

Outputs:

- `tools/scripts/audit_phase6c_installed_artifacts.py`
- `findings/phase-6c-installed-artifact-policy-audit.md`
- `findings/phase-6c-installed-artifact-policy-evidence-index.md`
- `artifacts/phase6c/phase6c-installed-artifact-policy-20260804-04/`

The script is host-only, refuses to overwrite an existing output, and
supports `--dry-run`.

## Phase 6C seccomp policy boundary addendum

The preserved PS7331 read-only capture includes service seccomp profiles and a
process-status snapshot. The five recovered service profiles contain generic
`futex: 1` rules, while the listed app/SystemUI/OTA processes report
`Seccomp: 2`. No ordinary app policy file was recovered, and no named
`FUTEX_CMP_REQUEUE_PI` or `FUTEX_WAIT_REQUEUE_PI` rule/caller marker was found.
This distinguishes service-policy evidence from app-policy evidence; it does
not prove that an untrusted app can or cannot reach requeue-PI.

Outputs:

- `findings/phase-6c-seccomp-policy-boundary.md`
- `findings/phase-6c-seccomp-policy-evidence-index.md`
- `artifacts/phase6c/phase6c-installed-artifact-policy-20260804-05/`

The device was not sent a futex call. Race, panic, kernel-memory and root
testing remain outside the stock-device boundary.

## Phase 6C image policy／zygote coverage

The preserved PS7331 `system.img` and `vendor.img` were inspected on the host
with `debugfs 1.47.4` using read-only `rdump`/`dump` commands. The canonical
extraction recovered 281 raw files, including root `/init`, from selected policy/config paths without
mounting or writing either image. It includes service seccomp profiles,
zygote init files, `app_process64`, Bionic/ART runtime libraries, SELinux
contexts/policy, permissions, sysconfig, init and BPF paths.

The extracted service profiles contain generic `futex: 1` entries, but no named
requeue-PI rule. The raw-tree marker audit found zero named
`FUTEX_CMP_REQUEUE_PI`/`FUTEX_WAIT_REQUEUE_PI` markers and five generic futex
policy lines. This is bounded artifact evidence; it does not classify the
ordinary app filter or prove a runtime opcode allow/deny result.

The image also contains `rootable_*_sepolicy.cil` variants. A host-only
comparison confirms they differ from the standard policy and include broader
`su`-related type-attribute membership. The compiled `/init` contains strings
for both rootable and standard policy paths, but this does not reveal the
selection branch or prove that rootable policy is active. Runtime policy
selection is therefore **待驗證**; the filename is not evidence of active root.

Outputs:

- `tools/scripts/extract_phase6c_image_policy_readonly.sh`
- `tools/scripts/audit_phase6c_installed_artifacts.py`
- `tools/scripts/audit_phase6c_selinux_policy_variants.py`
- `findings/phase-6c-image-policy-extraction.md`
- `findings/phase-6c-image-policy-evidence-index.md`
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/`
- `artifacts/phase6c/phase6c-image-policy-marker-audit-20260804-04/`
- `artifacts/phase6c/phase6c-selinux-variant-audit-20260804-02/`

The extractor and audits refuse to overwrite an existing output and support
`--dry-run`. No stock-device requeue-PI call, paired waiter, race, panic,
heap-shaping, kernel-memory access or root payload was executed.

## Phase 6C requeue-PI precondition model

The exact source was modeled into two abstract states. A single-context call
without a matching waiter reaches the `top_waiter == NULL` return and cannot
observe `waiter->task != current`; a paired waiter/proxy context can reach the
proxy call but is stateful and is outside the stock-device safety boundary.
PI-state preparation can occur before the no-waiter return, so even that path is
not a strictly read-only probe.

Outputs:

- `tools/scripts/model_phase6c_requeue_preconditions.py`
- `findings/phase-6c-requeue-precondition-model.md`
- `findings/phase-6c-requeue-precondition-evidence-index.md`
- `artifacts/phase6c/phase6c-requeue-preconditions-20260804-02/`

## Phase 6C requeue-PI protocol analysis

The preserved PS7331 futex selftests were analyzed on the host. The analysis
records the waiter/waker pairing, synchronization ordering, mismatch-test
setup, and the kernel no-waiter/proxy boundary. It does not compile or execute
the selftests, create threads, schedule a race, contact a device, access kernel
memory, or generate a payload.

Outputs:

- `tools/scripts/analyze_phase6c_requeue_protocol.py`
- `findings/phase-6c-requeue-protocol-analysis.md`
- `findings/phase-6c-requeue-protocol-evidence-index.md`
- `artifacts/phase6c/phase6c-requeue-protocol-analysis-20260804-01/`

The selected-device read-only boundary capture is retained locally at
`adb/phase6c/PHASE6C-RO-CAPTURE-20260804-01/` and documented in
`findings/phase-6c-runtime-capture-20260804-01.md`. Its HOME/setup-state
observation is snapshot-scoped and is not treated as GhostLock runtime or root
evidence.

## Phase 6C `/init` policy-loader static audit

The preserved PS7331 `/init` was disassembled on the host without executing
the ELF. An ADRP/ADD mapping confirms code-level references to both
`rootable_*` and standard SELinux policy paths. The two path-building regions
call a common stripped helper with different flag values, and a separate
function compares `androidboot.selinux` with `permissive`. This is provenance
evidence for a policy-loader decision surface, not evidence that the rootable
variant is active or that shell can change it.

Outputs:

- `tools/scripts/analyze_phase6c_init_policy_loader.py`
- `findings/phase-6c-init-policy-loader-analysis.md`
- `findings/phase-6c-init-policy-loader-evidence-index.md`
- `findings/phase-6b-6c-follow-up.md`
- `output/call-graphs/phase6c-policy-loader.mmd`
- `artifacts/phase6c/phase6c-init-policy-loader-audit-20260804-02/`

The analyzer is host-only, refuses to overwrite an existing output, and
supports `--dry-run`. It does not contact ADB, load policy, change boot
properties, trigger futex/race/panic behavior, access kernel memory, or emit a
root payload.

## Phase 6C GhostLock consistency audit

The exact PS7331 source, extracted kernel config, preserved boot-image metadata,
and existing runtime reports were joined by a host-only consistency audit. The
source dispatch/proxy landmarks and core config gates are present, but the
ordinary PI smoke test did not issue requeue-PI and no proxy identity mismatch,
cleanup residue, memory effect, or privilege transition has been observed.

The public `ghostlock-emerald` project targets a different device/kernel
(Poco M6 Pro / MT6789 / Android 16 / 6.12.30), so it is not a drop-in PS7331
compatibility proof.

Outputs:

- `tools/scripts/audit_phase6c_ghostlock_consistency.py`
- `findings/phase-6c-ghostlock-consistency-audit.md`
- `findings/phase-6c-ghostlock-consistency-evidence-index.md`
- `output/call-graphs/phase6c-ghostlock-evidence-flow.mmd`
- `artifacts/phase6c/phase6c-ghostlock-consistency-20260804-05/`

The audit is host-only, refuses to overwrite an existing output, and supports
`--dry-run`. Stock-device requeue-PI, paired waiter, race, panic, heap shaping,
kernel-memory and root-payload testing remain rejected.

## Phase 6C GhostLock upstream patch-chain audit

The preserved PS7331 GPL source was compared on the host with the public
upstream cleanup-target, early-return and waiter-state patch-chain. The source
still contains the `current->pi_blocked_on` cleanup marker, the broad
`if (unlikely(ret))` wrapper branch, and the futex proxy call/caller branch;
the later `waiter_task`/`ret < 0`/enqueued-guard signatures were not found.
This is **已證實（source scope）** and a **高可信 pre-fix inference**, not a
runtime GhostLock or root result.

Outputs:

- `tools/scripts/audit_phase6c_ghostlock_patch_chain.py`
- `findings/phase-6c-ghostlock-patch-chain-audit.md`
- `findings/phase-6c-ghostlock-patch-chain-evidence-index.md`
- `output/call-graphs/phase6c-ghostlock-patch-chain.mmd`
- `artifacts/phase6c/phase6c-ghostlock-patch-chain-20260804-01/`

The audit is host-only, refuses to overwrite existing output, and supports
`--dry-run`. No stock-device requeue-PI, paired waiter, race, panic, heap
shaping, kernel-memory operation or privilege payload was run.

## Phase 6D `/init` property/cmdline inventory

The preserved PS7331 `/init` was inventoried on the host. The scan recorded
162 literal marker occurrences and 111 mapped AArch64 ADRP/ADD references for
`/proc/cmdline`, `androidboot.*`, `ro.boot.*`, SELinux mode/policy names,
recovery/lock-state markers, and standard/rootable policy paths. Existing
windows locate the `androidboot.selinux`/`permissive` comparison candidate at
`0x41bd60`, rootable/standard path-builder candidates at `0x41ad00`/`0x41af80`,
and a common helper branch at `0x41be48`.

These results establish a policy-loader decision surface, not a shell-writable
root switch. Active policy identity, exact `w5` semantics and any legal early
boot selector remain **待驗證**. Boot-property injection, cmdline injection,
bootloader/fastboot selection and policy mutation remain rejected.

Outputs:

- `tools/scripts/inventory_phase6d_init_properties.py`
- `findings/phase-6d-init-property-inventory.md`
- `findings/phase-6d-init-property-evidence-index.md`
- `output/call-graphs/phase6d-init-policy-loader.mmd`
- `artifacts/phase6d/phase6d-init-property-inventory-20260804-01/`

The inventory is host-only, refuses to overwrite existing output, and supports
`--dry-run`.

## Phase 6C.5 GPL source scope verification

The PS7331 GPL package was audited without building or executing source. It
contains the MT8183 4.4 kernel sources, including `kernel/futex.c` and
`kernel/locking/rtmutex.c`, but does not contain `platform/system/core/init`,
`selinux.cpp`, or `selinux.h`. SELinux-named files found elsewhere are recorded
as kernel or external headers, not treated as `/init` source.

Outputs:

- `tools/scripts/audit_phase6c5_gpl_source_scope.py`
- `findings/phase-6c5-gpl-source-scope.md`
- `findings/phase-6c5-gpl-source-scope-evidence-index.md`
- `artifacts/phase6c5/gpl-source-scope-20260804-01/`

## Phase 6D `/init` AOSP anchor and pipeline map

Official AOSP Android 9 `system/core/init` anchor files for r1 and r61 are
preserved under `aosp/android-9/init-source-20260804-01/`. A host-only
comparison maps the AOSP `StatusFromCmdline`,
`FindPrecompiledSplitPolicy`, `LoadSplitPolicy`, `LoadPolicy`, and
`SelinuxInitialize` anchors to conservative candidate regions in the stripped
PS7331 `/init`. The binary regions are explicitly marked as unresolved where
symbols or an Amazon source tree are unavailable; the map is not a claim that
the rootable policy is active.

Outputs:

- `tools/scripts/fetch_aosp9_init_baseline.sh`
- `tools/scripts/analyze_phase6d_init_pipeline.py`
- `findings/phase-6d-init-pipeline-differential.md`
- `findings/phase-6d-init-pipeline-evidence-index.md`
- `aosp/android-9/init-source-20260804-01/`
- `artifacts/phase6d/phase6d-init-pipeline-diff-20260804-01/`
- `output/call-graphs/phase6d-init-pipeline-knowledge-base.mmd`

The analysis is host-only: it does not execute `/init`, inject boot
properties, load alternate SELinux policy, remount partitions, use fastboot,
trigger a kernel race/panic, access kernel memory, or generate a root payload.

## Phase 6D active-policy visibility capture

`tools/scripts/capture_phase6d_active_policy_readonly.sh` records a new output
directory per serial. The PS7331 capture `adb/phase6d/PHASE6D-ACTIVE-POLICY-RO-20260804-03/`
confirms Fire OS 7.3.3.1, Android API 28, kernel 4.4.146+, enforcing mode,
green/locked boot state, and visible standard/rootable CIL files. Shell access
to the live SELinux policy blob and kernel cmdline remains denied, so active
policy identity is not overstated.

## Phase 6D `/init` policy-loader scenario classification

The four proposed `/init` scenarios were classified from host-only evidence.
The strongest current result is a boot-time selector hypothesis: the stripped
binary has an `androidboot.selinux`/`permissive` parser candidate and separate
standard/rootable path-builder call sites. AVB/BoringSSL markers are present,
but no current CFG evidence connects them to the rootable branch. Rootable
paths are code-referenced, so a strings-only dead-code explanation is not
sufficient; runtime reachability remains unresolved.

Outputs:

- `tools/scripts/classify_phase6d_policy_loader_scenarios.py`
- `findings/phase-6d-policy-loader-scenarios.md`
- `findings/phase-6d-policy-loader-scenario-evidence-index.md`
- `artifacts/phase6d/phase6d-policy-scenarios-20260804-01/`
- `tools/scripts/analyze_phase6d_init_branch_window.py`
- `findings/phase-6d-init-branch-window.md`
- `output/call-graphs/phase6d-init-branch-window.mmd`
- `artifacts/phase6d/phase6d-init-branch-window-20260804-02/`

The extended conservative CFG parser produces 423 blocks and 663 explicit
branch/fall-through edges for the selected loader window. It confirms the
the `0x41be48` `w5` branch (terminator of conservative block `B41bdf4`) to
`0x41c30c` and its `0x41be4c` fall-through, while
keeping the high-level policy meaning unresolved.

Outputs:

- `tools/scripts/recover_phase6d_init_cfg.py`
- `findings/phase-6d-init-cfg.md`
- `output/call-graphs/phase6d-init-cfg.mmd`
- `artifacts/phase6d/phase6d-init-cfg-20260804-03/`

The classifier is host-only, refuses to overwrite output, and supports
`--dry-run`. It does not execute `/init`, inject boot properties, select
alternate policy, bypass AVB, remount partitions, or create a root payload.

## Phase 6E selected CVE surface audit

The preserved PS7331 source/config review narrows several unrelated CVE
surfaces: AF_ALG AEAD is disabled and its source file is absent; the described
AF_UNIX OOB path is not present in this 4.4 source shape; and the reviewed
MediaTek display/Bluetooth records do not establish MT8183 applicability.
These are reachability results, not claims that the kernel is vulnerability
free.

Outputs:

- `tools/scripts/audit_phase6e_cve_surface.py`
- `findings/phase-6e-cve-surface.md`
- `findings/phase-6e-cve-surface-evidence-index.md`
- `artifacts/phase6e/phase6e-cve-surface-20260804-01/`

## Phase 6F Binder static surface

The local Binder tree contains the expected validation/transaction function
family, but `binder_transaction_buffer_release()` has the older 4.4 vendor
signature (`failed_at` pointer) rather than the later Android common shape with
`binder_thread`, value-form `failed_at`, and `is_failure`. This is a version
difference and does not prove CVE-2023-20938 affectedness or exploitability.

Outputs:

- `tools/scripts/audit_phase6f_binder_cve_surface.py`
- `findings/phase-6f-binder-cve-2023-20938-static.md`
- `artifacts/phase6f/phase6f-binder-cve-20260804-01/`
- `output/call-graphs/phase6f-binder-static.mmd`

## Phase 6G MTK CMDQ static surface

The PS7331 source/config confirms `CONFIG_MTK_CMDQ=y`, `CONFIG_MTK_CMDQ_TAB=y`,
the `mtk_cmdq` device registration, v3 ioctl dispatch and user-copy/readback
paths. This is a sensitive control surface, not a confirmed CVE-2020-0069
finding. New device-node/ioctl, DMA, crash, kernel-memory and root tests remain
rejected.

Outputs:

- `tools/scripts/audit_phase6g_cmdq_surface.py`
- `findings/phase-6g-cmdq-static-surface.md`
- `artifacts/phase6g/phase6g-cmdq-static-20260804-02/`
- `output/call-graphs/phase6g-cmdq-static.mmd`
