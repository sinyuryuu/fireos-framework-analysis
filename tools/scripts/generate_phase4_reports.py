#!/usr/bin/env python3
"""Generate the Phase 4 static-analysis reports from checked-in evidence.

No ADB call is made here.  The script only reads the local AOSP references,
decompiler output, and earlier Phase 3 evidence.  Device-derived claims are
kept at the confidence level justified by those inputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AOSP_R1 = ROOT / "aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java"
AOSP_R61 = ROOT / "aosp/android-9/android-9.0.0_r61/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java"
FIRE_PM = ROOT / "decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java"
FIRE_SUPERVISOR = ROOT / "decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java"
FOS = ROOT / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"
P3C_REPORT = ROOT / "findings/phase-3c-report.md"
P3C_INDEX = ROOT / "findings/phase-3c-evidence-index.md"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def line_of(path: Path, pattern: str) -> int | None:
    rx = re.compile(pattern)
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if rx.search(line):
            return number
    return None


def write(path: Path, content: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite {path}; pass --force")
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, header: list[str], rows: list[list[str]], force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite {path}; pass --force")
    with path.open("w", encoding="utf-8", newline="") as stream:
        out = csv.writer(stream, lineterminator="\n")
        out.writerow(header)
        out.writerows(rows)


def make_phase4a(force: bool) -> None:
    write_csv(
        ROOT / "output/tables/aosp9-home-decision-order.csv",
        ["order", "decision", "AOSP reference", "Fire reference", "meaning", "confidence"],
        [
            ["1", "query result size", "PMS.chooseBestActivity():6149-6155", "PMS.chooseBestActivity():3120-3125", "zero/one candidate returns without preferred lookup", "已證實"],
            ["2", "sort result set", "ActivityIntentResolver / mResolvePrioritySorter", "PackageManagerService.java:~385", "priority, preferredOrder, isDefault, match, system, package", "高可信推論"],
            ["3", "top-field comparison", "PMS.chooseBestActivity():6165-6170", "PMS.chooseBestActivity():3133-3135", "different priority/preferredOrder/isDefault returns query[0]", "已證實"],
            ["4", "persistent preferred", "PMS.findPersistentPreferredActivityLP():6247-6302", "PMS.findPersistentPreferredActivityLP():3197-3252", "exact target must be present in current query", "已證實"],
            ["5", "ordinary preferred", "PMS.findPreferredActivity():6306-6465", "PMS.findPreferredActivity():3288-~3500", "only reached after top-field tie; match and set validation apply", "已證實 / decompiler caveat"],
            ["6", "instant/resolver fallback", "PMS.chooseBestActivity():6179-6223", "PMS.chooseBestActivity():3135-3173", "fallback only after no preferred result", "已證實"],
            ["7", "priority normalization", "PMS.adjustPriority():12575-12596", "PMS.adjustPriority():8166-8175", "non-privileged positive priority is capped to zero", "已證實"],
        ],
        force,
    )

    write(
        ROOT / "output/call-graphs/aosp9-home-resolution.mmd",
        """flowchart TD
  Q[HOME intent] --> QIA[queryIntentActivitiesInternal]
  QIA --> SORT[mResolvePrioritySorter]
  SORT --> CBA[chooseBestActivity]
  CBA -->|N=1| ONE[return query[0]]
  CBA -->|top priority/preferredOrder/isDefault differ| TOP[return query[0]]
  CBA -->|top fields tie| PPA[findPersistentPreferredActivityLP]
  PPA -->|exact target in query| PP[return persistent preferred]
  PPA -->|no match| PA[findPreferredActivity]
  PA -->|match + mAlways + set valid| ORD[return ordinary preferred]
  PA -->|otherwise| RES[instant app / ResolverActivity fallback]
  ADJ[adjustPriority] -. registration-time cap .-> SORT
""",
        force,
    )

    rows = [
        ["chooseBestActivity", "6149-6227", "6150-6226", "3120-3180", "AOSP_STANDARD", "same top-field gate; Fire decompiler adds throws artifact", "P4A-METHOD-001"],
        ["findPersistentPreferredActivityLP", "6247-6302", "6247-6302", "3197-3252", "AOSP_STANDARD", "persistent record returns only when exact component is in query", "P4A-METHOD-002"],
        ["findPreferredActivity", "6306-6475", "6306-6475", "3288-~3500", "AOSP_STANDARD", "same visible match/mAlways/exact-component structure; Java output is mangled", "P4A-METHOD-003"],
        ["queryIntentActivitiesInternal", "6565-6635+", "6565-6635+", "3724-3729 hole", "UNKNOWN", "Fire JADX has an unsupported/decompiler gap; do not infer equality", "P4A-METHOD-004"],
        ["adjustPriority", "12575-12630+", "12575-12630+", "8166-8244", "AOSP_STANDARD", "same privileged/non-privileged cap and system-package matching shape", "P4A-METHOD-005"],
        ["ActivityIntentResolver.addActivity", "AOSP no vendor hook", "AOSP no vendor hook", "8246-8262", "AMAZON_ADDITION", "callFilterComponentIntent can omit an intent filter before resolver indexing", "P4A-METHOD-006"],
        ["ActivityStackSupervisor.resolveIntent", "standard PM-internal call", "standard PM-internal call", "745-772", "AMAZON_ADDITION", "vendor callback may return non-null before PM; selected implementation did not prove a Fire result", "P4A-METHOD-007"],
        ["Fire package literal in core chooser", "none", "none", "no literal in selected PMS chooser", "NOT_FOUND", "absence is bounded to inspected source, not proof of global absence", "P4A-METHOD-008"],
    ]
    write_csv(
        ROOT / "output/tables/phase-4a-method-diff.csv",
        ["method", "AOSP r1", "AOSP r61", "Fire OS", "classification", "observation", "evidence"],
        rows,
        force,
    )
    write(
        ROOT / "output/call-graphs/fireos-home-resolution.mmd",
        """flowchart TD
  HK[Home key / explicit HOME] --> ASS[ActivityStackSupervisor.resolveIntent]
  ASS --> VRES{VendorActivityStackSupervisorCallback.callResolveIntent}
  VRES -->|non-null: not proven| VRETURN[callback result]
  VRES -->|null| PMI[PackageManagerInternal.resolveIntent]
  PMI --> QIA[queryIntentActivitiesInternal]
  QIA --> VFILTER{VendorPackageManagerCallback.callFilterComponentIntent at addActivity}
  VFILTER -->|false| INDEX[resolver index contains filter]
  VFILTER -->|true: callback return not observed| DROP[filter omitted]
  INDEX --> CBA[chooseBestActivity]
  CBA -->|priority 50 vs priority 0| FIRE[Fire Launcher]
  CBA -->|tie only| PREF[persistent / ordinary preferred lookup]
