# Phase 6AA evidence index

本階段所有結果均為保存輸入的 host-only 分析。

| Evidence ID | Source / SHA-256 | Location | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| `6AA-001` | Phase 6W candidate CSV / `99c43f368b46d23727b16a0562cac2f03e2c4cd6b50fb4ee62c4e895f6c0488f` | `high-impact-exported-candidates.csv` | 6 rows classified `EXPORTED_LOWER_OR_NONSTANDARD_PROTECTION`; 5 unique components | over-approximated manifest triage input | Confirmed |
| `6AA-002` | OOBE manifest / `bcc51d83ee74bbc230b774a52684e3e4cdb5cbc6cff7be673e6e3979037275ff` | `manifest.txt:144-146` | `OOBE_PERMISSION` has protection value `0x2` | package-defined signature-level component permission | Confirmed |
| `6AA-003` | OOBE manifest / same as `6AA-002` | `manifest.txt:475-477,599-602,656-659,926-930` | four OOBE activities require `OOBE_PERMISSION` | implicit export does not remove component permission guard | Confirmed |
| `6AA-004` | OOBE source / `OOBELauncherV2.java` hash is included in Phase 6AA artifact input manifest | `OOBELauncherV2.java:67-71` | guarded activity enables OOBE Home and starts OOBE flow | high-impact setup side effect, not ordinary HOME API | Confirmed |
| `6AA-005` | Fire Launcher manifest / `ba88dc674466a2c4561e7258586ca31f739e8527153d81dc6cd2a262a3f2fdab` | `AndroidManifest.xml:13-17,508-511` | BADGING is normal; provider is exported with write permission | manifest surface is not sufficient to infer arbitrary write | Confirmed |
| `6AA-006` | `BadgingProvider.java` / hash is included in Phase 6AA artifact input manifest | `BadgingProvider.java:58-109` | caller UID packages must contain target `pkgName` before `updateBadge` | method-level caller-package guard | Strong evidence |
| `6AA-007` | Phase 6AA summary / `artifacts/phase6aa/exposed-component-closure-20260805-01/summary.json` | host-only closure | 4 signature guards + 1 custom caller guard; no device contact | candidate set reduced without runtime mutation | Confirmed |

## Safety boundary

No activity was started, no ContentProvider was queried or updated, no broadcast or
Binder transaction was sent, and no package/settings/OOBE state was changed.

