#!/usr/bin/env python3
"""Build a host-only Amazon caller/sink provenance matrix.

The matrix is deliberately curated from saved, version-scoped evidence.  It
does not call ADB, send Binder transactions, invoke broadcasts, or mutate
users, packages, settings, HOME state, OTA state, or partitions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROWS = [
    {
        "surface": "H2 household service",
        "caller_or_entry": "H2ClientService.onBind() → IH2ClientService methods",
        "registration_or_interface": "exported service; action com.amazon.alta.h2shared.aidl.IH2ClientService",
        "permission_or_gate": "manifest BIND_SERVICE (signature); live query reports the same permission",
        "identity_handling": "AbstractAPICall logs Binder.getCallingUid(); no additional method-local caller gate observed in the recovered Stub",
        "sink": "UserHelper → AndroidUserHelper → AmazonUserManager.createAdultUser/createChildUser",
        "user_scope": "Amazon household/profile lifecycle; nonzero child/adult user creation or removal",
        "low_privilege_caller_found": "false",
        "dynamic_test_allowed": "false",
        "verdict": "Trusted profile-management capability; no direct HOME writer in the APK",
        "evidence": "artifacts/phase6mc-alta-static-20260810-01-manifest.txt:144-154; H2ClientService.java:105-107; AndroidUserHelper.java:78-81",
    },
    {
        "surface": "H2 create-child path",
        "caller_or_entry": "IH2ClientService.addUser() → AddUserAPICall → HouseholdController.createUser()",
        "registration_or_interface": "signature-bound H2 service; workflow command",
        "permission_or_gate": "BIND_SERVICE plus household/account workflow checks",
        "identity_handling": "No shell/app relay was exercised; workflow uses supplied UserMetadata only after service binding",
        "sink": "CreateAndroidUserCommand → UserHelper.createAndroidUser() → AmazonUserManager.createChildUser(name)",
        "user_scope": "New child profile; downstream KFT state is per supplied child user",
        "low_privilege_caller_found": "false",
        "dynamic_test_allowed": "false",
        "verdict": "Natural supported child-user provenance, not a User-0 launcher route",
        "evidence": "AddUserAPICall.java:1-35; HouseholdController.java:323-372; CreateAndroidUserCommand.java:21-32; AndroidUserHelper.java:78-81",
    },
    {
        "surface": "IAmazonUserManager tx3",
        "caller_or_entry": "AmazonUserManagerImpl.createChildUser() → IAmazonUserManager.Proxy transaction 3",
        "registration_or_interface": "amazon.os.IAmazonUserManager / amazonusermanagerservice",
        "permission_or_gate": "private service-manager/SELinux boundary plus child/KFT predicate; ordinary shell lookup is unavailable",
        "identity_handling": "Static Stub/implementation review; no raw tx3 sent in this phase",
        "sink": "AmazonUserManagerService.enableKftLauncherComponent(UserInfo)",
        "user_scope": "UserInfo.id supplied by the child lifecycle; enables Tahoe and sets Fire/Launcher3 state 2 for that child",
        "low_privilege_caller_found": "false",
        "dynamic_test_allowed": "false",
        "verdict": "Confirmed child-scoped package-state writer; not a normal User-0 selector",
        "evidence": "findings/phase-6bk-report.md; decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325,54415-54478",
    },
    {
        "surface": "IAmazonUserManager tx4",
        "caller_or_entry": "IAmazonUserManager.Stub transaction 4 setUserSetupComplete(UserInfo)",
        "registration_or_interface": "amazon.os.IAmazonUserManager / amazonusermanagerservice",
        "permission_or_gate": "interface token; prior controlled evidence reached the method from an ordinary APK",
        "identity_handling": "Implementation clears Binder identity before settings writes, then restores it",
        "sink": "AmazonUserManagerHelper.putIntForUser(user_setup_complete, tv_user_setup_complete)",
        "user_scope": "Caller-supplied setup-state user; settings only",
        "low_privilege_caller_found": "true",
        "dynamic_test_allowed": "false",
        "verdict": "Confirmed settings confused-deputy boundary; no package/HOME sink",
        "evidence": "findings/phase-6gv-amazon-user-manager-tx4-settings-deputy.md; findings/phase-6gi-amazon-user-manager-tx4-user10-deputy.md",
    },
    {
        "surface": "AmazonActivityManager prewarm",
        "caller_or_entry": "AmazonActivityManagerService.BinderService.preWarmApplicationForUser()",
        "registration_or_interface": "private amazonactivitymanager service",
        "permission_or_gate": "APP_PREWARM permission plus target/package filters; service-manager and SELinux boundary",
        "identity_handling": "Static path clears identity before process-start work; denial-result consumption remains an audit note",
        "sink": "startProcessLocked / application prewarm",
        "user_scope": "Requested user/process; no HOME component sink observed",
        "low_privilege_caller_found": "false",
        "dynamic_test_allowed": "false",
        "verdict": "Static authorization candidate, not a launcher or root result",
        "evidence": "findings/phase-6k-report.md: IPC authorization review; findings/phase-6er-amazon-prewarm-confused-deputy.md",
    },
    {
        "surface": "post-system-OTA OOBE sender",
        "caller_or_entry": "AmazonPackageManagerService.onBootPhase(550)",
        "registration_or_interface": "system-server boot lifecycle",
        "permission_or_gate": "PackageManagerService.isUpgrade() plus RECEIVE_BOOT_AFTER_SYSTEM_OTA protected broadcast permission",
        "identity_handling": "system-server sends the broadcast; no ordinary caller relay observed",
        "sink": "BootAfterSystemOTAReceiver → OOBEActivationHelper → OobeHomeActivity/setup state",
        "user_scope": "Provisioning/OOBE lifecycle, primarily User 0 setup state",
        "low_privilege_caller_found": "false",
        "dynamic_test_allowed": "false",
        "verdict": "High-impact lifecycle control; not a safe third-party HOME selector",
        "evidence": "findings/phase-6q-bootafter-system-ota.md; findings/phase-6r-bootafter-system-ota-authorization.md; decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126",
    },
    {
        "surface": "Play Store generic state writers",
        "caller_or_entry": "com.android.vending internal verifier/enterprise-policy paths",
        "registration_or_interface": "data-app package; no HOME-specific interface identified",
        "permission_or_gate": "captured grants include package-state permissions; any framework call still reaches PMS gates",
        "identity_handling": "bounded JADX output; exact callers/inputs are internal and not invoked",
        "sink": "generic setApplicationEnabledSetting/setComponentEnabledSetting writers",
        "user_scope": "internally derived package/component targets",
        "low_privilege_caller_found": "unknown",
        "dynamic_test_allowed": "false",
        "verdict": "No Fire/HOME controller found in bounded scan; provenance lead only",
        "evidence": "findings/phase-6mb-vending-permission-and-state-writer-audit.md",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "root": str(args.root), "output": str(args.output), "rows": len(ROWS)}, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    input_paths = sorted({
        path
        for row in ROWS
        for path in [
            args.root / "findings/phase-6bk-report.md",
            args.root / "findings/phase-6k-report.md",
            args.root / "findings/phase-6q-bootafter-system-ota.md",
            args.root / "findings/phase-6r-bootafter-system-ota-authorization.md",
            args.root / "findings/phase-6er-amazon-prewarm-confused-deputy.md",
            args.root / "findings/phase-6mb-vending-permission-and-state-writer-audit.md",
            args.root / "artifacts/phase6mc-alta-static-20260810-01-manifest.txt",
            args.root / "artifacts/phase6mc-alta-jadx-20260810-01/sources/com/amazon/alta/h2clientservice/H2ClientService.java",
            args.root / "artifacts/phase6mc-alta-jadx-20260810-01/sources/com/amazon/alta/h2shared/helpers/AndroidUserHelper.java",
            args.root / "artifacts/phase6mc-alta-jadx-20260810-01/sources/com/amazon/alta/h2shared/helpers/UserHelper.java",
            args.root / "artifacts/phase6mc-alta-jadx-20260810-01/sources/com/amazon/alta/h2clientservice/workflow/commands/CreateAndroidUserCommand.java",
            args.root / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log",
        ]
    })
    missing = [str(path) for path in input_paths if not path.is_file()]
    if missing:
        raise SystemExit("missing input evidence:\n" + "\n".join(missing))

    args.output.mkdir(parents=True)
    fields = list(ROWS[0].keys())
    with (args.output / "caller-provenance.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ROWS)
    with (args.output / "input-manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["path", "sha256"])
        for path in input_paths:
            writer.writerow([str(path.relative_to(args.root)), sha256(path)])
    summary = {
        "analysis": "host-only curated caller/sink provenance",
        "rows": len(ROWS),
        "low_privilege_caller_found": [row["surface"] for row in ROWS if row["low_privilege_caller_found"] == "true"],
        "dynamic_tests_allowed": [row["surface"] for row in ROWS if row["dynamic_test_allowed"] == "true"],
        "limitations": [
            "The matrix maps saved evidence; it is not proof that an untested IPC is safe to invoke.",
            "No unknown Binder transaction, broadcast, user creation, package mutation, OTA, or reboot was performed.",
            "JADX-derived method text remains an approximate representation; critical claims should be checked against smali/disassembly.",
        ],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
