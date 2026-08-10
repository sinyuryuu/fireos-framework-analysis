#!/usr/bin/env python3
"""Build the Phase 15 host-only private-service closure."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREWARM = ROOT / "work/luna_worker_phase15_prewarm_parent_closure_20260810.csv"
SERVICES = ROOT / "work/luna_worker_phase15_private_service_boundary_20260810.csv"
DEX = ROOT / "decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log"
FOSINIT = ROOT / "artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonactivitymanager_fosinit.xml"
AVC = ROOT / "artifacts/phase6j/phase6j-service-visibility-20260805-01/filtered_avc.matches.txt"
SERVICE_MATRIX = ROOT / "artifacts/phase6aq/service-context-audit-20260805-06/service-context-matrix.csv"
RUNTIME_RESULT = ROOT / "adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/result.json"
RUNTIME_HOME = ROOT / "adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/after-home_user0.txt"
RUNTIME_PID = ROOT / "adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/target-pid-after.txt"
CALLER_SOURCE = ROOT / "artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java"
CALLER_MANIFEST = ROOT / "artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/resources/AndroidManifest.xml"

TABLE = ROOT / "output/tables/phase15-private-service-boundary.csv"
REPORT = ROOT / "findings/phase-15-report.md"
INDEX = ROOT / "findings/phase-15-evidence-index.md"
GRAPH = ROOT / "output/call-graphs/phase15-prewarm-service-boundary.mmd"
GRAPH_TEXT = ROOT / "output/call-graphs/phase15-prewarm-service-boundary.md"
MANIFEST = ROOT / "firmware/manifests/PHASE15-HOST-ANALYSIS-20260810/sha256sums.txt"

ALLOWED = {"Confirmed", "Strong evidence", "Probable", "Hypothesis", "Disproved", "Unknown"}
FIELDS = [
    "id", "surface_or_service", "entrypoint", "publication",
    "permission_or_gate", "caller_or_client", "binder_identity_or_domain",
    "user_scope", "sink_or_effect", "observed_effect", "evidence",
    "confidence", "missing_edge", "next_safe_step", "source_kind",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def val(row: dict[str, str], *names: str) -> str:
    for name in names:
        item = (row.get(name) or "").strip()
        if item:
            return item
    return "UNKNOWN"


def normalize_confidence(raw: str) -> str:
    aliases = {
        "HIGH": "Strong evidence", "high": "Strong evidence",
        "MEDIUM": "Probable", "medium": "Probable",
        "LOW": "Hypothesis", "low": "Hypothesis",
        "UNKNOWN": "Unknown", "unknown": "Unknown",
        "CONFIRMED": "Confirmed", "confirmed": "Confirmed",
    }
    result = aliases.get(raw.strip(), raw.strip())
    if result not in ALLOWED:
        raise ValueError("invalid confidence: " + raw)
    return result


def normalize_prewarm(row: dict[str, str]) -> dict[str, str]:
    return {
        "id": row["id"],
        "surface_or_service": val(row, "surface"),
        "entrypoint": val(row, "entrypoint"),
        "publication": "IAmazonActivityManager Stub/Proxy or preserved caller",
        "permission_or_gate": val(row, "permission_or_gate"),
        "caller_or_client": val(row, "caller"),
        "binder_identity_or_domain": val(row, "binder_identity"),
        "user_scope": val(row, "user_scope"),
        "sink_or_effect": val(row, "sink"),
        "observed_effect": val(row, "observed_effect"),
        "evidence": val(row, "evidence"),
        "confidence": normalize_confidence(val(row, "confidence")),
        "missing_edge": val(row, "missing_edge"),
        "next_safe_step": val(row, "next_safe_step"),
        "source_kind": "luna_worker_prewarm",
    }


def normalize_service(row: dict[str, str]) -> dict[str, str]:
    return {
        "id": row["id"],
        "surface_or_service": val(row, "service"),
        "entrypoint": val(row, "entrypoint"),
        "publication": val(row, "publication"),
        "permission_or_gate": val(row, "permission_or_gate"),
        "caller_or_client": val(row, "caller_or_client"),
        "binder_identity_or_domain": val(row, "uid_or_domain"),
        "user_scope": val(row, "user_scope"),
        "sink_or_effect": val(row, "sink_or_effect"),
        "observed_effect": val(row, "observed_effect"),
        "evidence": val(row, "evidence"),
        "confidence": normalize_confidence(val(row, "confidence")),
        "missing_edge": val(row, "missing_edge"),
        "next_safe_step": val(row, "next_safe_step"),
        "source_kind": "luna_worker_service_boundary",
    }


def data_rows() -> list[dict[str, str]]:
    data = [normalize_prewarm(row) for row in read_csv(PREWARM)]
    data.extend(normalize_service(row) for row in read_csv(SERVICES))
    if len({row["id"] for row in data}) != len(data):
        raise ValueError("duplicate worker evidence id")
    return data


EXACT_EVIDENCE = [
    ("P15-MAIN-001", "main_exact_dex",
     "decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3642543-3642624",
     "prewarm method: permission check, identity clear, application lookup, startProcessLocked",
     "static authorization anomaly; no HOME/package writer in method", "Strong evidence"),
    ("P15-MAIN-002", "main_exact_dex",
     "decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:4465050-4465105",
     "Stub code 1 reads String plus two ints and dispatches preWarmApplicationForUser",
     "exact transaction dispatch mapping", "Confirmed"),
    ("P15-MAIN-003", "main_exact_dex",
     "decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:4464650-4464710",
     "Proxy writes token, package, flags, userId and calls transact(1)",
     "exact parcel contract", "Confirmed"),
    ("P15-MAIN-004", "main_registration",
     "artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonactivitymanager_fosinit.xml:8-28",
     "fosinit publishes AmazonActivityManagerService and vendor manager",
     "publication is confirmed; caller identity remains separate", "Confirmed"),
    ("P15-MAIN-005", "main_registration",
     "decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3783142-3783161",
     "AmazonActivityManagerAMSCallback obtains amazonactivitymanager via ServiceManager",
     "system-server callback wiring", "Confirmed"),
    ("P15-MAIN-006", "main_selinux_runtime",
     "artifacts/phase6j/phase6j-service-visibility-20260805-01/filtered_avc.matches.txt:17-23,44-65,79-83",
     "shell UID 2000 receives service_manager find denials for private services",
     "shell route blocked under enforcing policy", "Confirmed"),
    ("P15-MAIN-007", "prior_live_evidence",
     "adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/result.json",
     "ordinary no-permission APK obtained five private-service handles",
     "handle presence is not method authorization", "Confirmed"),
    ("P15-MAIN-008", "prior_live_evidence",
     "findings/phase-6er-amazon-prewarm-confused-deputy.md",
     "tx1 prewarm caused a temporary target process to appear and was rolled back",
     "confirmed process/resource deputy; no root or HOME effect", "Confirmed"),
    ("P15-MAIN-009", "worker_join",
     "findings/phase-6aq-service-context-closure.md",
     "KFT writer disables Fire Launcher/Launcher3 for supplied child/profile UserInfo",
     "child-scoped writer; User 0 relay not closed", "Confirmed"),
    ("P15-MAIN-010", "cross_phase_join",
     "findings/phase-6fl-amazon-caller-identity-relay-audit.md",
     "reviewed relay inventory found no new ordinary-app-to-User0 HOME/package writer",
     "strong negative result bounded to reviewed corpus", "Strong evidence"),
]


def evidence_path(evidence: str) -> Path | None:
    for raw in evidence.split(";"):
        item = re.sub(r":\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*$", "", raw.strip())
        path = ROOT / item
        if path.is_file():
            return path
    return None


def write_table(data: list[dict[str, str]]) -> None:
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    with TABLE.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def write_index(data: list[dict[str, str]]) -> None:
    lines = [
        "# Phase 15 evidence index — Amazon private-service closure",
        "",
        "Generated from fixed-schema worker inventories and exact PS7331/fosinit,",
        "SELinux, and prior bounded runtime artifacts. Phase 15 itself performed",
        "no device mutation.",
        "",
        "| Evidence ID | Source | File | SHA-256 | Test ID | Observation | Interpretation | Confidence |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in data:
        path = evidence_path(row["evidence"])
        file_hash = sha256(path) if path else "UNAVAILABLE"
        test_id = "PRIOR-EVIDENCE-REFERENCED" if row["source_kind"] == "prior_live_evidence" else "PHASE15-HOST-ANALYSIS-20260810"
        lines.append(
            "| %s | %s | %s | SHA256=%s | %s | %s | %s | %s |"
            % (row["id"], row["source_kind"], row["evidence"], file_hash,
               test_id, row["observed_effect"], row["missing_edge"], row["confidence"])
        )
    for eid, source, path_text, observation, interpretation, level in EXACT_EVIDENCE:
        path = evidence_path(path_text)
        file_hash = sha256(path) if path else "UNAVAILABLE"
        test_id = "PRIOR-EVIDENCE-REFERENCED" if source == "prior_live_evidence" else "PHASE15-HOST-ANALYSIS-20260810"
        lines.append(
            "| %s | %s | %s | SHA256=%s | %s | %s | %s | %s |"
            % (eid, source, path_text, file_hash, test_id, observation, interpretation, level)
        )
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


REPORT_TEXT = """# Phase 15 — Amazon private-service authorization and sink closure