""",
        force,
    )

    write(
        ROOT / "findings/phase-4a-aosp-home-resolution-model.md",
        f"""# Phase 4A — AOSP Android 9 HOME resolution model

## Scope

This report is generated from the checked-in AOSP `android-9.0.0_r1` and
`android-9.0.0_r61` sources. The model in
`tools/scripts/model_aosp9_home_resolution.py` implements the decision points
that determine whether an ordinary preferred record can be used. It is not a
replacement for the framework.

## Decision order

1. `queryIntentActivitiesInternal()` produces the candidate set and applies
   visibility, user, component and direct-boot filters (`{AOSP_R1.relative_to(ROOT)}:6565-6635+`).
2. Resolver sorting compares `priority`, `preferredOrder`, `isDefault`,
   `match`, `system`, then package name (`{AOSP_R1.relative_to(ROOT)}:13500-13535`).
3. `chooseBestActivity()` returns the only result immediately. With multiple
   results it compares only the first two candidates' `priority`,
   `preferredOrder`, and `isDefault` (`{AOSP_R1.relative_to(ROOT)}:6149-6170`).
4. If any of those three fields differs, `query.get(0)` wins and the ordinary
   preferred lookup is not called.
5. If they tie, `findPreferredActivity()` first checks persistent preferred
   activities and then ordinary preferred activities
   (`{AOSP_R1.relative_to(ROOT)}:6172-6177`, `6247-6302`, `6306-6323`).
6. An ordinary record must have the current best match category, satisfy the
   `mAlways` requirement, point to an exact current candidate, and pass the
   saved component-set check (`6306-6465`). A changed result set can cause an
   always record to be dropped and re-added as a last-chosen (`6421-6458`).

## Meaning of mAlways

`mAlways=true` asks the preferred resolver to treat the record as a durable
preference when the chooser is in the tie path. It does not promote the
record's component above a different `priority`, `preferredOrder`, or
`isDefault` winner. A persistent preferred record is consulted first inside
`findPreferredActivity()`, but it is still required to resolve to an exact
component in the current query (`6247-6302`).

## Priority normalization

`adjustPriority()` caps a positive priority from a non-privileged application
to zero (`{AOSP_R1.relative_to(ROOT)}:12575-12596`). This explains the Phase 3A
effective priority of zero for sideloaded launchers. Fire's privileged system
package retains its manifest priority 50 in the captured device state.

## Replayed scenario

The model input is Fire priority 50 plus a priority-0 third-party candidate with
an exact `mAlways=true` preferred record. The expected and modeled result is
Fire, because the priority difference returns `query[0]` before preferred lookup.
The unit test also proves the control case: an ordinary preferred record wins
when the ranking fields are genuinely tied.

Evidence: `P4A-MODEL-001`, `P3C-PREF-001`, `P3C-REBOOT-001`.
""",
        force,
    )

    write(
        ROOT / "findings/phase-4a-fireos-resolver-method-diff.md",
        f"""# Phase 4A — Fire OS resolver method diff

## Method-level result

The selected Fire OS PackageManagerService methods are AOSP-shaped for the
central chooser. The Fire Java output is partly decompiler-generated; where a
method contains an unsupported/dead block, the report leaves the conclusion
bounded instead of filling in missing logic.

| Method | Fire location | AOSP comparison | Classification |
|---|---|---|---|
| `chooseBestActivity` | `decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java:3120-3180` | r1 `6149-6227`; r61 corresponding method | `AOSP_STANDARD` |
| `findPersistentPreferredActivityLP` | same file `3197-3252` | r1 `6247-6302` | `AOSP_STANDARD` |
| `findPreferredActivity` | same file `3288-~3500` | r1 `6306-6475` | `AOSP_STANDARD` for visible branches; Java decompiler caveat |
| `queryIntentActivitiesInternal` | same file `3724-3729` has unsupported block | r1 `6565-6635+` | `UNKNOWN` for the missing block |
| `adjustPriority` | same file `8166-8244` | r1 `12575-12630+` | `AOSP_STANDARD` shape |
| `ActivityIntentResolver.addActivity` | same file `8246-8262` | no AOSP vendor callback | `AMAZON_ADDITION` |
| `ActivityStackSupervisor.resolveIntent` | `decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java:745-772` | AOSP PM-internal call path | `AMAZON_ADDITION` |

