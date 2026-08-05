#!/usr/bin/env python3
"""Audit Amazon user/profile Binder paths that mention launcher state.

This is a host-only, source-backed audit.  It reads preserved PS7331 VDEX
disassembly and preserved read-only service/SELinux captures.  It never
contacts ADB, looks up a Binder handle, sends a transaction, changes package
state, changes a user/profile, or replays an OTA/OOBE broadcast.

The important distinction in this audit is between:

* a Binder method whose implementation has a high-impact launcher side
  effect; and
* a shell-reachable method on the production device.

The former is static evidence.  The latter requires an allowed service lookup
and is not inferred from the former.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FOS_REL = Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log")
BOOT_REL = Path("decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log")
SERVICE_REL = Path(
    "artifacts/phase6j/phase6j-service-visibility-20260805-01/service_list.stdout.txt"
)
AVC_REL = Path(
    "artifacts/phase6j/phase6j-service-visibility-20260805-01/filtered_avc.matches.txt"
)
FOS_SHA256 = "ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c"

CSV_FIELDS = [
    "evidence_id",
    "surface",
    "symbol",
    "source_file",
    "source_lines",
    "source_sha256",
    "entry_or_call",
    "authorization_or_gate",
    "state_effect",
    "home_relation",
    "live_observation",
    "classification",
    "confidence",
    "conclusion",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, value: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def source_line(path: Path, needle: str) -> int | None:
    for number, line in enumerate(read(path).splitlines(), 1):
        if needle in line:
            return number
    return None


def lines_containing(path: Path, needle: str) -> list[int]:
    return [number for number, line in enumerate(read(path).splitlines(), 1) if needle in line]


def line_range(path: Path, start: int, end: int) -> str:
    lines = read(path).splitlines()
    return "\n".join(f"{number:06d}: {lines[number - 1]}" for number in range(start, end + 1)) + "\n"


def method_block(path: Path, heading: str, next_heading: str | None = None) -> tuple[int, int, str]:
    lines = read(path).splitlines()
    start = next((i for i, line in enumerate(lines, 1) if heading in line), None)
    if start is None:
        raise RuntimeError(f"{path}: missing method heading {heading!r}")
    if next_heading:
        end = next((i for i in range(start + 1, len(lines) + 1) if next_heading in lines[i - 1]), len(lines)) - 1
    else:
        end = next((i for i in range(start + 1, len(lines) + 1) if lines[i - 1].startswith("   ") and "method #" in lines[i - 1]), len(lines)) - 1
    return start, end, line_range(path, start, end)


def row(**values: str) -> dict[str, str]:
    result = {field: "" for field in CSV_FIELDS}
    result.update(values)
    return result


def load_inputs() -> dict[Path, str]:
    paths = [FOS_REL, BOOT_REL, SERVICE_REL, AVC_REL]
    missing = [str(ROOT / path) for path in paths if not (ROOT / path).is_file()]
    if missing:
        raise FileNotFoundError("missing input(s): " + ", ".join(missing))
    return {path: read(ROOT / path) for path in paths}


def assert_markers(inputs: dict[Path, str]) -> None:
    fos = inputs[FOS_REL]
    boot = inputs[BOOT_REL]
    required_fos = [
        "class #441: AmazonUserManagerService",
        "direct_method #5652: checkManageUsersPermission",
        "direct_method #5655: getSystemServiceName",
        "virtual_method #5624: enableKftLauncher",
        "direct_method #5625: enableKftLauncherComponent",
        "direct_method #5634: tryEnableKftLauncherComponent",
        'const-string v1, "com.amazon.firelauncher"',
        'const-string v1, "com.android.launcher3"',
        "virtual_method #5657: onBootPhase",
        "virtual_method #5658: onStart",
        "class #567: AmazonProfileService.BinderService",
        "virtual_method #6514: initiateLauncher",
        "direct_method #6671: enforceProfileInteractionPermissions",
        'const-string v0, "amazonprofileservice"',
    ]
    required_boot = [
        "class #144: IAmazonUserManager",
        "class #2136: IAmazonUserManager.Stub",
        "virtual_method #1424: onTransact",
        "virtual_method #1410: enableKftLauncher",
        "const-string v2, \"amazon.os.IAmazonUserManager\"",
        "const/4 v5, #int 3",
    ]
    for marker in required_fos:
        if marker not in fos:
            raise RuntimeError(f"{FOS_REL}: missing expected marker {marker!r}")
    for marker in required_boot:
        if marker not in boot:
            raise RuntimeError(f"{BOOT_REL}: missing expected marker {marker!r}")


def build_rows(inputs: dict[Path, str]) -> list[dict[str, str]]:
    fos = ROOT / FOS_REL
    boot = ROOT / BOOT_REL
    services = inputs[SERVICE_REL]
    avc = inputs[AVC_REL]
    service_listed = "amazonusermanagerservice" in services
    profile_listed = "amazonprofileservice" in services
    user_find_denied = "service=amazonusermanagerservice" in avc and "uid=2000" in avc and "{ find }" in avc
    profile_find_denied = "service=amazonprofileservice" in avc and "uid=2000" in avc and "{ find }" in avc
    fos_hash = sha256(fos)
    boot_hash = sha256(boot)

    user_start = source_line(fos, "class #441: AmazonUserManagerService")
    user_on_start = source_line(fos, "virtual_method #5658: onStart")
    user_on_boot = source_line(fos, "virtual_method #5657: onBootPhase")
    user_service_name = source_line(fos, "direct_method #5655: getSystemServiceName")
    check_users = source_line(fos, "direct_method #5652: checkManageUsersPermission")
    enable_kft = source_line(fos, "virtual_method #5624: enableKftLauncher")
    enable_component = source_line(fos, "direct_method #5625: enableKftLauncherComponent")
    try_enable = source_line(fos, "direct_method #5634: tryEnableKftLauncherComponent")
    profile_service = source_line(fos, "class #571: AmazonProfileService")
    profile_on_start = source_line(fos, "virtual_method #6710: onStart")
    profile_init = source_line(fos, "virtual_method #6514: initiateLauncher")
    profile_guard = source_line(fos, "direct_method #6671: enforceProfileInteractionPermissions")
    interface = source_line(boot, "class #144: IAmazonUserManager")
    stub = source_line(boot, "class #2136: IAmazonUserManager.Stub")
    transact = source_line(boot, "virtual_method #1424: onTransact")
    proxy = source_line(boot, "virtual_method #1410: enableKftLauncher")
    child_client = source_line(boot, "virtual_method #1285: createChildUser")

    live_gate = (
        "service listed in saved capture; shell UID 2000 denied service_manager find in saved AVC"
        if service_listed and user_find_denied
        else "saved capture does not establish shell reachability"
    )
    profile_live_gate = (
        "service listed in saved capture; shell UID 2000 denied service_manager find in saved AVC"
        if profile_listed and profile_find_denied
        else "saved capture does not establish shell reachability"
    )

    return [
        row(
            evidence_id="6AK-UM-001",
            surface="publication",
            symbol="AmazonUserManagerService.getSystemServiceName / onStart",
            source_file=str(FOS_REL),
            source_lines=f"getSystemServiceName:{user_service_name}; onStart:{user_on_start}; class:{user_start}",
            source_sha256=fos_hash,
            entry_or_call='publishBinderService("amazonusermanagerservice", BinderService)',
            authorization_or_gate="No gate at publication; access is governed by service-manager SELinux and method behavior.",
            state_effect="Publishes the Amazon user-management Binder endpoint.",
            home_relation="Indirect: this service owns a KFT-specific launcher state path, not the ordinary HOME resolver.",
            live_observation=live_gate,
            classification="SERVICE_VISIBLE_BUT_SHELL_FIND_BLOCKED",
            confidence="Confirmed",
            conclusion="The service exists in system_server but is not a normal shell-visible endpoint on the saved production capture.",
        ),
        row(
            evidence_id="6AK-UM-002",
            surface="binder_contract",
            symbol="IAmazonUserManager.Stub.onTransact -> enableKftLauncher",
            source_file=str(BOOT_REL),
            source_lines=f"interface:{interface}; stub:{stub}; onTransact:{transact}; proxy:{proxy}",
            source_sha256=boot_hash,
            entry_or_call="interface token amazon.os.IAmazonUserManager; transaction code 3; dispatches to enableKftLauncher(UserInfo)",
            authorization_or_gate="Generated stub enforces the interface token and unmarshals UserInfo; no permission check is present in this dispatch block.",
            state_effect="Makes the high-impact server method available to a caller that already has a Binder handle.",
            home_relation="Potential KFT launcher package-state control, not an ordinary set-home/default-home API.",
            live_observation="No transaction was sent; shell was blocked before handle acquisition in the saved AVC capture.",
            classification="STATIC_METHOD_AUTH_REVIEW_CANDIDATE",
            confidence="Strong evidence",
            conclusion="The generated IPC contract alone does not authorize shell access; it exposes a method-local authorization review point.",
        ),
        row(
            evidence_id="6AK-UM-003",
            surface="server_method",
            symbol="AmazonUserManagerService.BinderService.enableKftLauncher(UserInfo)",
            source_file=str(FOS_REL),
            source_lines=f"method:{enable_kft}; block:54415-54478",
            source_sha256=fos_hash,
            entry_or_call="checks AmazonPackageManager availability; returns true for multimodal-device branch; otherwise calls tryEnableKftLauncherComponent and then DPM path",
            authorization_or_gate="No direct checkManageUsersPermission call in this method block; it does call clearCallingIdentity before DPM/profile-owner work.",
            state_effect="Can reach KFT component/package state changes and DPM active-admin/profile-owner operations for a supplied UserInfo.",
            home_relation="High-impact special-user path; not evidence that ordinary HOME resolution is changed.",
            live_observation=live_gate,
            classification="STATIC_HIGH_IMPACT_NOT_ADOPTABLE",
            confidence="Confirmed",
            conclusion="This is the strongest launcher-related Amazon IPC candidate found in this audit, but it is not a shell workaround under the current SELinux boundary.",
        ),
        row(
            evidence_id="6AK-UM-004",
            surface="package_state_mutation",
            symbol="enableKftLauncherComponent(UserInfo)",
            source_file=str(FOS_REL),
            source_lines=f"method:{enable_component}; block:54297-54325",
            source_sha256=fos_hash,
            entry_or_call="AmazonPackageManager.setComponentEnabledSetting(com.amazon.tahoe/...FreeTimeLauncherActivity, 1, 1, userId)",
            authorization_or_gate="Reached only from tryEnableKftLauncherComponent after TV/feature/package checks; outer Binder/service visibility remains required.",
            state_effect="Calls setApplicationEnabledSetting(com.amazon.firelauncher, 2, 0, userId) and com.android.launcher3 with state 2; state 2 is disabled in Android PackageManager constants.",
            home_relation="Could alter a KFT user's launcher availability, but explicitly disables Fire Launcher and is outside the approved experiment boundary.",
            live_observation="Not executed; Fire Launcher was not disabled or otherwise mutated.",
            classification="STATIC_ONLY_REJECTED_FOR_DEVICE_TEST",
            confidence="Confirmed",
            conclusion="The source contains an explicit KFT-specific Fire Launcher disable path; it is not an approved workaround and was not tested.",
        ),
        row(
            evidence_id="6AK-UM-005",
            surface="lifecycle_entry",
            symbol="AmazonUserManagerService.onBootPhase(I)",
            source_file=str(FOS_REL),
            source_lines=f"method:{user_on_boot}; block:55059-55105",
            source_sha256=fos_hash,
            entry_or_call="phase 500 initialization; if AmazonPackageManager.isUpgrade(), iterates users and invokes enableKftLauncher only for child users, then setUserSetupComplete",
            authorization_or_gate="System-server lifecycle and isUpgrade/child-user conditions; not a shell-triggered entry.",
            state_effect="May apply KFT launcher/user-setup state during an upgrade for child users.",
            home_relation="Related to profile-specific launcher state, not ordinary user-0 HOME selection.",
            live_observation="No OTA or lifecycle event was triggered.",
            classification="LIFECYCLE_STATIC_ONLY",
            confidence="Confirmed",
            conclusion="The service has an upgrade-time child-user path, but there is no evidence it rewrites the current user's ordinary HOME preferred record.",
        ),
        row(
            evidence_id="6AK-UM-006",
            surface="authorization_control",
            symbol="checkManageUsersPermission(String)",
            source_file=str(FOS_REL),
            source_lines=f"method:{check_users}; block:54847-54895",
            source_sha256=fos_hash,
            entry_or_call="allows UID 1000/system and UID 0/root; otherwise checks android.permission.MANAGE_USERS and throws SecurityException",
            authorization_or_gate="Explicit UID/permission gate for selected user-management methods; not observed in enableKftLauncher itself.",
            state_effect="Protects sorted-list/user-management operations and the file-backed user list helper.",
            home_relation="Confirms Amazon distinguishes trusted/system user management from shell; it does not by itself prove the KFT method's complete authorization policy.",
            live_observation="Shell UID is 2000 in the saved device baseline; no method was invoked.",
            classification="PARTIAL_AUTH_BOUNDARY",
            confidence="Confirmed",
            conclusion="A separate explicit MANAGE_USERS gate exists, while enableKftLauncher remains a method-local authorization review candidate.",
        ),
        row(
            evidence_id="6AK-UM-007",
            surface="trusted_client",
            symbol="AmazonUserManagerImpl.createChildUser -> IAmazonUserManager.enableKftLauncher",
            source_file=str(BOOT_REL),
            source_lines=f"createChildUser:{child_client}; client call around 369203-369243",
            source_sha256=boot_hash,
            entry_or_call="trusted framework client obtains mService and calls enableKftLauncher, then setUserSetupComplete; failures remove the created user",
            authorization_or_gate="Client is framework-side; this is not evidence of a third-party or shell caller.",
            state_effect="Creates/initializes child-user KFT state and launcher state as part of user creation.",
            home_relation="Explains why the IPC exists and why it should not be treated as a default-home setter.",
            live_observation="No child user was created.",
            classification="TRUSTED_CLIENT_CONTEXT",
            confidence="Confirmed",
            conclusion="The known client context is child-user provisioning, not ordinary Launcher selection.",
        ),
        row(
            evidence_id="6AK-PROF-001",
            surface="publication",
            symbol="AmazonProfileService.onStart",
            source_file=str(FOS_REL),
            source_lines=f"class:{profile_service}; onStart:{profile_on_start}; block:80813-80823",
            source_sha256=fos_hash,
            entry_or_call='publishBinderService("amazonprofileservice", BinderService)',
            authorization_or_gate="Private service-manager endpoint; saved AVC denies shell UID 2000 find.",
            state_effect="Publishes profile lifecycle Binder APIs.",
            home_relation="Profile lifecycle and explicit profile-picker launch paths; not formal HOME resolver selection.",
            live_observation=profile_live_gate,
            classification="SERVICE_VISIBLE_BUT_SHELL_FIND_BLOCKED",
            confidence="Confirmed",
            conclusion="The profile service is not a legitimate shell-visible route in the saved capture.",
        ),
        row(
            evidence_id="6AK-PROF-002",
            surface="profile_method",
            symbol="AmazonProfileService.BinderService.initiateLauncher()",
            source_file=str(FOS_REL),
            source_lines=f"method:{profile_init}; block:76246-76256; guard:{profile_guard}; block:78949-78966",
            source_sha256=fos_hash,
            entry_or_call="calls enforceProfileInteractionPermissions; logs Initiate launcher; returns AmazonProfileManager.SUCCESS",
            authorization_or_gate="requires com.amazon.device.permission.PROFILE_INTERACTION via Context.checkPermission(calling pid/user)",
            state_effect="No set-home, preferred-activity, component-state, or explicit Fire Launcher start is present in this method block.",
            home_relation="Name is launcher-related, but bounded implementation is a permission-gated profile interaction acknowledgement, not a HOME setter.",
            live_observation="No Binder transaction was sent; service lookup is denied to shell.",
            classification="NOT_HOME_SELECTOR",
            confidence="Confirmed",
            conclusion="initiateLauncher is not a demonstrated formal HOME control surface.",
        ),
    ]


def graph() -> str:
    return """flowchart TD
    U[AmazonUserManagerService.onStart] --> P[publishBinderService\namazonusermanagerservice]
    P --> ACL[SELinux service_manager label\namazonusermanager_service]
    S[adb shell / uid 2000] -. find denied in saved AVC .-> ACL
    C[AmazonUserManagerImpl / trusted framework client] --> X[IAmazonUserManager proxy\ntransaction code 3]
    X --> T[IAmazonUserManager.Stub.onTransact]
    T --> E[BinderService.enableKftLauncher(UserInfo)]
    E --> F{isMMDevice?}
    F -- yes --> R[return true\nno launcher mutation in this branch]
    F -- no --> K[tryEnableKftLauncherComponent]
    K --> Q[existsKftLauncher / isTv checks]
    Q --> M[enableKftLauncherComponent]
    M --> A[enable com.amazon.tahoe FreeTimeLauncherActivity]
    M --> D[disable com.amazon.firelauncher\nand com.android.launcher3]
    E --> I[clearCallingIdentity]
    I --> DP[setActiveAdmin / setProfileOwner\nKFT user]
    PS[AmazonProfileService.initiateLauncher] --> PG[enforce PROFILE_INTERACTION]
    PG --> PSR[return SUCCESS\nno formal HOME write in bounded block]