Date: 2026-08-10
Device context: KFTRWI / trona / Android 9/API 28 / PS7331.4463N
Serial referenced by prior runtime evidence: G001LT0511550CFT
Scope: host-only static closure plus previously archived bounded runtime evidence.

## Executive result

已證實：an ordinary APK can obtain handles for several Amazon private services
under the FireOS app_api_service route. The earlier bounded tx1 test also
demonstrated a real process/resource effect: a no-permission APK requested
preWarmApplicationForUser and a temporary target process appeared. This is a
confused-deputy finding, not root and not a HOME replacement.

已證實：the exact PS7331 VDEX is mapped through the generated Proxy and Stub,
transaction 1, fosinit service declaration, and system-server callback
ServiceManager acquisition.

高可信推論：the prewarm anomaly is confined to a process-prewarm sink. The
reviewed method reaches getApplicationInfo and startProcessLocked("prewarm");
it contains no setHomeActivity, preferred-activity, package-enabled,
component-enabled, or Fire Launcher mutation sink.

已證實：the KFT path is the strongest Fire-specific package-state writer in
this corpus. It enables Tahoe and disables Fire Launcher/Launcher3 for a
supplied child/profile UserInfo.id. The evidence does not close an ordinary
caller or shell to accepted User 0 input.

未找到：a new low-privilege path that changes formal HOME, disables User 0 Fire
Launcher, writes persistent preferred HOME, or reaches an OTA/partition sink.
Phase 15 sent no Binder transaction and changed no device state.