## Important Amazon boundaries

`addActivity()` calls `VendorPackageManagerCallback.callFilterComponentIntent`
before adding an activity filter to the resolver index
(`PackageManagerService.java:8259-8261`). A `true` callback return would omit
that filter. No checked-in dynamic evidence identifies a HOME-specific return
value, and no Fire Launcher-specific branch was found in the selected chooser
body. This is therefore an Amazon candidate-filtering surface, not proof of a
Fire override.

`ActivityStackSupervisor.resolveIntent()` calls
`VendorActivityStackSupervisorCallback.callResolveIntent()` before the normal
PackageManagerInternal resolver (`ActivityStackSupervisor.java:745-772`). A
non-null return would short-circuit the normal path. The inspected callback
implementation and Phase 3 event evidence do not establish a non-null Fire
result.

## Hard-coded package search boundary

The selected core `PackageManagerService` chooser and `adjustPriority` regions
contain no literal `com.amazon.firelauncher`. That is strong negative evidence
for a direct package-name branch in those methods only. Amazon private services
do contain Fire package references in lifecycle and KFT/free-time paths; those
are catalogued in `findings/phase-4b-amazon-callback-control-surface.md` and do
not, by themselves, prove current main-user HOME selection.

Evidence: `P4A-METHOD-001` through `P4A-METHOD-008`, `P3C-CALLBACK-001`.
""",
        force,
    )

    write(
        ROOT / "findings/phase-4a-h1-verdict.md",
        """# Phase 4A H1 verdict

## 判定：已證實（resolver ordering）；高可信推論（本機實際 candidate set 的完整重播）

H1 的核心語句由 AOSP Android 9 原始碼直接證實：
`chooseBestActivity()` 在 ordinary preferred lookup 之前先比較前兩名候選的
`priority`、`preferredOrder`、`isDefault`；任一不同即返回排序後的第一名。

以 Fire priority 50、第三方 priority 0、第三方 `mAlways=true` preferred
record 的輸入重播時，離線模型選 Fire，且標示
`preferred_considered=false`。Phase 3C 的實機結果亦完全相同：p0 record
寫入並跨重啟保存，但 resolver、Home key、explicit HOME 與 foreground 仍是
Fire。

尚缺的直接證據是當時 system_server 內部完整 `ResolveInfo` list 的逐項
序列化 trace；現有 `cmd package query-activities`、resolver 結果、AOSP
方法與事件快照足以把 H1 標為已證實，但不把未取得的內部 trace 假裝存在。

Evidence: `P4A-MODEL-001`, `P3C-PREF-001`, `P3C-REBOOT-001`,
`P3C-LOGCAT-001`.
""",
        force,
    )
    write(
        ROOT / "findings/phase-4a-h2-verdict.md",
        """# Phase 4A H2 verdict

## 判定：高可信推論（核心 chooser）；待驗證（Amazon callback/filter return）

在已比對的 `PackageManagerService` chooser、preferred lookup 與 priority
normalization 內，Fire OS 與 AOSP Android 9 的可見控制流等價；沒有找到
`com.amazon.firelauncher` 硬編碼，也沒有看到 callback 回傳 Fire component。
這支持「主結果可由 AOSP-shaped resolver 加上 privileged Fire priority 50
解釋」的 H2 核心部分。

H2 不能被標成完整已證實，因 Fire OS 新增了兩個尚未以回傳值封閉的控制面：

* `VendorActivityStackSupervisorCallback.callResolveIntent()` 可在 PM 前
  回傳非 null 結果；現有證據沒有證明它在本 HOME 請求中如此做。
* `VendorPackageManagerCallback.callFilterComponentIntent()` 可在 resolver
  建索引時排除 filter；現有證據沒有證明它排除了哪個 HOME filter。

因此「沒有任何 Amazon 核心介入」是已排除過強的表述；「核心 chooser 的
Fire 勝出不需要 package-name 特判即可重現」則是高可信推論。

Evidence: `P4A-METHOD-001`–`P4A-METHOD-008`, `P3C-CALLBACK-001`,
`P3C-PREF-001`.
""",
        force,
    )
    write(
        ROOT / "findings/phase-4a-core-hypotheses-summary.md",
        """# Phase 4A core hypotheses summary