"""


def markdown_graph(graph_text: str) -> str:
    return """# Phase 6AK launcher/user service graph (plain text)

The diagram is intentionally a static call/control graph.  Dashed edges are
boundaries evidenced by the saved live SELinux capture, not invoked Binder
transactions.

```text
AmazonUserManagerService.onStart
  -> publishBinderService("amazonusermanagerservice")
  -> service_context amazonusermanager_service
  -> shell uid=2000: service_manager find denied (saved AVC)

trusted AmazonUserManagerImpl
  -> IAmazonUserManager.Proxy.transact(code=3)
  -> IAmazonUserManager.Stub.onTransact
  -> BinderService.enableKftLauncher(UserInfo)
     -> isMMDevice branch / tryEnableKftLauncherComponent
     -> enableKftLauncherComponent
        -> enable com.amazon.tahoe/...FreeTimeLauncherActivity
        -> disable com.amazon.firelauncher and com.android.launcher3
     -> clearCallingIdentity
     -> DPM active-admin/profile-owner path

AmazonProfileService.BinderService.initiateLauncher
  -> enforceProfileInteractionPermissions
  -> return SUCCESS
  -> no bounded formal HOME write or Fire Launcher explicit start
```

Mermaid source:

```mermaid
""" + graph_text + "```\n"