## 1. Exact prewarm call chain

The exact PS7331 method begins at
decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3642543:

    checkCallingPermission("com.amazon.permission.APP_PREWARM")
    Binder.clearCallingIdentity()
    package/user branches
    IPackageManager.getApplicationInfo(package, 1024, userId)
    PreWarmCacheHelper.getKeepIfLargeValue(package)
    ActivityManagerService.startProcessLocked(..., "prewarm", ...)
    Binder.restoreCallingIdentity()

The saved instruction stream has no visible move-result, comparison, denial
return, or SecurityException between the permission call and identity clear.
That is a Strong evidence authorization-review candidate, not evidence of
arbitrary code execution or root.

The Proxy at disassembly.log:4464650-4464710 serializes a String and two ints
and invokes Binder transact(1). The Stub at disassembly.log:4465050-4465105
enforces the interface token, reads the same values, dispatches to the server
method, and writes an integer result.

## 2. Publication and caller boundary

amazonactivitymanager_fosinit.xml:8-28 declares AmazonActivityManagerService
and the cached activity vendor manager. The exact system-server callback
initializes its interface with ServiceManager.getService("amazonactivitymanager")
at disassembly.log:3783142-3783161.

Saved runtime evidence separates two caller classes:

- shell UID 2000 is denied service-manager find under SELinux Enforcing;
- an ordinary APK previously obtained non-null handles to private services, so
  method-level authorization must be reviewed separately.