| Hypothesis | Verdict | Basis |
|---|---|---|
| H1: ranking fields are considered before ordinary preferred | 已證實 | AOSP r1/r61 source, Fire corresponding method, offline model, Phase 3C device result |
| H2: selected core resolver is AOSP-shaped and no core Fire package hardcode is needed | 高可信推論 | method comparison and model replay |
| H2 global form: no Amazon callback/filter can affect HOME | 待驗證 | Fire has pre-PM resolve callback and resolver-index filter callback |
| ordinary `mAlways=true` record can cross priority 50 vs 0 | 已排除 | exact Phase 3C write + resolver and reboot result |
| direct Fire package hardcode in inspected chooser | 已排除（bounded scope） | no literal in selected PackageManagerService chooser ranges |
| unknown callback return / candidate filtering behavior | 待驗證 | implementation result not available in checked-in evidence |
""",
        force,
    )


def make_phase4b(force: bool) -> None:
    alias_dir = ROOT / "adb/phase4/PHASE4-ALIAS-T04"
    alias_live = alias_dir.exists()
    rows = [
        ["priority", "PMS.adjustPriority; mResolvePrioritySorter", "manifest only; positive third-party value capped", "no safe shell API", "yes for privileged/system", "direct", "yes", "do not repeat priority matrix", "P3A/P4A"],
        ["preferredOrder", "mResolvePrioritySorter", "not exposed by ordinary APK manifest", "no justified shell control", "system/package parser", "tie ranking", "yes", "static only", "P4B-RANK-002"],
        ["match", "sorter + findPreferredActivity", "filter shape controls match, but HOME baseline match is already exact", "no direct safe shell control", "no", "candidate eligibility and preferred match", "yes", "alias/filter APK only", "P4A-METHOD-003"],
        ["isDefault", "sorter / query matching", "DEFAULT category can affect query result", "no direct shell control", "no", "top-field tie gate", "yes", "alias/filter APK", "P4B-RANK-004"],
        ["system/privileged", "sorter and adjustPriority", "not legally obtainable by sideloaded APK", "no", "yes", "priority retention and tie order", "n/a", "static only", "P3A-PRIORITY-001"],
        ["persistent preferred", "findPersistentPreferredActivityLP", "not writable by ordinary shell in observed public path", "DevicePolicy/provisioning risk", "owner/system path", "can override if exact candidate", "yes in theory", "static; no DPM", "P4A-METHOD-002"],
        ["ordinary preferred", "findPreferredActivity", "shell can write via set-home-activity", "yes", "no", "only tie path", "yes", "already tested; no repeat", "P3C-PREF-001"],
        ["last chosen", "setLastChosenActivity/getLastChosenActivity", "chooser history, not HOME priority winner", "command availability only", "no", "HOME likely bypassed by top-field difference", "yes", "static only", "P4B-RANK-008"],
        ["enabled state", "query filters / PM state", "test package only", "yes for test APK", "no", "candidate inclusion", "yes", "alias experiment", "P4B-RANK-009"],
        ["direct boot", "query flags and ActivityInfo", "manifest attribute", "no", "no", "pre-unlock candidate availability", "yes", "alias experiment", "P4B-RANK-010"],
        ["instant/domain verification", "chooseBestActivity fallback", "not applicable to local HOME APK", "no safe control", "system-managed", "post-preferred fallback", "yes", "static only", "P4A-METHOD-001"],
        ["package visibility/user", "queryIntentActivitiesInternal", "user/profile/context dependent", "read-only/user-scoped", "system policy", "candidate set", "yes", "read-only", "P4B-RANK-012"],
    ]
    write_csv(
        ROOT / "output/tables/phase-4b-ranking-factors.csv",
        ["factor", "AOSP location", "third-party control", "shell control", "system-only aspect", "HOME effect", "reversible", "test decision", "evidence"],
        rows,
        force,
    )
    write(
        ROOT / "findings/phase-4b-ranking-control-surface.md",
        """# Phase 4B — ranking control surface

The only ranking factor a normal sideloaded HOME APK can declare directly is
its intent-filter shape. Positive manifest priority is capped to zero by
`adjustPriority()` unless the package is privileged/system. `preferredOrder` is
not an ordinary application control, and the observed shell preferred API does
not change the top-field gate. `match` and `isDefault` can be explored with
filter composition, but they cannot make a priority-0 candidate cross a
priority-50 candidate when the first two ranking fields differ.

`persistent preferred` is a separate, stronger state source in the code, but a
normal shell user cannot safely create a device-policy persistent preference on
this device without entering provisioning/Device Owner territory. That route is
therefore static-only and marked **因風險拒絕測試**.

`last chosen` is a chooser-history mechanism in AOSP (`setLastChosenActivity()`
and `getLastChosenActivity()`), not a documented HOME replacement mechanism.
The Android 9 HOME chooser's top-field branch returns before ordinary preferred
lookup, so it is not a credible bypass for Fire priority 50.

See `output/tables/phase-4b-ranking-factors.csv` for the complete factor-by-factor
matrix and exact experiment decisions.
""",
        force,
    )
    write_csv(
        ROOT / "output/tables/phase-4b-alias-filter-matrix.csv",
        ["candidate", "filter_shape", "effective_priority", "is_default", "query_inclusion", "explicit_start", "implicit_home", "home_key", "rollback", "evidence"],
        [
            ["HomeActivity", "MAIN + HOME + DEFAULT", "0", "true", "yes", "ok", "Fire", "Fire", "test APK removed", "P4B-ALIAS-001"],
            ["HomeAliasDefault", "alias MAIN + HOME + DEFAULT", "0", "true", "yes", "delivered to target", "Fire", "Fire", "test APK removed", "P4B-ALIAS-001"],
            ["HomeAliasHomeOnly", "alias MAIN + HOME", "0", "false", "yes in query output", "delivered to target", "Fire", "Fire", "test APK removed", "P4B-ALIAS-001"],
            ["DirectBootHomeActivity", "MAIN + HOME + DEFAULT + directBootAware", "0", "true", "yes", "ok", "Fire", "Fire", "test APK removed", "P4B-ALIAS-001"],
            ["SpecificHomeActivity", "MAIN + HOME + DEFAULT + data scheme", "0", "true", "no for data-less HOME", "ok explicit", "Fire", "Fire", "test APK removed", "P4B-ALIAS-001"],
            ["SecondaryHomeActivity", "MAIN + SECONDARY_HOME", "n/a", "n/a", "no ordinary HOME", "ok explicit", "Fire", "Fire", "test APK removed", "P4B-ALIAS-001"],
        ],
        force,
    )
    write(
        ROOT / "findings/phase-4b-alias-and-filter-results.md",
        """# Phase 4B — multi-activity alias and filter result