def report(rows: list[dict[str, str]], inputs: dict[Path, str], output: Path) -> tuple[str, str]:
    user_row = next(row for row in rows if row["evidence_id"] == "6AK-UM-003")
    profile_row = next(row for row in rows if row["evidence_id"] == "6AK-PROF-002")
    live_user = next(row for row in rows if row["evidence_id"] == "6AK-UM-001")
    try:
        output_label = output.relative_to(ROOT)
    except ValueError:
        output_label = output
    evidence_lines = [
        "# Phase 6AK evidence index — Launcher/user service authorization",
        "",
        "This index is generated by `tools/scripts/audit_phase6ak_launcher_user_service.py`.",
        "The audit is host-only; no Binder transaction or device mutation was performed.",
        "",
        "| Evidence ID | Source | File / location | Observed result | Interpretation | Confidence |",
        "|---|---|---|---|---|---|",
    ]
    for item in rows:
        evidence_lines.append(
            f"| {item['evidence_id']} | PS7331 VDEX / saved capture | `{item['source_file']}:{item['source_lines']}` | "
            f"{item['entry_or_call']} | {item['conclusion']} | {item['confidence']} |"
        )
    evidence_lines.extend([
        "",
        "## Input hashes",
        "",
        "| Input | SHA-256 |",
        "|---|---|",
    ])
    for path in (FOS_REL, BOOT_REL, SERVICE_REL, AVC_REL):
        evidence_lines.append(f"| `{path}` | `{sha256(ROOT / path)}` |")
    evidence = "\n".join(evidence_lines) + "\n"

    report_text = f"""# Phase 6AK — Amazon launcher/user Binder authorization closure

Generated: {datetime.now(timezone.utc).isoformat()}

## Scope and safety

This phase is a host-only analysis of preserved Fire OS PS7331 VDEX
disassembly and saved read-only service/SELinux captures.  It did not use ADB,
look up a private Binder handle, send a transaction, create a user, alter a
package, alter a profile, replay an OTA/OOBE broadcast, or change settings.

## Executive result

### 已證實

1. `AmazonUserManagerService` publishes
   `amazonusermanagerservice` from `onStart()`.  The saved service list shows
   the endpoint, while the saved SELinux AVC shows shell UID 2000 is denied
   `service_manager find` for the service.  Evidence: `6AK-UM-001`.
2. `IAmazonUserManager.Stub.onTransact()` dispatches transaction code `3` to
   `enableKftLauncher(UserInfo)` after interface enforcement and unmarshalling.
   The generated stub block contains no permission check.  Evidence:
   `6AK-UM-002`.
3. The server method contains an explicit KFT path.  Its helper enables
   `com.amazon.tahoe.launcher.FreeTimeLauncherActivity` and calls
   `setApplicationEnabledSetting` with state `2` for
   `com.amazon.firelauncher` and `com.android.launcher3`.  Evidence:
   `6AK-UM-003`, `6AK-UM-004`.
4. The KFT path is entered from child-user creation and from the system-server
   upgrade/child-user lifecycle path, not from ordinary HOME resolution.
   Evidence: `6AK-UM-005`, `6AK-UM-007`.
5. `AmazonProfileService.BinderService.initiateLauncher()` is protected by
   `com.amazon.device.permission.PROFILE_INTERACTION` and, in its bounded
   method body, only enforces the permission, logs, and returns success.  No
   formal HOME write or Fire Launcher explicit start appears there. Evidence:
   `6AK-PROF-002`.

### 高可信推論

- `enableKftLauncher` is a high-impact static method-auth review candidate,
  but it is not a shell-accessible workaround under the saved production
  policy.  The correct boundary is **method-local auth candidate plus
  service-manager/SELinux reachability denial**, not “unauthorized shell root”.
- The explicit Fire Launcher state mutation belongs to KFT/child-user
  provisioning.  It does not explain the ordinary user-0 resolver result by
  itself and does not demonstrate a standard default-HOME writer.

### 待驗證

- Whether every trusted caller of `enableKftLauncher` is independently
  constrained by a higher-level package/signature policy outside the generated
  stub.  No private transaction was sent to answer this.
- Whether the current tablet exposes the multimodal feature branch that makes
  `enableKftLauncher` return early.  This is not needed for the shell-boundary
  result and was not changed or probed through private APIs.

### 已排除 / 因風險拒絕測試

- No evidence supports using `enableKftLauncher` as an ordinary HOME
  replacement.
- No attempt was made to invoke transaction code 3, forge a `UserInfo`, create
  a child user, set a profile owner, or disable Fire Launcher.  Those tests are
  outside the approved safe boundary.

## Detailed control paths

### AmazonUserManagerService

```text
AmazonUserManagerService.onStart()
  -> publishBinderService("amazonusermanagerservice")
  -> shell uid=2000 service_manager find denied (saved AVC)

trusted framework client
  -> IAmazonUserManager.Proxy.transact(code=3)
  -> Stub.onTransact
  -> BinderService.enableKftLauncher(UserInfo)
  -> KFT checks / tryEnableKftLauncherComponent
  -> enableKftLauncherComponent
     -> enable FreeTime launcher component
     -> disable Fire Launcher and Launcher3 for supplied user
  -> DPM active-admin/profile-owner path after clearCallingIdentity
```

The separate `checkManageUsersPermission(String)` method explicitly permits
UID 1000 and UID 0, otherwise checks `android.permission.MANAGE_USERS` and
throws `SecurityException`.  It is used by selected user-list methods and is
not called in the bounded `enableKftLauncher` method.  That asymmetry is
recorded as a static review item, not as a device exploit finding.

### AmazonProfileService

```text
AmazonProfileService.BinderService.initiateLauncher()
  -> enforceProfileInteractionPermissions()
  -> Context.checkPermission(com.amazon.device.permission.PROFILE_INTERACTION)
  -> log "Initiate launcher"
  -> return AmazonProfileManager.SUCCESS
```

Other profile-service methods can explicitly start configured profile-picker
activities for the current user, but that is a profile UI path and not a
formal HOME resolver setter.

## Why this does not produce a new workaround

The method that contains the explicit Fire Launcher disable calls is behind a
private system-server service.  Existing live evidence shows shell cannot even
obtain the service handle under enforcing SELinux.  The allowed route would
also cross KFT child-user/DPM semantics and could alter protected package
state, so it is not an acceptable experiment on the production user.

This closes the highest-value static candidate without repeating the already
disproved component-disable or ordinary `set-home-activity` tests.

## Reproduction

```sh
python3 tools/scripts/audit_phase6ak_launcher_user_service.py --dry-run
python3 tools/scripts/audit_phase6ak_launcher_user_service.py \\
  --output {output_label}
```

The command reads only the four preserved inputs listed in the evidence index.
The generated artifact contains input hashes, method snippets, a CSV, a
control-flow graph, and a SHA-256 manifest.

## Next minimal research target

If more launcher research is justified, the next safe target is a host-only
comparison of the KFT path against the current user-0 HOME resolver and the
saved `BootAfterSystemOTAReceiver`/OOBE lifecycle evidence.  Do not invoke the
private Binder method; first identify all trusted callers and their package /
signature constraints from static artifacts.
"""
    return report_text, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/phase6ak/launcher-user-service-20260805-01"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-publish", action="store_true", help="write only the canonical artifact")
    args = parser.parse_args()

    inputs = load_inputs()
    assert_markers(inputs)
    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "binder_transaction_sent": False,
            "inputs": [str(path) for path in (FOS_REL, BOOT_REL, SERVICE_REL, AVC_REL)],
            "output": str(args.output),
        }, indent=2))
        return 0

    rows = build_rows(inputs)
    artifact = (ROOT / args.output) if not args.output.is_absolute() else args.output
    artifact.mkdir(parents=True, exist_ok=False)

    table_path = artifact / "launcher-user-service.csv"
    with table_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    graph_text = graph()
    write_text(artifact / "launcher-user-service.mmd", graph_text)
    write_text(artifact / "launcher-user-service.md", markdown_graph(graph_text))

    fos = ROOT / FOS_REL
    boot = ROOT / BOOT_REL
    _, _, user_method = method_block(fos, "virtual_method #5624: enableKftLauncher", "   virtual_method #5627:")
    _, _, component_method = method_block(fos, "direct_method #5625: enableKftLauncherComponent", "   direct_method #5626:")
    _, _, check_method = method_block(fos, "direct_method #5652: checkManageUsersPermission", "  class #442:")
    _, _, profile_method = method_block(fos, "virtual_method #6514: initiateLauncher", "   virtual_method #6515:")
    _, _, profile_guard_method = method_block(fos, "direct_method #6671: enforceProfileInteractionPermissions", "   direct_method #6672:")
    _, _, stub_method = method_block(boot, "virtual_method #1424: onTransact", "  class #2137:")
    _, _, child_method = method_block(boot, "virtual_method #1285: createChildUser", "   virtual_method #1287:")
    write_text(artifact / "amazon-user-manager-methods.txt", user_method + "\n" + component_method + "\n" + check_method)
    write_text(artifact / "amazon-profile-methods.txt", profile_method + "\n" + profile_guard_method)
    write_text(artifact / "amazon-user-manager-ipc.txt", stub_method + "\n" + child_method)

    summary = {
        "phase": "6AK",
        "title": "Amazon launcher/user Binder authorization closure",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "binder_transaction_sent": False,
        "package_or_user_state_mutated": False,
        "rows": len(rows),
        "key_result": "KFT enableKftLauncher is a static high-impact path, but shell service-manager find is denied in saved production capture; no new shell workaround established.",
        "input_hashes": {str(path): sha256(ROOT / path) for path in (FOS_REL, BOOT_REL, SERVICE_REL, AVC_REL)},
        "expected_fos_sha256": FOS_SHA256,
        "fos_sha256_matches_expected": sha256(fos) == FOS_SHA256,
        "artifact_files": [
            "launcher-user-service.csv",
            "launcher-user-service.mmd",
            "launcher-user-service.md",
            "amazon-user-manager-methods.txt",
            "amazon-profile-methods.txt",
            "amazon-user-manager-ipc.txt",
        ],
    }
    write_json(artifact / "summary.json", summary)

    manifest_paths = sorted(path for path in artifact.iterdir() if path.is_file())
    manifest = "".join(f"{sha256(path)}  {path.name}\n" for path in manifest_paths)
    write_text(artifact / "sha256sums.txt", manifest)

    report_text, evidence_text = report(rows, inputs, artifact)
    if not args.skip_publish:
        write_text(ROOT / "findings/phase-6ak-launcher-user-service.md", report_text)
        write_text(ROOT / "findings/phase-6ak-evidence-index.md", evidence_text)

        output_table = ROOT / "output/tables/phase6ak-launcher-user-service.csv"
        output_graph = ROOT / "output/call-graphs/phase6ak-launcher-user-service.mmd"
        output_plain = ROOT / "output/call-graphs/phase6ak-launcher-user-service.md"
        write_text(output_table, table_path.read_text(encoding="utf-8"))
        write_text(output_graph, graph_text)
        write_text(output_plain, markdown_graph(graph_text))

    print(json.dumps({
        "artifact": str(artifact.relative_to(ROOT)),
        "report": "findings/phase-6ak-launcher-user-service.md",
        "evidence_index": "findings/phase-6ak-evidence-index.md",
        "rows": len(rows),
        "host_only": True,
        "device_contacted": False,
        "binder_transaction_sent": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