The preserved direct caller for prewarm is Amazon Alexa's
ExplicitIntentAction.java:268-282, and the package declares APP_PREWARM. This
supports the intended privileged-caller interpretation but does not erase the
confirmed tx1 behavior observed in the earlier bounded test.

## 3. Sink inventory beyond Launcher

| Surface | Evidence result | Meaning |
|---|---|---|
| ActivityManager prewarm | getApplicationInfo then startProcessLocked | Confirmed process/resource deputy; no formal HOME/package sink |
| Amazon Package Manager | flags/metadata/proxy-related methods | Capability exists; no closed ordinary-app enabled-state/HOME edge |
| Amazon User Manager/KFT | Tahoe/Fire/Launcher3 state changes | Confirmed child/profile writer; User 0 relay not closed |
| Profile service | profile interaction and cross-user gates | No persistent HOME writer in reviewed path |
| Input/keyevent | implicit MAIN + HOME path and input policy | No explicit Fire component or preferred mutation observed |
| Migration service | Fire Launcher refresh notification | Side effect, not package/HOME setter |
| OOBE/OTA | lifecycle/setup and update capability | Not a generic low-privilege control surface; replay rejected |

The normalized rows are in output/tables/phase15-private-service-boundary.csv.
Worker source rows remain under work/ and are included in the Phase 15 hash
manifest.

## 4. HOME and Fire Launcher conclusion

The prior User 0 baseline remains:

    priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
    com.amazon.firelauncher/.Launcher

Nothing in the prewarm chain writes that resolver state. The KFT writer is
scoped to a supplied child/profile UserInfo.id, and the ordinary-app handle
test left User 0 HOME and Fire package state unchanged after rollback.

Therefore:

- 已證實: process-prewarm confused deputy;
- 已證實: child/profile KFT state writer exists;
- 已排除（目前保存範圍）: prewarm as a Fire Launcher replacement or root path;
- 待驗證: remaining private methods whose caller/sink joins are incomplete;
- 因風險拒絕測試: guessed Binder parcels, forged UserInfo, private-service
  mutation, OOBE/OTA replay, Fire Launcher mutation, root, and partition work.

## 5. Next safe work

1. Recover missing fosinit/service-context declarations for user/profile/migration.
2. Map callers of package-state writers and prove user/caller validation.
3. Inspect AmazonPackageManager metadata/flag consumers for a real policy
   decision, without treating metadata capability as a package-state writer.
4. If no new caller-to-sink edge appears, formally close the result as:
   formal HOME replacement unavailable without protected/system capability;
   one confirmed process/resource deputy remains, with no root claim.

No additional device mutation is justified by the current evidence.

## Reproduction and QA

    python3 tools/scripts/build_phase15_static_closure.py --dry-run
    python3 tools/scripts/build_phase15_static_closure.py --force
    python3 -m py_compile tools/scripts/build_phase15_static_closure.py

