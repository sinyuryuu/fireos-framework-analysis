# Phase 6TM-C — host-only OTA citation-map repair

Date: 2026-08-10. Read-only basis: git tree `c0281880bfd1bc76e97dfb33b2051c252d11bc55`, the Phase 6TG/6TL/6TJ reports and tables, and committed/public artifact manifests plus preserved local firmware/source path references.

Safety boundary: no OTA was downloaded, constructed, modified, or executed. No recovery, sideload, flash, reboot, Binder, driver, root, exploit, device mutation, or partition write was performed. This report adds only the two requested new files; existing files were not edited.

## Result

The canonical public anchors are:

- PS7331 OTA/source mapping: `artifacts/phase5/ps7331-official-update-source-20260804-01/source-map.tsv` (artifact SHA-256 `0a7eb0ac06352eb33b9ac5ce8416637b6819c67c1389bc52937ff893c836f6be`) and `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/summary.json` (artifact SHA-256 `54c59cfc445e1b7ff7d6be7dc21b02668260e24b66dbcd53c3c2cf256928395a`). These record the official route, PS7331 identity, 1,301,005,356-byte package, and OTA SHA-256 `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`.
- OTA member/Edify manifest: `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/members.tsv` (artifact SHA-256 `1f18be825bb2b250080cb05c42fc92c66631d7eb2d6493bc40e9d25526fed33b`) and `updater-script.txt` (member SHA-256 `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`). The latter is a committed derived text output, not the raw extracted directory.
- PS7331 boot manifest: `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/boot-image-metadata.json` (Git blob `331bbf3d29b09f07875dfefe005e2dadf627bee5`; image SHA-256 `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`; kernel field SHA-256 `a608a5f99c155dc8e8b12b308528cbd17175b47199985d017613f9e2fbb1edba`). This is a host-only derived boot-image manifest; the referenced `firmware/extracted/PS7331/boot.img` is not a public raw-tree path.
- TG-05 dispatch: `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv` (artifact SHA-256 `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24`), with summary SHA-256 `4cf463ec498b74e6460fb598f7ce5e5756418aaa5c2ac5767009c22e9c29b9fe`. This is host-only static dispatch evidence, not a shell/public API or execution result.
- TG-06 cache flow: `artifacts/phase6ne-updater-cache-flow-20260810-03/selected-functions.csv` (`113caf07b212241f85c3ca4823b68a1d2b6a77d859a712efdd050548e04c7937`), `direct-call-edges.csv` (`d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477`), and `summary.json` (`1cb21f3de9403c54e080c27f2d285d8e76a0e3a970063a250cdcc3c222a98b60`). The previous citation incorrectly used the summary hash for the selected-functions source.

## Replacement map

| TG row | Replacement citation | Classification | Exact claim boundary |
|---|---|---|---|
| TG-01 | `artifacts/phase5/ps7331-official-update-source-20260804-01/source-map.tsv` (`0a7eb0…`), `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/summary.json` (`54c59c…`), and `firmware/manifests/OTA-20260803-01/sha256sums.txt` (`43cab7…`). Preserve OTA SHA `9f50d2…`; do not cite the raw archive as a public-tree file. | Raw archive: `LOCAL_ONLY`; mapping/identity: `PUBLIC_CONFIRMED`. | Public commit confirms the official PS7331 route, package identity, size and hash record. It does not make `firmware/original/update-kindle-...bin` present in the public tree. | 
| TG-03 | `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt` (member SHA `4a61d6…`, manifest artifact SHA `4a61d6…`), supported by `members.tsv` (`1f18be…`); cite lines 1–24. | Script text: `DERIVED_OUTPUT` and `PUBLIC_CONFIRMED` as a committed artifact; raw extracted member path: `LOCAL_ONLY`. | Confirms the preserved script text and its fixed system/vendor/boot-chain/cache targets. It does not prove runtime execution or public presence of `firmware/extracted/PS7331/...`. |
| TG-04 | `artifacts/phase6ah/update-binary-validation-20260805-01/analysis.json` (Git blob `ee29dc…`) and its `sha256sums.txt` (Git blob `3f8508…`), recording input `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` with SHA `02643fa…`. | Input binary path: `LOCAL_ONLY`; committed hash/input manifest and CFG result: `PUBLIC_CONFIRMED` + `DERIVED_OUTPUT`. | Public commit confirms the hash-recorded PS7331 native input and host-only static analysis. It does not contain the raw `update-binary` file itself, nor prove execution/caller reachability. |
| TG-05 | Replace `artifacts/phase6mk-updater-dispatch-20260810-01/registration-dispatch.csv` and `443c…` with `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv`, file SHA `d88e35ec…`; optionally pair with `summary.json` SHA `4cf46340…`. | `PUBLIC_CONFIRMED` artifact; interpretation is `DERIVED_OUTPUT`. | Confirms the committed 24-row static registration/dispatch table. It is not a shell API, Binder route, runtime execution, or low-privilege caller proof. |
| TG-06 | Replace the conflated source citation with three records: `selected-functions.csv` SHA `113caf07…`, `direct-call-edges.csv` SHA `d653e4a8…`, and `summary.json` SHA `1cb21f3d…`, all under `artifacts/phase6ne-updater-cache-flow-20260810-03/`. | Files: `PUBLIC_CONFIRMED` committed artifacts; analysis: `DERIVED_OUTPUT`; full canonicalization/dataflow: `UNKNOWN`. | Confirms only the bounded static `PerformBlockImageUpdate → CacheSizeCheck` relation and observed markers. Full canonicalization input/output, traversal behavior, runtime behavior and caller reachability remain `UNKNOWN`. |

## Explicit negative/provenance rules

1. A path appearing inside a committed manifest is not evidence that the referenced raw OTA, extracted directory, `boot.img`, or `update-binary` is itself in the public git tree.
2. A SHA recorded in a manifest is labeled by scope: OTA/member/input SHA-256 is distinct from the Git blob SHA of the manifest file. The CSV uses separate fields for these scopes.
3. `PUBLIC_CONFIRMED` means the cited record and its bytes are verifiable from HEAD; `DERIVED_OUTPUT` means a host-only extraction/static-analysis output; `LOCAL_ONLY` means a preserved local/raw path not present in HEAD; `UNKNOWN` is retained where the cited evidence does not close execution, caller, or canonicalization behavior.

