# Phase 6BJ evidence index

## PH6BJ-STATIC-001

- **Source:** Host-only DEX disassembly caller closure scan
- **File:** `artifacts/phase6bj/binder-caller-closure-20260805-01/caller-map.csv`
- **SHA-256:** `ff9f4e43a0deb572dacc8c16fde35041e44dcad5ca5aecf079a8fafd36bd7689`
- **Input SHA-256:** `fosservices=ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`; `services=373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`; `boot-fosframework=fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`; `ota-PS7331=04d68d0bb562a14e9cbff3bdce63b66eb911ee4bb7e728ca77cd435a5b03c146`
- **Timestamp:** 2026-08-05T06:09:45Z (UTC)
- **Command:** `python3 tools/scripts/audit_phase6bj_binder_caller_closure.py --source ... --output artifacts/phase6bj/binder-caller-closure-20260805-01`
- **Observed result:** 19 invoke instructions across five target methods; no device contact and no Binder transaction.
- **Interpretation:** Establishes static caller/wrapper locations only; does not prove runtime reachability.
- **Confidence:** Confirmed
- **Related hypothesis:** Amazon private Binder methods may provide a launcher-control path.

## PH6BJ-STATIC-002

- **Source:** `AmazonUserManagerService.BinderService.enableKftLauncherComponent`
- **File:** `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325`
- **SHA-256:** `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- **Observed result:** Enables `com.amazon.tahoe.launcher.FreeTimeLauncherActivity`; sets `com.amazon.firelauncher` and `com.android.launcher3` to state 2 for the supplied `UserInfo.id`.
- **Interpretation:** Amazon has an explicit KFT child-user launcher state mutation.
- **Confidence:** Confirmed
- **Related hypothesis:** KFT may explain Fire Launcher protection in child profiles.

## PH6BJ-STATIC-003

- **Source:** `tryEnableKftLauncherComponent` and `enableKftLauncher`
- **File:** `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54371-54404`
- **SHA-256:** `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- **Observed result:** Internal methods gate the KFT component operation on KFT launcher existence/device path and call the component-state helper; `enableKftLauncher` then proceeds into profile-owner/empowerment work.
- **Interpretation:** The path is an Amazon user-management lifecycle path, not a generic HOME setter.
- **Confidence:** Strong evidence
- **Related hypothesis:** A shell caller could directly replay KFT state mutation.

## PH6BJ-STATIC-004

- **Source:** `AmazonInputManagerService.BinderService.registerKeyEventInterceptor`
- **File:** `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:19829-20000`
- **SHA-256:** `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- **Observed result:** Checks `GET_KEYEVENTS`, obtains `Binder.getCallingUid()`, resolves packages, checks an internal package whitelist and foreground package, then checks key whitelist/duplicate state.
- **Interpretation:** The method has multiple caller gates and is not a formal HOME resolver mutation.
- **Confidence:** Confirmed
- **Related hypothesis:** Input interception could replace the HOME resolver.

## PH6BJ-STATIC-005

- **Source:** `AmazonWindowManagerService.BinderService.setPipVisibility`
- **File:** `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:56150` and offset `044926-044930`
- **SHA-256:** `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- **Observed result:** Writes only the service's PIP state field.
- **Interpretation:** No HOME component or package state mutation is present in the method.
- **Confidence:** Confirmed
- **Related hypothesis:** Amazon WindowManager private API may force Fire Launcher.

## PH6BJ-RT-001

- **Source:** Read-only PS7331 service visibility capture
- **File:** `adb/phase6bj/PHASE6BJ-READONLY-20260805-01/metadata.json`
- **SHA-256:** See the directory `sha256sums.txt`; metadata SHA-256 is recorded there.
- **Test ID:** `PHASE6BJ-READONLY-20260805-01`
- **Serial:** `G001LT0511550CFT`
- **Timestamp:** 2026-08-05T06:10:59Z (UTC)
- **Command:** `tools/scripts/capture_phase6aq_service_visibility.py --serial G001LT0511550CFT --output adb/phase6bj/PHASE6BJ-READONLY-20260805-01`
- **Observed result:** Device is online; fingerprint is PS7331; shell is UID 2000 and SELinux is Enforcing. Target Amazon private names appear in `service list`, but each targeted `service check` returns `not found`.
- **Interpretation:** Name listing does not provide a shell-usable private Binder handle; no private method was invoked.
- **Confidence:** Confirmed
- **Related hypothesis:** Shell can call an Amazon private service by name.

## PH6BJ-SAFETY-001

- **Source:** Capture metadata and script safety declarations
- **File:** `adb/phase6bj/PHASE6BJ-READONLY-20260805-01/metadata.json`; `tools/scripts/capture_phase6aq_service_visibility.py`
- **Observed result:** `binder_transactions=false`, `package_state_changed=false`, `settings_changed=false`, `reboot_requested=false`, `private_service_methods_invoked=false`.
- **Interpretation:** Phase 6BJ live capture was read-only.
- **Confidence:** Confirmed
- **Related hypothesis:** The runtime verification could be performed without changing device state.