Generated input/output hashes are in
firmware/manifests/PHASE15-HOST-ANALYSIS-20260810/sha256sums.txt.
Raw device captures and prior test APK artifacts are not rewritten by this phase.
"""


def write_report() -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(REPORT_TEXT, encoding="utf-8")


def write_graph() -> None:
    graph = """flowchart TD
  A[ordinary APK / saved Alexa caller] --> B[ServiceManager.getService amazonactivitymanager]
  B --> C[IAmazonActivityManager Proxy]
  C -->|transact code 1: token + String + int + int| D[Stub.onTransact]
  D --> E[BinderService.preWarmApplicationForUser]
  E --> F[checkCallingPermission APP_PREWARM]
  F --> G[result not visibly consumed]
  G --> H[clearCallingIdentity]
  H --> I[IPackageManager.getApplicationInfo]
  I --> J[PreWarmCacheHelper]
  J --> K[startProcessLocked prewarm]
  K --> L[process/resource effect only]
  K -.-> X[NO observed HOME/package-state sink]
  M[shell UID 2000] -.->|SELinux find denied| B
  N[ordinary app handle] --> B
  O[KFT child lifecycle] --> P[enableKftLauncherComponent UserInfo]
  P --> Q[Amazon Package Manager enabled-state calls]
  Q --> R[child/profile UserInfo.id scope]
  R -.-> S[User 0 Fire Launcher relay not closed]
"""
    plain = """# Phase 15 prewarm and package-state boundary

""" + graph + """

Plain-text form:

ordinary APK/Alexa -> ServiceManager -> Proxy -> transact(1)
  -> Stub.onTransact -> preWarmApplicationForUser
  -> permission check -> clearCallingIdentity -> getApplicationInfo
  -> PreWarmCacheHelper -> startProcessLocked("prewarm")
  -> process/resource effect
  -X-> HOME resolver / package enabled-state writer

KFT child lifecycle -> enableKftLauncherComponent(UserInfo)
  -> Amazon Package Manager enabled-state calls
  -> supplied child/profile UserInfo.id
  -X-> demonstrated ordinary User 0 relay
"""
    GRAPH.parent.mkdir(parents=True, exist_ok=True)
    GRAPH.write_text(graph, encoding="utf-8")
    GRAPH_TEXT.write_text(plain, encoding="utf-8")


def write_manifest() -> None:
    paths = [
        PREWARM, PREWARM.with_suffix(".md"), SERVICES, SERVICES.with_suffix(".md"),
        DEX, FOSINIT, AVC, SERVICE_MATRIX, RUNTIME_RESULT,
        RUNTIME_HOME, RUNTIME_PID, CALLER_SOURCE, CALLER_MANIFEST, TABLE,
        REPORT, INDEX, GRAPH, GRAPH_TEXT, ROOT / "tools/scripts/build_phase15_static_closure.py",
    ]
    lines = []
    for path in paths:
        if path.is_file():
            lines.append("%s  %s" % (sha256(path), path.relative_to(ROOT)))
        else:
            lines.append("MISSING  %s" % path.relative_to(ROOT))
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


def check_inputs() -> None:
    required = [PREWARM, SERVICES, DEX, FOSINIT, AVC, RUNTIME_RESULT]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing input(s): " + ", ".join(missing))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    check_inputs()
    outputs = [TABLE, REPORT, INDEX, GRAPH, GRAPH_TEXT, MANIFEST]
    if args.dry_run:
        print("inputs=ok")
        for path in outputs:
            print("would_write=" + str(path.relative_to(ROOT)))
        return 0
    if not args.force:
        existing = [str(path.relative_to(ROOT)) for path in outputs if path.exists()]
        if existing:
            raise SystemExit("refusing to overwrite; use --force: " + ", ".join(existing))
    data = data_rows()
    write_table(data)
    write_report()
    write_index(data)
    write_graph()
    write_manifest()
    print("rows=%d" % len(data))
    print("report=" + str(REPORT.relative_to(ROOT)))
    print("table=" + str(TABLE.relative_to(ROOT)))
    print("manifest=" + str(MANIFEST.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
