# Phase 6AI evidence index

All Phase 6AI analysis is host-only. No device command was executed by the
Phase 6AI audit script. The live ACL rows below are carried forward from the
earlier explicit-serial read-only capture and are not re-read or modified here.

| Evidence ID | Source / SHA-256 | Location | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| 6AI-DL-001 | `artifacts/phase6ai/denylist-flow-20260805-02/summary.json` and `sha256sums.txt` | audit metadata | `device_contacted=false`, `unsafe_operations_performed=false`, 16 rows | Reproducible host-only scope | Confirmed |
| 6AI-DL-002 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` / `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | `ControlProtectedPackagesCallback.shouldProtectPackage`, lines 97034-97049, offsets `0x06a61a-0x06a640` | System/privileged check, deny-list lookup, UID 2000 comparison | Amazon protected-package predicate | Confirmed |
| 6AI-DL-003 | `decompiled/baksmali/vdexExtractor/services/disassembly.log` / `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` | `VendorProtectedPackagesCallback.callShouldProtectPackage`, lines 539225-539239 | Iterates callbacks and ORs their result | Fire OS callback fan-in | Confirmed |
| 6AI-DL-004 | `artifacts/amazon-services/amazonpackagemanager_fosinit.xml` / `eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286` | `VendorProtectedPackagesCallback` registration, XML line 22 | Amazon callback is `SYSTEMSERVER` | Registration provenance | Confirmed |
| 6AI-DL-005 | fosservices disassembly / same hash as 6AI-DL-002 | `AmazonPackageManagerService.onBootPhase`, lines 96087-96105 | Phase 500 constructs `DenyListArcusHelper` | Startup producer entry | Confirmed |
| 6AI-DL-006 | fosservices disassembly / same hash | `DenyListArcusHelper.<init>`, lines 97161-97200 | Device-protected `PackageManagerDenyList` store and handler are initialized | Persistent store shape | Confirmed |
| 6AI-DL-007 | fosservices disassembly / same hash | `ControlProtectedPackagesCallback.getSharedPrefPackages`, lines 96969-96992 | Reads `DenyListKeyPackages` string set | Consumer read path | Confirmed |
| 6AI-DL-008 | fosservices disassembly / same hash | `extractListFromResorces`, lines 97231-97251 | Seeds only if `DenyListKeyPackages` is absent; commits HashSet | Initial seed condition | Confirmed |
| 6AI-DL-009 | fosservices disassembly / same hash | `processJSON`, lines 97326-97426 | Raw resource `0x7e05000a`, JSON key `packages_deny_list` | Resource-backed source; content not mapped | Confirmed / content pending |
| 6AI-DL-010 | fosservices disassembly / same hash | `initialize`, lines 97300-97325 | Reads `persist.sys.denylist_arcusid`; registers Arcus and sync ID | Refresh selector | Confirmed |
| 6AI-DL-011 | fosservices disassembly / same hash | `registerArcusBroadcastReceivers`, lines 97427-97451 | Registers `amazon.arcus.sync.<id>` and `.unmod.<id>` | Dynamic refresh trigger registration | Confirmed |
| 6AI-DL-012 | fosservices disassembly / same hash | `DenyListArcusHelper$2.onReceive`, lines 97109-97145 | Matching action posts refresh worker | Trigger-to-worker edge | Confirmed |
| 6AI-DL-013 | fosservices disassembly / same hash | `DenyListArcusHelper$2$1.run`, lines 97079-97100 | `openConfiguration(arcusId)` feeds `getDenyList` | Arcus payload acquisition | Confirmed |
| 6AI-DL-014 | fosservices disassembly / same hash | `getDenyList`, lines 97252-97299 | Parses JSON array and calls writer | Runtime replacement parser | Confirmed |
| 6AI-DL-015 | fosservices disassembly / same hash | `saveProtectedPackages`, lines 97454-97483 | Removes old key, writes new set, commits | Persistent writer | Confirmed |
| 6AI-DL-016 | artifact flow details / hash in `artifacts/phase6ai/denylist-flow-20260805-02/sha256sums.txt` | symbol occurrence inventory | No public shell/Binder writer found in saved scope; direct writer call is internal | Scope-limited negative evidence | Strong evidence |
| 6AI-DL-017 | `artifacts/phase6k/readonly-device-20260805-01/deny_list_ls.stdout.txt` / `9f7ad63a2514d38b0b488ff69de9136f3de064c2c08ee1bc26d5fcbd89c4e76c`; `deny_list_stat.stdout.txt` / `0d1fda69c255b17cb44cb0a6dea15d796027c5ec0e2bd309648b503dd2a71438`; denied listing stderr / `5b3f6d3330a214881f41dd9e8f720d7320535f7e964b0032612813cda7771b89` | saved read-only capture | `system:system`, mode 660, 2645 bytes; content listing denied | Shell cannot establish literal membership | Confirmed metadata / membership pending |

## Negative-evidence boundary

No evidence ID in this index asserts that `com.amazon.firelauncher` was read from
the deny-list file. The exact set remains unavailable to the shell capture. The
previous Fire Launcher rejection is supporting runtime correlation, not a literal
membership dump.
