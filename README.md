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
