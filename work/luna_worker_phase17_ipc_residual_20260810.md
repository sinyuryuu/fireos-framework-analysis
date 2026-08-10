# Phase 17, branch B — residual Amazon Framework/System IPC

Host-side static review only, dated 2026-08-10. No ADB/device contact, service call, Binder transaction or guessed parcel, package/settings mutation, exploit/root/OTA action, or runtime replay was performed.

The CSV contains 7 non-duplicate residual rows. Concrete new edges are the AmazonPackageManager flags read path and its consumers: PackageRecency gates `PACKAGE_RECENCY_NOTIFICATION`; GameMode tests bit `0x2`; AppCompat tests bit `0x1`. The mutators are gated by `amazon.permission.ADD_RM_PKG_METADATA` (`signature|amazon`) and persist `AmazonApplicationFlags` through `writeToFile()`. Exact privileged callers and cross-user validation remain open.

`SettingsDBUtils` and the OOBE `PackageHelper` are separate rows because their settings/component sinks are proven statically while receiver-delivery user and provider/PackageManager enforcement remain unresolved. The already-closed protected OTA sender/receiver route is not duplicated. No exact User-0 HOME replacement, UID-changing sink, or ordinary caller reachability is established.

Static capability, caller reachability, and runtime effect are kept distinct in every row. The saved service-context evidence records shell UID 2000 `service_manager find` denial for private Amazon services; no Binder method is claimed invocable from shell. Runtime fields only cite existing saved observations and do not imply a new run.

Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:23294-232e4,95889-96009,134746-134758,181605-181607,95417-95640`; OOBE sources `SettingsDBUtils.java:21-74`, `OOBEActivationHelper.java:53-75`, `PackageHelper.java:11-22`; `artifacts/phase6mo-oobe-context-user-scope-20260810-01/context-user-scope.csv`; protected-broadcast and permission evidence `artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/manifest-aapt.xmltree.txt:551-554,1937-1938`.

Row count (excluding header): 7. CSV QA: fixed 13-field header; all rows 13 fields; duplicate IDs 0; duplicate complete rows 0.

SHA-256:

- CSV: `2644d6d4f8c1037786ebc3cb9aa5d0b390696fad211ebdee119af1dbdb80a407`
- Markdown: computed in the final handoff after this file was written.

Safe next steps remain host-only caller, manifest, Context/user, and provider-enforcement joins. No Binder invocation is needed.
