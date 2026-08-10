# Phase 6TM host-only provenance closure

This bundle extends Phase 6TJ–TL with the H2 custom-permission provenance check, the ION loader/process static graph, and the corrected public citation map for the PS7331 OTA evidence. It does not turn a capability, exported component, library caller, or recovery writer into proof of low-privilege reachability.

Generation HEAD: `c0281880bfd1bc76e97dfb33b2051c252d11bc55`.

## Safety boundary

Host-only analysis was used. No device, Binder bind/call, `service call`, driver open/ioctl, Root/exploit, OTA/recovery/sideload/flash, reboot, package/settings mutation, or partition write was performed.

## Inputs

- **6TM-A H2 permission:** `work/luna_worker_phase6tm_h2_permission_20260810.md` (4467cc5ee0ce3e00242167aa51567b65d0defd9dcc5344e792375cb622a6546e); `work/luna_worker_phase6tm_h2_permission_20260810.csv` (3913d9157e16b7ff3e99f8df3ce21824cb650688a6be3173b2cd4c0fffb30a35); 8 row(s).
- **6TM-B ION loader:** `work/luna_worker_phase6tn_ion_loader_graph_20260810.md` (961516629d95bb4c6bf1e4e68887938e865e51a900447e320f9143355e848295); `work/luna_worker_phase6tn_ion_loader_graph_20260810.csv` (567ab073bbdbe2d4b7bba938236161902180f253ae7ecf687ed257febb952ae6); 15 row(s).
- **6TM-C OTA citation repair:** `work/luna_worker_phase6tm_ota_public_repair_20260810.md` (86ff320b689cf484cb2d41f9e08b756fe1885244fc6060453bfda1b56079d083); `work/luna_worker_phase6tm_ota_public_repair_20260810.csv` (4099f4aff88c6ae340f202a36985ff9ad77440d24d48cd444ea8cb395e037618); 5 row(s).

Context hashes: `findings/phase-6tj-tl-report.md` (90e677aa19f058e6e4dd5adacba27448809649bbdb8f947a023e7181dbf302b0); `findings/phase-6tj-tl-evidence-index.md` (abd2a6c6033cbce978644af313354fe5c533f0344a3cda7e284cc1b36ebbec20); `output/tables/phase6tj-citation-map.csv` (28462d8bcaf444b2d66f9a04f8a21f9dc8c18989c9cba5ea115cb82a4b4c7967); `findings/phase-6ti-readonly-snapshot.md` (588d84c53ecf889a80ad6096e614512580e1cdb4db59ce5c5e0603f9a887f174)

## H2 permission result — confirmed boundary

The exact-build H2 XML-tree declares `com.amazon.alta.h2clientservice.permission.BIND_SERVICE` with raw `protectionLevel=0x2` (`signature`), and the exported H2 service references it. The custom holder, grant, and external production caller remain `UNKNOWN`; UID, placement, platform grants, and package signing digest do not prove custom-permission ownership. The recovered static path reaches user/profile lifecycle sinks but not HOME or PackageManager component-state selection.

Classification: `DECLARATION_CONFIRMED_PROVENANCE_OPEN`; low-privilege reachability is not established.

## ION loader result — bounded static evidence

The ION worker output is accepted only to the level supported by its exact-build loader, manifest, ELF, and SELinux evidence. A complete process→loaded library→device node→ioctl →privileged effect chain is required before any driver capability is treated as reachable. Missing loader, caller, permission, or downstream-effect edges remain `UNKNOWN`. No HOME, package-state, credential, OTA, or root effect is inferred from library presence alone.

## OTA citation result — provenance correction

The canonical citation map separates public committed manifests and derived static outputs from local-only raw OTA/extracted paths. TG-05 uses the `phase6mk...-04` registration table and TG-06 keeps selected-functions, direct-call-edges, and summary hashes distinct. These corrections change citation scope, not device behavior or caller reachability.

## Evidence acceptance rule

A positive privilege or replacement finding requires caller → gate → identity/user scope → exact sink. `UNKNOWN` is not a negative finding, but it is also not permission to invoke an unverified Binder, service, driver, OTA, or boot path.

## CSV validation

Integrated rows: `28`; OTA citation rows: `5`; parse warnings: `0`.

Warnings:
- None detected.
