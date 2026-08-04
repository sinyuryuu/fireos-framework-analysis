#!/usr/bin/env python3
"""Host-only PS7331 source/config layout model.

This script never invokes ADB, executes a kernel, derives a KASLR slide, or
emits an exploit payload.  It reports source/ABI layout and allocator-class
facts only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_config(path: Path) -> dict[str, str | bool]:
    values: dict[str, str | bool] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        match = re.fullmatch(r"CONFIG_([A-Za-z0-9_]+)=(.*)", line)
        if match:
            raw_value = match.group(2)
            values[f"CONFIG_{match.group(1)}"] = (
                True if raw_value == "y" else False if raw_value == "n" else raw_value
            )
        else:
            match = re.fullmatch(r"# (CONFIG_[A-Za-z0-9_]+) is not set", line)
            if match:
                values[match.group(1)] = False
    return values


def align(value: int, boundary: int) -> int:
    return (value + boundary - 1) // boundary * boundary


def layout(fields: list[tuple[str, int, int]], boundary: int = 8) -> dict:
    offset = 0
    result = []
    for name, size, field_boundary in fields:
        offset = align(offset, field_boundary)
        result.append({"name": name, "offset": offset, "size": size})
        offset += size
    return {"fields": result, "sizeof": align(offset, boundary), "alignment": boundary}


def kmalloc_class(request: int) -> str:
    # Linux 4.4 slab_common.c uses 64/128/192/256... on this ARM64 config;
    # 96-byte requests are redirected to kmalloc-128 when alignment is 64.
    if request <= 64:
        return "kmalloc-64"
    if request <= 128:
        return "kmalloc-128"
    if request <= 192:
        return "kmalloc-192"
    return f"kmalloc-{1 << (request - 1).bit_length()}"


def line(path: Path, text: str) -> int | None:
    for number, value in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if text in value:
            return number
    return None


def source_ref(path: Path, needle: str, observation: str) -> dict:
    return {"file": str(path), "line": line(path, needle), "sha256": sha256(path),
            "needle": needle, "observation": observation}


def build(source: Path, config_path: Path) -> dict:
    files = {
        "rtmutex_common": source / "kernel/locking/rtmutex_common.h",
        "rtmutex": source / "kernel/locking/rtmutex.c",
        "futex": source / "kernel/futex.c",
        "sched": source / "include/linux/sched.h",
        "pipe_h": source / "include/linux/pipe_fs_i.h",
        "pipe": source / "fs/pipe.c",
        "ion_h": source / "drivers/staging/android/ion/ion_priv.h",
        "ion": source / "drivers/staging/android/ion/ion.c",
        "fork": source / "kernel/fork.c",
        "slab": source / "include/linux/slab.h",
        "slab_common": source / "mm/slab_common.c",
        "slub": source / "mm/slub.c",
        "cache": source / "arch/arm64/include/asm/cache.h",
    }
    missing = [str(path) for path in files.values() if not path.is_file()]
    if missing:
        raise SystemExit("missing source input: " + ", ".join(missing))
    config = parse_config(config_path)
    for key in ("CONFIG_ARM64", "CONFIG_FUTEX", "CONFIG_RT_MUTEXES", "CONFIG_SLUB"):
        if config.get(key) is not True:
            raise SystemExit(f"required config is not enabled: {key}")

    ptr = 8
    rb = layout([("parent_color", ptr, ptr), ("right", ptr, ptr), ("left", ptr, ptr)])
    waiter_fields = [("tree_entry", rb["sizeof"], ptr), ("pi_tree_entry", rb["sizeof"], ptr),
                     ("task", ptr, ptr), ("lock", ptr, ptr)]
    if config.get("CONFIG_DEBUG_RT_MUTEXES") is True:
        waiter_fields += [("ip", ptr, ptr), ("deadlock_task_pid", ptr, ptr), ("deadlock_lock", ptr, ptr)]
    waiter_fields.append(("prio", 4, 4))
    waiter = layout(waiter_fields)
    pipe = layout([("page", ptr, ptr), ("offset", 4, 4), ("len", 4, 4),
                   ("ops", ptr, ptr), ("flags", 4, 4), ("private", ptr, ptr)])
    mutex = layout([("count", 4, 4), ("wait_lock", 4, 4), ("wait_list", 16, ptr),
                    ("owner", ptr, ptr), ("osq", 4, 4)])
    ion = layout([("ref", 4, 4), ("node_or_list", rb["sizeof"], ptr), ("dev", ptr, ptr),
                  ("heap", ptr, ptr), ("flags", ptr, ptr), ("private_flags", ptr, ptr),
                  ("size", ptr, ptr), ("priv_virt_or_phys", ptr, ptr), ("lock", mutex["sizeof"], ptr),
                  ("kmap_cnt", 4, 4), ("vaddr", ptr, ptr), ("dmap_cnt", 4, 4),
                  ("sg_table", ptr, ptr), ("pages", ptr, ptr), ("vmas", 16, ptr),
                  ("handle_count", 4, 4), ("task_comm[16]", 16, 1), ("pid", 4, 4),
                  ("alloc_dbg[48]", 48, 1)])

    objects = {
        "task_struct": {
            "sizeof": 3488, "alignment": 16,
            "selected_offsets": {"pi_lock": 2068, "pi_waiters": 2080,
                                  "pi_waiters_leftmost": 2088, "pi_blocked_on": 2096},
            "storage": "dedicated task_struct kmem_cache",
            "cache_alignment": 64, "modeled_object_size": align(3488, 64), "slab_order": 0,
            "basis": "AArch64 clang record-layout probe using generated PS7331 config",
            "allocation": source_ref(files["fork"], 'kmem_cache_create("task_struct"',
                                       "fork_init creates the dedicated cache"),
        },
        "rt_mutex_waiter": {
            **waiter, "storage": "blocked task kernel stack; not a kmalloc object",
            "kmalloc_cache": "NOT_APPLICABLE",
            "basis": "source declaration plus AArch64 clang record-layout probe",
            "allocation": source_ref(files["futex"], "struct rt_mutex_waiter rt_waiter;",
                                       "futex_wait_requeue_pi declares a local waiter"),
            "documentation": source_ref(files["rtmutex_common"], "allocated on the kernel stack",
                                         "rtmutex_common documents stack storage"),
        },
        "pipe_buffer": {
            **pipe, "storage": "pipe_buffer array allocated by kzalloc",
            "single_element_cache": kmalloc_class(pipe["sizeof"]),
            "default_count": 16, "default_array_request": pipe["sizeof"] * 16,
            "default_array_cache": kmalloc_class(pipe["sizeof"] * 16),
            "allocation": source_ref(files["pipe"], "kzalloc(sizeof(struct pipe_buffer) * pipe_bufs",
                                       "alloc_pipe_info allocates an array"),
        },
        "ion_buffer": {
            **ion, "storage": "ION metadata allocated by kzalloc(sizeof(struct ion_buffer))",
            "cache": kmalloc_class(ion["sizeof"]),
            "allocation": source_ref(files["ion"], "kzalloc(sizeof(struct ion_buffer)",
                                       "ion_buffer_create allocates metadata"),
        },
    }
    selected = ["CONFIG_RANDOMIZE_BASE", "CONFIG_USERFAULTFD", "CONFIG_SLUB_CPU_PARTIAL",
                "CONFIG_SLUB_DEBUG", "CONFIG_SLUB_STATS", "CONFIG_KASAN", "CONFIG_DEBUG_INFO",
                "CONFIG_DEBUG_RT_MUTEXES", "CONFIG_MUTEX_SPIN_ON_OWNER", "CONFIG_ION",
                "CONFIG_SECCOMP", "CONFIG_CMDLINE", "CONFIG_ARM64_VA_BITS"]
    return {
        "schema": "phase6b-ps7331-layout-v1",
        "scope": {"device_execution": False, "kernel_execution": False, "race_trigger": False,
                   "memory_spray": False, "kaslr_slide": False, "root_operation": False},
        "inputs": {"source": str(source), "config": str(config_path),
                    "config_sha256": sha256(config_path), "abi": "AArch64 LP64",
                    "pointer_size": 8, "page_size": 4096, "kmalloc_min_alignment": 64,
                    "source_hashes": {name: sha256(path) for name, path in files.items()}},
        "config": {key: config.get(key) for key in selected},
        "objects": objects,
        "observations": [
            source_ref(files["rtmutex"], "current->pi_blocked_on = NULL;", "pre-fix cleanup target"),
            source_ref(files["rtmutex"], "if (unlikely(ret))", "proxy wrapper cleanup branch"),
            source_ref(files["futex"], "rt_mutex_start_proxy_lock(&pi_state->pi_mutex", "requeue-PI call site"),
            source_ref(files["slab"], "#define ARCH_KMALLOC_MINALIGN", "ARM64 kmalloc alignment source"),
            source_ref(files["slab_common"], "static s8 size_index[24]", "kmalloc size-index table"),
            source_ref(files["slub"], 'setup_slub_max_order', "SLUB max-order boot parameter"),
        ],
        "limitations": [
            "RANDOMIZE_BASE confirms KASLR is enabled; no runtime slide or kernel address is calculated.",
            "The modeled cache class does not prove an address, adjacency, reuse, or corruption event.",
            "The inspected rt_mutex_waiter is stack-resident, so it is not a direct SLUB spray target in this path.",
            "No identity mismatch, cleanup residue, memory effect, crash, or privilege transition is inferred.",
        ],
    }


def write_output(output: Path, result: dict, command: str) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    (output / "commands.txt").write_text(command + "\n", encoding="utf-8")
    (output / "model.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["object", "sizeof", "alignment", "storage", "cache", "allocation_file", "allocation_line"]
    rows = []
    for name, item in result["objects"].items():
        cache = item.get("cache") or item.get("default_array_cache") or item.get("single_element_cache") or {}
        cache_name = cache if isinstance(cache, str) else cache.get("cache", "")
        rows.append({"object": name, "sizeof": item.get("sizeof", ""), "alignment": item.get("alignment", ""),
                     "storage": item.get("storage", ""), "cache": cache_name,
                     "allocation_file": item.get("allocation", {}).get("file", ""),
                     "allocation_line": item.get("allocation", {}).get("line", "")})
    with (output / "layout.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    (output / "result.md").write_text(
        "# Phase 6B host-only layout model\n\n"
        "Device/kernel execution, race trigger, memory spray, KASLR slide calculation and root operation: **False**.\n\n"
        "| Object | Size | Storage | Modeled cache |\n|---|---:|---|---|\n" +
        "\n".join(f"| `{r['object']}` | {r['sizeof']} | {r['storage']} | {r['cache']} |" for r in rows) +
        "\n\n" + "\n".join(f"- Limitation: {value}" for value in result["limitations"]) + "\n",
        encoding="utf-8")
    manifest = []
    for path in sorted(output.iterdir()):
        if path.name != "sha256sums.txt":
            manifest.append(f"{sha256(path)}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "device_execution": False,
                          "source_root": str(args.source_root), "config": str(args.config),
                          "output": str(args.output)}, indent=2))
        return 0
    if not args.source_root.is_dir() or not args.config.is_file():
        parser.error("source root/config input is missing")
    write_output(args.output, build(args.source_root, args.config), " ".join(sys.argv))
    print(f"wrote host-only model: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
