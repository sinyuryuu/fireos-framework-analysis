# Phase 5BR evidence index

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| `P5BR-SEARCH-001` | Bounded public-web search | `artifacts/phase5/phase5br-exact-artifact-search-20260804-01/queries.tsv` | No exact PS7330 signed boot/Image/vmlinux in returned results | Confirmed, bounded search scope |
| `P5BR-DEVICE-001` | Existing exact-device read-only probe | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt` | Installed PS7330 boot read denied | Confirmed, access scope |
| `P5BR-SOURCE-001` | Official PS7330 source archive | `artifacts/phase5/ps7330-full-source-members-20260804-01/` | Exact build-selected source available and pre-fix-consistent | Confirmed, source scope |
| `P5BR-ADJACENT-001` | Official PS7331 local artifact | `firmware/extracted/PS7331/boot.img` | Adjacent version only; marked `VERSION_MISMATCH` for installed PS7330 | Confirmed, version scope |
| `P5BR-METADATA-001` | Amazon device specification | `findings/phase-5br-exact-artifact-search.md` | KFTRWI/trona/Android 9/Fire OS 7 device identity | Confirmed, metadata scope |

Search absence is not a global nonexistence proof and does not establish
exploitability or root.
