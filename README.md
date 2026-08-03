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
