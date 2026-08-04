# Phase 5BP evidence index

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| `P5BP-ARCHIVE-001` | Amazon official PS7330 source archive | `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2` | SHA-256 `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665` | Confirmed, archive scope |
| `P5BP-SCRIPT-001` | Preserved Amazon build config | `artifacts/phase5/ps7330-build-scripts-20260804-01/build_kernel_config.sh:9–18` | Exact `mt8183/4.4`, `trona_defconfig`, arm64, expected image names | Confirmed |
| `P5BP-SCRIPT-002` | Preserved Amazon build config | `.../build_kernel_config.sh:12–24` | AOSP GCC prebuilt repo, branch `llvm-r383902b`, prefix, Clang recommendation | Confirmed |
| `P5BP-SCRIPT-003` | Preserved Amazon build script | `.../build_kernel.sh:130–185` | Defconfig, full make, copy and output validation flow | Confirmed |
| `P5BP-SCRIPT-004` | Preserved Amazon build script | `.../build_kernel.sh:201–207` | Toolchain clone fallback and platform tar extraction | Confirmed |
| `P5BP-SCAN-001` | Host-only static scan | `artifacts/phase5/ps7330-build-scripts-20260804-01/commands.txt` | No visible executable patch/overlay/signing step in these two files | Confirmed, scan scope |
| `P5BP-HASH-001` | SHA-256 manifest | `artifacts/phase5/ps7330-build-scripts-20260804-01/sha256sums.txt` | Preserved script and ledger hashes | Confirmed |
| `P5BO-CROSS-001` | Exact PS7330/PS7331 source comparison | `artifacts/phase5/phase5bo-exact-build-source-marker-20260804-01/summary.json` | Both exact build-selected source markers are pre-fix | Confirmed, source scope |
| `P5BO-BOOT-001` | Read-only device probe | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt` | PS7330 boot pull denied | Confirmed, access scope |
| `P5BO-DEVICE-001` | Read-only device postcheck | `adb/phase5/PHASE5BO-DEVICE-POSTCHECK-20260804-01/` | Device remains PS7330, green verified boot, enforcing SELinux, ADB connected | Confirmed, runtime scope |

No entry in this index proves signed-binary equivalence, exploitability, kernel
offsets, root, or safe upgradeability.