## Test boundary

`PHASE4-ALIAS-T04` installed one APK only:
`org.fireosresearch.phase4.alias`. It did not call `set-home-activity`, did not
modify settings, did not change Fire Launcher state, and did not reboot. The
raw before/installed/after snapshots, explicit start output, logcat, and
rollback SHA-256 are under `adb/phase4/PHASE4-ALIAS-T04/`.

## Device result — 已證實

The installed package contributed four ordinary HOME query entries: the direct
activity, the DEFAULT alias, the HOME-only alias, and the direct-boot activity.
All had effective priority 0; the HOME-only alias was marked `isDefault=false`.
The data-specific filter was not a data-less ordinary HOME candidate, and the
`SECONDARY_HOME` activity was not in the ordinary HOME query. Every declared
component was explicitly startable; the two aliases delivered to the target
activity because it is `singleTask`.

With all these candidates present, implicit MAIN+HOME resolved to
`com.amazon.firelauncher/.Launcher`, and `input keyevent 3` returned to Fire.
After `pm uninstall --user 0 org.fireosresearch.phase4.alias`, the package path
was absent and the resolver again returned Fire. No test APK remained installed.

## Interpretation

Alias multiplicity, direct-boot awareness, DEFAULT omission, a data-specific
filter, and a secondary HOME category did not form a legal priority-0 path to
replace the privileged priority-50 Fire candidate. This supports the ranking
model, but it does not test persistent preferred or alternate profile policy.

Evidence: `P4B-ALIAS-001`, `P4B-ALIAS-ROLLBACK-001`.
""",
        force,
    )
    write(
        ROOT / "findings/phase-4b-alternate-home-surfaces.md",
        """# Phase 4B — alternate HOME surfaces

## Static/read-only result

Android 9 contains the normal HOME start path (`startHomeActivityLocked()` and
`startHomeOnAllDisplays()` in the ActivityManager side), while the selected
Fire artifacts expose Amazon callback boundaries around resolution and Home
key policy. The repository's prior role/device_config probe found no usable
HOME role holder or device_config command on this build (`P3C-ROLE-001`).

No evidence in the selected Fire OS artifacts shows a user-level alternate
HOME that would replace the main HOME resolver without Device Owner, managed
profile policy, system UID, or a privileged package.

`CATEGORY_SECONDARY_HOME`, display-specific HOME, dock/car HOME, dream exit,
and lock-task/kiosk are **待驗證** only where the local artifact lacks a full
class/method implementation. Creating Device Owner or provisioning a managed
profile is **因風險拒絕測試** because reversal can require a factory reset.

No alternate HOME APK was installed in this phase; the Phase 4 alias APK is a
candidate-composition control and is not advertised as a secondary HOME.
""",
        force,
    )
    write(
        ROOT / "findings/phase-4b-last-chosen-and-fallback.md",
        """# Phase 4B — last-chosen and fallback boundary

AOSP Android 9 includes `setLastChosenActivity()` and
`getLastChosenActivity()` (`PackageManagerService.java:6025-6057`) and converts
an invalid always record to a last-chosen record when the saved candidate set
is no longer valid (`findPreferredActivity():6421-6458`). This is distinct from
the priority gate in `chooseBestActivity():6165-6175`.

The existing Fire evidence has an ordinary `mAlways=true` record that persists,
but Fire remains the resolver result. That is consistent with last-chosen and
ordinary preferred state being below a priority difference. A new shell history
mutation was not justified because the device did not expose a documented safe
HOME-specific last-chosen setter and Phase 3C already established the relevant
ordinary preferred behavior.

Controlled failure candidates were not made effective: making a priority-0
test candidate the real HOME would require changing or bypassing the Fire
candidate, which is outside the safety boundary. Deliberately inducing a
system-level HOME crash/fallback is **因風險拒絕測試**. Test-APK failure modes
remain available as source-only controls for future work.
""",
        force,
    )
    write(
        ROOT / "findings/phase-4b-existing-workaround-analysis.md",
        """# Phase 4B — existing workaround families

This phase records design patterns without installing unverified binaries.

| Family | Typical API shape | Fire Launcher mutation required | Assessment |
|---|---|---:|---|
| Fire Toolbox / LauncherHijack-era tools | monitor current task and start explicit third-party launcher | historically often yes or accessibility | version- and build-dependent; inspect source before use |
| Launcher manager / package-state tools | `set-home-activity`, disable/hide, protected package operations | often yes | ordinary preferred path is disproved on this build |
| Accessibility redirect | user-enabled `AccessibilityService`, observe window changes, explicit start | no | closest reversible approximation; requires consent and may flash/lag |
| UsageStats observer | foreground observation then explicit start | no | weaker reliability and background limits |
| overlay/notification/quick tile | user-triggered explicit shortcut | no | stable entry point, not HOME replacement |

## Public-source review

### LauncherHijack (source reviewed; no binary installed)

