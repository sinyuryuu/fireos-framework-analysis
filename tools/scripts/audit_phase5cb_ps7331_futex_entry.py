#!/usr/bin/env python3
"""Audit the PS7331 source-level futex/PI entry and direct gate surface.

Host-only source/config analysis.  It deliberately does not emit syscall
arguments, race timing, payload material, addresses, or device commands.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def occurrences(lines: list[str], patterns: tuple[str, ...]) -> list[dict[str, object]]:
    compiled = [re.compile(pattern) for pattern in patterns]
    return [
        {"line": i + 1, "text": line.strip()}
        for i, line in enumerate(lines)
        if any(pattern.search(line) for pattern in compiled)
    ]


def function_lines(lines: list[str], signature: str) -> tuple[int, int, list[str]]:
    start = next((i for i, line in enumerate(lines) if re.search(signature, line)), None)
    if start is None:
        raise ValueError(f"function not found: {signature}")
    depth = 0
    opened = False
    end = start
    for i in range(start, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        opened |= "{" in lines[i]
        if opened and depth == 0:
            end = i
            break
    return start + 1, end + 1, lines[start : end + 1]


def inspect(futex_path: Path, rtmutex_path: Path, config_path: Path) -> dict:
    futex_lines = futex_path.read_text(encoding="utf-8", errors="replace").splitlines()
    rtmutex_lines = rtmutex_path.read_text(encoding="utf-8", errors="replace").splitlines()
    config_lines = config_path.read_text(encoding="utf-8", errors="replace").splitlines()

    syscall_start, syscall_end, syscall = function_lines(
        futex_lines, r"^\s*SYSCALL_DEFINE6\(futex"
    )
    do_start, do_end, do_futex = function_lines(
        futex_lines, r"^\s*long\s+do_futex\s*\("
    )
    requeue_start, requeue_end, requeue = function_lines(
        futex_lines, r"^\s*static\s+int\s+futex_requeue\s*\("
    )
    proxy_start, proxy_end, proxy = function_lines(
        rtmutex_lines, r"^\s*int\s+rt_mutex_start_proxy_lock\s*\("
    )

    direct_gate_patterns = (r"\bcapable\s*\(", r"\bns_capable\s*\(", r"\bsecurity_[a-zA-Z0-9_]*\s*\(")
    direct_gate = (
        occurrences(syscall, direct_gate_patterns)
        + occurrences(do_futex, direct_gate_patterns)
        + occurrences(requeue, direct_gate_patterns)
        + occurrences(proxy, direct_gate_patterns)
    )
    pointer_checks = (
        occurrences(syscall, (r"access_ok\s*\(", r"copy_from_user\s*\("))
        + occurrences(requeue, (r"get_futex_key\s*\(", r"get_futex_value_locked\s*\("))
    )
    pi_entry = occurrences(
        do_futex,
        (r"case\s+FUTEX_WAIT_REQUEUE_PI", r"case\s+FUTEX_CMP_REQUEUE_PI"),
    )
    cmpxchg_gate = occurrences(
        do_futex,
        (r"if\s*\(!futex_cmpxchg_enabled\)",),
    )
    requeue_proxy = occurrences(
        requeue,
        (r"rt_mutex_start_proxy_lock\s*\(",),
    )
    config_hits = occurrences(
        config_lines,
        (r"^CONFIG_FUTEX=", r"^CONFIG_RT_MUTEXES=", r"^CONFIG_SECURITY_SELINUX=", r"^CONFIG_SECCOMP="),
    )

    return {
        "scope": "PS7331 exact 4.4 source and embedded config; host-only",
        "futex_path": str(futex_path),
        "futex_sha256": sha256(futex_path),
        "rtmutex_path": str(rtmutex_path),
        "rtmutex_sha256": sha256(rtmutex_path),
        "config_path": str(config_path),
        "config_sha256": sha256(config_path),
        "entry_functions": {
            "syscall": {"span": [syscall_start, syscall_end], "matches": occurrences(syscall, (r"SYSCALL_DEFINE6\(futex",))},
            "do_futex": {"span": [do_start, do_end], "pi_dispatch": pi_entry, "cmpxchg_gate": cmpxchg_gate},
            "futex_requeue": {"span": [requeue_start, requeue_end], "proxy_calls": requeue_proxy},
            "rt_mutex_start_proxy_lock": {"span": [proxy_start, proxy_end]},
        },
        "direct_credential_gate": {
            "matches": direct_gate,
            "status": "not_observed_in_scoped_functions" if not direct_gate else "observed",
        },
        "pointer_and_state_checks": pointer_checks,
        "futex_cmpxchg_feature_gate": {
            "matches": cmpxchg_gate,
            "status": "present" if cmpxchg_gate else "not_observed",
        },
        "config_hits": config_hits,
        "userspace_policy_status": "UNRESOLVED_FROM_KERNEL_SOURCE_ONLY",
        "source_reachability_status": (
            "SYSCALL_TO_PI_REQUEUE_PROXY_PATH_PRESENT"
            if pi_entry and requeue_proxy else "INCOMPLETE"
        ),
        "runtime_exploitability_proven": False,
        "root_or_privilege_gain_proven": False,
        "device_execution": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--futex", type=Path, required=True)
    parser.add_argument("--rtmutex", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output in {Path("/"), Path("."), Path("..")}:
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "device_execution": False,
                          "futex": str(args.futex), "rtmutex": str(args.rtmutex),
                          "config": str(args.config), "output": str(args.output)},
                         indent=2, sort_keys=True))
        return 0
    for path, label in ((args.futex, "futex source"), (args.rtmutex, "rtmutex source"),
                        (args.config, "kernel config")):
        if not path.is_file():
            parser.error(f"{label} is not a regular file: {path}")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")
    result = inspect(args.futex, args.rtmutex, args.config)
    args.output.mkdir(parents=True)
    (args.output / "entry-audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# PS7331 futex entry audit\n\n"
        f"- Source reachability: **{result['source_reachability_status']}**\n"
        f"- Direct credential gate in scoped functions: **{result['direct_credential_gate']['status']}**\n"
        f"- Userspace policy status: **{result['userspace_policy_status']}**\n"
        "- Runtime exploitability proven: **False**\n"
        "- Root/privilege gain proven: **False**\n\n"
        "Absence of a direct capability check in these files does not bypass Android "
        "SELinux, seccomp, process domains, or other runtime policy.\n",
        encoding="utf-8",
    )
    (args.output / "README.txt").write_text(
        "Host-only source/config audit. No syscall invocation, device I/O, futex "
        "trigger, payload, address, or image mutation.\n",
        encoding="utf-8",
    )
    files = sorted(path for path in args.output.iterdir() if path.is_file())
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
