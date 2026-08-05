# Phase 6AN evidence index

| Evidence ID | Source | Observed result | Confidence |
|---|---|---|---|
| `6AN-GPL-001` | `fireos.tar` member inventory | No system/core, frameworks/base, Amazon namespace, init, selinux.cpp, or deny-list path; only three packages/apps members | Confirmed |
| `6AN-GPL-002` | `platform.tar` member inventory | 150 generic system/core members, but no system/core/init, frameworks/base, Amazon namespace, selinux.cpp, or deny-list path | Confirmed |
| `6AN-GPL-003` | Both archive hashes and inventories | GPL package is not a complete Amazon framework/resource source tree | Strong evidence |
| `6AN-GPL-004` | Phase 6AM plus resource investigation | resource ID 0x7e05000a remains unresolved from the available base framework artifact; runtime overlay/package scope is pending | Hypothesis |

Device contact: none. Extraction: none. Source execution: none. Partition or
package mutation: none.
