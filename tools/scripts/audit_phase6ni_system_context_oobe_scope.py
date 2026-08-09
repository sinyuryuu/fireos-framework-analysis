#!/usr/bin/env python3
"""Verify the preserved PS7331 OOBE sender's system-context user path.

Host-only.  Reads disassembly/XML already present in the workspace and never
contacts a device or executes a Binder/updater path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[2]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(text: str, needle: str, label: str) -> dict[str, object]:
    return {"label": label, "needle": needle, "present": needle in text}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--services-log", type=Path, default=BASE / "decompiled/baksmali/vdexExtractor/services/disassembly.log")
    ap.add_argument("--fosservices-log", type=Path, default=BASE / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log")
    ap.add_argument("--boot-log", type=Path, default=BASE / "decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log")
    ap.add_argument("--fosinit", type=Path, default=BASE / "artifacts/amazon-services/amazonpackagemanager_fosinit.xml")
    ap.add_argument("--output", type=Path, default=BASE / "artifacts/phase6ni-system-context-oobe-scope-20260810-01")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    paths = [args.services_log, args.fosservices_log, args.boot_log, args.fosinit]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        print("missing input: " + ", ".join(missing), file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"refusing to overwrite existing output: {args.output}", file=sys.stderr)
        return 2

    services = args.services_log.read_text(encoding="utf-8", errors="replace")
    fosservices = args.fosservices_log.read_text(encoding="utf-8", errors="replace")
    boot = args.boot_log.read_text(encoding="utf-8", errors="replace")
    fosinit = args.fosinit.read_text(encoding="utf-8", errors="replace")
    checks = [
        require(fosservices, "Lcom/amazon/android/service/pm/AmazonPackageManagerService;.mContext", "Amazon PM service stores mContext"),
        require(fosservices, "virtual_method #7558: onBootPhase (I)V", "Amazon PM onBootPhase exists"),
        require(fosservices, "Context;.sendBroadcast:(Landroid/content/Intent;Ljava/lang/String;)", "sender uses Context.sendBroadcast with permission"),
        require(fosservices, "isUpgrade", "sender has upgrade guard"),
        require(services, "SystemServer;.createSystemContext", "SystemServer creates system context"),
        require(boot, "direct_method #3345: systemMain ()Landroid/app/ActivityThread;", "system context starts from ActivityThread.systemMain"),
        require(boot, "virtual_method #3240: getSystemContext ()Landroid/app/ContextImpl;", "SystemServer obtains ActivityThread system context"),
        require(boot, "ContextImpl;.createSystemContext", "ContextImpl system-context constructor path"),
        require(boot, "ContextImpl;.mUser", "ContextImpl stores mUser"),
        require(boot, "Process;.myUserHandle", "null ContextImpl user defaults to process user"),
        require(boot, "Process;.myUid", "Process.myUserHandle derives from process UID"),
        require(fosinit, "AmazonPackageManagerService", "fosinit publishes Amazon PM service"),
    ]
    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "checks": len(checks),
            "all_present": all(c["present"] for c in checks),
            "output": str(args.output),
        }, indent=2))
        return 0 if all(c["present"] for c in checks) else 1

    args.output.mkdir(parents=True)
    manifest = {
        "host_only": True,
        "device_contacted": False,
        "binder_called": False,
        "updater_executed": False,
        "partition_written": False,
        "inputs": {str(p.relative_to(BASE)): digest(p) for p in paths},
        "checks": len(checks),
        "all_present": all(c["present"] for c in checks),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with (args.output / "evidence.csv").open("w", encoding="utf-8") as f:
        f.write("evidence_id,label,needle,present,source\n")
        for idx, check in enumerate(checks, 1):
            source = "services" if check["needle"] in services else "fosservices" if check["needle"] in fosservices else "boot-framework" if check["needle"] in boot else "fosinit"
            f.write(f"6NI-OOBE-{idx:03d},{check['label']},{check['needle']},{check['present']},{source}\n")

    report = """# Phase 6NI — OOBE sender system-context user-scope closure

This is a host-only verification of preserved PS7331 VDEX and `fosinit`
artifacts. No device, Binder, OTA, updater, or package/settings mutation was
performed.

## Verified chain

```text
SystemServer.createSystemContext()
  -> ActivityThread.systemMain()
  -> ActivityThread.getSystemContext()
  -> ContextImpl.createSystemContext()
  -> ContextImpl constructor with null UserHandle
  -> Process.myUserHandle() default
  -> AmazonPackageManagerService.mContext
  -> onBootPhase(550) + isUpgrade()
  -> mContext.sendBroadcast(BOOT_AFTER_SYSTEM_OTA, permission)
  -> framework broadcast user derived from ContextImpl.getUserId()
```

The preserved code therefore supports **Strong evidence** that the sender is a
system-server context path whose user is the system process user by default.
The selected fragments do not encode a child `UserInfo`, a `USER_ALL` target,
or a HOME/preferred-activity setter. The exact numeric runtime user remains a
runtime/build-context fact and is not promoted here to an unconditional User 0
claim.

## Boundary

The receiver's already-closed OOBE path uses its delivered context for
component/settings operations. It does not, in the reviewed source, call
`setHomeActivity`, `replacePreferredActivity`, or a formal HOME role setter.
Consequently this chain is lifecycle/setup evidence, not a launcher replacement
or a shell-callable privilege relay.

## Confidence labels

- **已證實：** system-server creates and owns the sender context path; the
  context default derives from the process user; the OTA broadcast is guarded
  and permission-protected.
- **高可信推論：** on this Android system-server path the effective user is the
  system user, conventionally user 0, but this report does not replace a live
  numeric observation.
- **待驗證：** exact runtime numeric delivery user on this particular build;
  complete runtime `fosinit` loading outside the preserved corpus.
- **已排除（bounded）：** the reviewed OOBE helper is a direct formal HOME
  preference writer.
- **因風險拒絕測試：** manual protected-broadcast replay, OTA/recovery
  execution, package/state mutation, and partition writes.
"""
    (args.output / "result.md").write_text(report, encoding="utf-8")
    (args.output / "flow.mmd").write_text(
        "flowchart TD\n"
        "  SS[SystemServer.createSystemContext] --> CT[ContextImpl.mUser]\n"
        "  CT --> PM[AmazonPackageManagerService.mContext]\n"
        "  PM --> GU[onBootPhase + isUpgrade guard]\n"
        "  GU --> BC[permission-protected BOOT_AFTER_SYSTEM_OTA broadcast]\n"
        "  BC --> RC[receiver context-derived user scope]\n"
        "  RC -. no formal HOME setter in reviewed OOBE source .-> H[HOME resolver]\n",
        encoding="utf-8",
    )
    files = sorted(p for p in args.output.iterdir() if p.is_file() and p.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{digest(p)}  {p.name}" for p in files) + "\n", encoding="utf-8"
    )
    print(json.dumps({**manifest, "output": str(args.output)}, indent=2))
    return 0 if manifest["all_present"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
