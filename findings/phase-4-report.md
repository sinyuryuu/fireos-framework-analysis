# Phase 4 — core hypothesis validation and workaround exploration

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