The public [LauncherHijack repository](https://github.com/BaronKiko/LauncherHijack)
describes an Accessibility-based launcher redirection design and marks the
project deprecated. Its public [HELP.md](https://github.com/BaronKiko/LauncherHijack/blob/master/HELP.md)
documents manual Accessibility enablement and warns that a killed launcher
process can require a second Home press. It also documents an optional
"corrupt default launcher" path; that path is intentionally classified as
**因風險拒絕測試** here because it damages package state and may require a
new user or stronger recovery. No APK or binary from that repository was
installed, and its historical package-block assumptions were not applied to
this Fire OS build.

The design is relevant as a prior art comparison, not as proof of behavior on
KFTRWI. The local harness in `tools/phase4-accessibility/` is independently
source-built, has no network permission, does not automate consent, and is
only an explicit foreground redirect.

## Live device result — T03

After manual consent in Settings and a visible toggle, the corrected harness
ran 30 controlled cycles from `adb/phase4/PHASE4-ACCESSIBILITY-T03/`. Each
cycle sent `KEYCODE_HOME` while the test package was present. The service
logged 30 explicit redirect attempts, but the foreground snapshots recorded
`mResumedActivity=com.amazon.firelauncher/.Launcher` in all 30 cycles. The
alias appeared only as a task/last-paused record; it never became the resumed
or focused activity. Logcat includes the Android background-start boundary
`Activity start request ... stopped`.

Therefore this tested Accessibility implementation achieved **0/30 (0%)**
foreground redirects on the device. It is **已排除** as a reliable Home-key
workaround for this build and implementation, while the broader class of
user-consented accessibility designs remains **待驗證**. It did not alter the
HOME resolver. The service was manually disabled, both research APKs were
removed, and the final resolver/ADB checks passed; see
`adb/phase4/PHASE4-ACCESSIBILITY-T03/rollback-result-verified.md`.

No unknown APK or binary was installed. Any future public-project review must
record source URL, commit, permissions, digest, and whether it disables Fire
Launcher. A redirect must never be described as a true HOME replacement.
""",
        force,
    )
    write(
        ROOT / "findings/phase-4b-amazon-callback-control-surface.md",
        """# Phase 4B — Amazon callback control surface

## Confirmed static boundaries

| Boundary | Location | What it can do | Current conclusion |
|---|---|---|---|
| `VendorActivityStackSupervisorCallback.callResolveIntent` | `decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java:745-772` | return non-null before `PackageManagerInternal.resolveIntent` | **待驗證** whether current HOME returns Fire |
| `VendorPackageManagerCallback.callFilterComponentIntent` | `decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java:8246-8272` | omit a filter from resolver registration/removal | **待驗證** HOME-specific return |
| `AmazonUserManagerService$BinderService.enableKftLauncherComponent` | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54404` | hardcodes Tahoe FreeTime, Fire Launcher, and launcher3 in KFT/free-time component state calls | **高可信推論** profile-specific path, not proof of main-user HOME |
| `MigrationService.appsAvailable` | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:~33650` | broadcasts external-app availability to `com.amazon.firelauncher` | lifecycle notification, not resolver selection |
| `AppAdapterHandler.lambda$goHome$3` | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:~25745-26095` | starts implicit MAIN+HOME for a network issue path | no Fire component hardcode; standard HOME route |

The static artifacts do contain Amazon package references outside the core
chooser. Therefore the global statement “Amazon has no Fire package references”
is **已排除**. The narrower statement “the inspected core chooser does not
need a Fire package hardcode to produce the observed result” remains
**高可信推論**.

No unknown Binder transaction was called and no critical service was killed.
An exported/documented, shell-writable control point that changes the main HOME
component was not found.
""",
        force,
    )
    write(
        ROOT / "findings/phase-4b-assisted-workarounds.md",
        """# Phase 4B — assisted workaround assessment

## Candidate: user-consented Accessibility redirect

The proposed harness is source-only in this commit under
`tools/phase4-accessibility/` (or the documented Phase 4 test harness when
present). It must be manually enabled by the device owner, listens only for
`TYPE_WINDOW_STATE_CHANGED`, does not read window text or input, uses an
explicit Fire-package filter, cooldown, loop guard, visible stop control, and
starts a test launcher explicitly. It cannot change PackageManager's HOME
resolver.

## Classification after live measurement

* True HOME replacement: **否**.
* This implementation's Home-key workaround: **已排除** (0/30 foreground
  redirects).
* Unlock workaround: **待驗證**.
* Required authorization: user must enable Accessibility in Settings.
* Reboot persistence: **待驗證**; no reboot was run after the failed
  foreground-start result.
* Main observed failure boundary: background activity start was logged as
  stopped; the explicit target remained task history rather than resumed.
* Rollback: disable the service in Settings, uninstall the test APK, and verify
  Fire resolver/foreground; do not modify Fire Launcher.

The implementation was not auto-enabled and did not automate consent. The
manual consent and rollback were completed; no Fire package state was changed.
""",
        force,
    )
    write(
        ROOT / "findings/phase-4b-final-workaround-verdict.md",
        """# Phase 4B final workaround verdict

## 正式 HOME replacement

**未找到新的可證實方案。** The ordinary preferred record remains below the
priority-50 privileged candidate, and the multi-activity/alias control did not
change candidate ranking or Home key behavior. No Fire state mutation was used.

## Closest safe approximation

The tested Accessibility redirect is **not viable on this build**: it made
30 explicit attempts but achieved 0 foreground handoffs. A different
user-consented design might use a foreground-visible interaction or a
notification/Quick Settings action, but that would be an explicit shortcut,
not an automatic HOME replacement. UsageStats observation remains a weaker,
unmeasured candidate and should not be advertised as a solution.

Measured latency and flash rate were not claimed because the target never
became resumed. Reboot persistence was not tested after the failed handoff.

## Paths not worth repeating

Priority APK matrix, ordinary `set-home-activity` persistence, HOME role/
device_config availability, random settings/overlay writes, and Fire Launcher
state mutation are respectively **已排除**, **已排除**, **已確認不可用**,
**已拒絕**, and **因風險拒絕測試** under the unchanged build/caller conditions.
""",
        force,
    )
    write_csv(
        ROOT / "output/tables/phase-4b-workaround-comparison.csv",
        ["candidate", "true_HOME", "authorization", "latency", "flash", "battery", "reboot", "rollback", "status", "evidence"],
        [
            ["ordinary set-home-activity", "No", "shell", "none", "none", "none", "record persists but ineffective", "restore preferred + uninstall test APK", "已排除", "P3C-PREF-001"],
            ["priority elevation by sideload", "No", "none", "none", "none", "none", "not applicable", "uninstall APK", "已排除", "P3A-PRIORITY-001"],
            ["Accessibility foreground redirect (tested T03)", "No", "explicit user Accessibility enable", "target not resumed", "Fire remained foreground", "待測量", "not tested", "disable service + uninstall", "已排除 for this implementation (0/30)", "P4B-ACCESS-001"],
            ["UsageStats observer redirect", "No", "usage access", "待測量", "可能", "可能", "待驗證", "revoke access + uninstall", "Potentially viable", "P4B-WA-004"],
            ["Quick Settings/notification explicit entry", "No", "user action", "user-driven", "none", "low", "likely", "remove tile/notification + uninstall", "Viable as shortcut only", "P4B-WA-005"],
            ["Device Owner / persistent kiosk", "Policy HOME possible", "provisioning", "n/a", "n/a", "high risk", "not accepted", "may require factory reset", "因風險拒絕測試", "P4B-RISK-001"],
        ],
        force,
    )


def make_final(force: bool) -> None:
    write(
        ROOT / "findings/phase-4a-evidence-index.md",
        """# Phase 4A evidence index

## P4A-MODEL-001

- Source: `tools/scripts/model_aosp9_home_resolution.py` and unit tests
- File: `tests/test_aosp9_home_resolution.py`
- Command: `python3 -m unittest tests/test_aosp9_home_resolution.py`
- Observed: Fire priority 50 is selected before p0 ordinary preferred lookup;
  tie control selects the ordinary preferred target.
- Confidence: 已證實

## P4A-METHOD-001 … P4A-METHOD-008

- Source: AOSP r1/r61 and Fire decompiled method comparison
- Files: `output/tables/phase-4a-method-diff.csv`,
  `findings/phase-4a-fireos-resolver-method-diff.md`
- Observed: central chooser/preferred branches are AOSP-shaped; Fire adds
  resolver callback/filter boundaries; one query method has a decompiler gap.
- Confidence: 已證實 for source locations; 高可信推論 for equivalence; 待驗證 for callback return values.

## P4A-DEVICE-001

- Source: Phase 3C controlled p0 experiment
- Files: `adb/phase3c/PHASE3C-PREFERRED-P0-03/` and
  `findings/phase-3c-evidence-index.md`
- Observed: mAlways=true p0 preferred record persisted but Fire remained the
  resolver and foreground through Home, explicit HOME, lock/unlock and reboot.
- Confidence: 已證實
""",
        force,
    )
    write(
        ROOT / "findings/phase-4-evidence-index.md",
        """# Phase 4 evidence index

Phase 4 evidence is intentionally split into static, offline-model, and live
reversible experiment records.

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| P4A-MODEL-001 | offline AOSP model | `tools/scripts/model_aosp9_home_resolution.py`, `tests/test_aosp9_home_resolution.py` | priority 50 returns Fire before ordinary preferred; tie control uses preferred | 已證實 |
| P4A-METHOD-001–008 | AOSP/Fire method diff | `output/tables/phase-4a-method-diff.csv` | core chooser equivalent in visible branches; two Amazon callback boundaries | 已證實 / 待驗證 |
| P4A-DEVICE-001 | Phase 3C device evidence | `adb/phase3c/PHASE3C-PREFERRED-P0-03/` | preferred record persistence does not change Fire result | 已證實 |
| P4B-RANK-001 | ranking inventory | `output/tables/phase-4b-ranking-factors.csv` | only privileged/system path can retain positive priority | 高可信推論 |
| P4B-CALLBACK-001 | Amazon callback static scan | `findings/phase-4b-amazon-callback-control-surface.md` | callback can short-circuit or filter, but current return is unknown | 待驗證 |
| P4B-WA-001 | safety review | `findings/phase-4b-assisted-workarounds.md` | Accessibility redirect is approximation, not HOME replacement | 高可信推論 |
| P4B-ALIAS-001 | one reversible APK experiment | `adb/phase4/PHASE4-ALIAS-T04/` | aliases/filter composition left Fire resolver and Home key unchanged | 已證實 |
| P4B-ALIAS-ROLLBACK-001 | rollback snapshot | `adb/phase4/PHASE4-ALIAS-T04/after_rollback/`, `rollback-diff.md` | test package absent, resolver Fire, ADB device | 已證實 |
| P4B-ACCESS-001 | manual-consent Accessibility run | `adb/phase4/PHASE4-ACCESSIBILITY-T03/` | 30 explicit redirect attempts; 0/30 resumed/focused alias handoffs; Fire remained resumed | 已證實 |
| P4B-ACCESS-ROLLBACK-001 | manual disable and rollback | `adb/phase4/PHASE4-ACCESSIBILITY-T03/rollback-result-verified.md`, `after_rollback/` | service setting empty, test packages absent, resolver Fire, ADB device | 已證實 |
| P4B-RISK-001 | risk gate | `findings/phase-4-risk-register.md` | Device Owner, Fire state mutation, crash fallback rejected | 因風險拒絕測試 |

Live Phase 4B experiment IDs are added here by the controlled experiment
runner after each raw output directory is finalized. No generated summary
replaces the raw command output or SHA-256 manifest.
""",
        force,
    )
    write(
        ROOT / "findings/phase-4-risk-register.md",
        """# Phase 4 risk register

| Risk / operation | Decision | Reason | Recovery |
|---|---|---|---|
| disable/hide/suspend/uninstall/force-stop/clear Fire Launcher | 因風險拒絕測試 | explicit Phase 4 safety boundary; may remove the only usable HOME | not applicable; never executed |
| Device Owner / managed provisioning | 因風險拒絕測試 | may require factory reset to remove | no safe no-reset guarantee |
| core SystemUI/Settings/overlay mutation | 因風險拒絕測試 unless exact reversible target | may remove navigation/settings access | only static/read-only analysis |
| unknown Binder transaction | 因風險拒絕測試 | no verified descriptor/permission/rollback | none |
| controlled test APK install/remove | 允許 | non-core package, explicit serial, uninstall rollback | `pm uninstall --user 0 TEST_PACKAGE` |
| ordinary preferred write for a new test package | avoid repeat | Phase 3C already disproved it under unchanged conditions | restore saved Fire preferred record, uninstall test package |
| accessibility redirect | user-consent required | must be explicitly enabled by device owner; no auto-consent | disable service, uninstall APK |
| normal reboot | only after a proven safe mutation | must preserve baseline and wait for ADB/system ready | post-reboot snapshot and explicit rollback |
| deliberate HOME crash/fallback | 因風險拒絕測試 | could create no-HOME or crash loop | static analysis only |
""",
        force,
    )
    write(
        ROOT / "findings/phase-4-report.md",
        """# Phase 4 — core hypothesis validation and workaround exploration

## Executive summary

### 已證實

Android 9's central `chooseBestActivity()` compares the leading candidates'
`priority`, `preferredOrder`, and `isDefault` before ordinary preferred lookup.
Fire priority 50 therefore wins over a priority-0 third-party candidate in the
tested candidate shape. Phase 3C's mAlways=true record is stored and persistent,
but it does not cross that ranking gate.

### 高可信推論

The inspected Fire OS core chooser is AOSP-shaped and does not need a literal
`com.amazon.firelauncher` branch to reproduce the observed result. Fire OS does
add vendor callbacks before PM resolution and while indexing filters, so the
global claim that Amazon cannot influence HOME is too strong.

### 待驗證

The return value of `VendorActivityStackSupervisorCallback.callResolveIntent()`
for a real HOME request, and the HOME-specific return of
`VendorPackageManagerCallback.callFilterComponentIntent()`, remain unresolved.
No checked-in evidence shows either returning Fire for the main user.

### Workaround verdict

No new true HOME replacement was proven. The manually consented Accessibility
harness was measured on-device: it issued 30 explicit attempts but produced
0/30 foreground handoffs; Fire remained resumed and the target remained only
in task history. It is therefore **已排除** as a reliable workaround in this
implementation/build. Notification/Quick Settings or a different
user-consented foreground design remain explicit shortcuts, not HOME
replacement. Device Owner/kiosk and Fire package mutation are outside the
safety boundary.

## Phase 4A

See:

* `findings/phase-4a-aosp-home-resolution-model.md`
* `findings/phase-4a-fireos-resolver-method-diff.md`
* `findings/phase-4a-h1-verdict.md`
* `findings/phase-4a-h2-verdict.md`
* `output/tables/aosp9-home-decision-order.csv`
* `output/tables/phase-4a-method-diff.csv`

## Phase 4B

The ranking matrix, alternate HOME surfaces, callback inventory, workaround
comparison, and risk gates are in the files under `findings/phase-4b-*` and
`output/tables/phase-4b-*`. The multi-activity alias APK is a candidate-set
control; it does not mutate Fire Launcher or repeat the Phase 3A priority
matrix.

## Paths explicitly not pursued

Fire Launcher state mutation, Device Owner/provisioning, core overlays,
unknown Binder transactions, and deliberate crash/fallback tests are **因風險拒絕測試**.
Ordinary set-home persistence and sideload priority cap are **已排除** from
further repetition under unchanged conditions.

## Remaining research value

The single highest-value static/dynamic follow-up is to obtain an instrumented
or verbose trace that records whether the two Amazon callbacks return non-null
or filter the Fire/third-party HOME filters. If that evidence remains
unavailable, the project can reasonably close the formal HOME-replacement
question as “not available through tested shell-writable state; only a
privileged/system or policy-controlled path remains plausible.” The tested
Accessibility redirect should remain documented as a failed approximation,
not a recommended workaround.
""",
        force,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print("Would generate Phase 4A/4B reports, tables, graphs, and evidence indexes.")
        return 0
    for path in (AOSP_R1, AOSP_R61, FIRE_PM, FIRE_SUPERVISOR, FOS, P3C_REPORT, P3C_INDEX):
        if not path.exists():
            raise SystemExit(f"required input missing: {path}")
    make_phase4a(args.force)
    make_phase4b(args.force)
    make_final(args.force)
    print("Generated Phase 4 static reports.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
