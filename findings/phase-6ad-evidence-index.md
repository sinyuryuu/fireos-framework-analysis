# Phase 6AD evidence index

| Evidence ID | Source / SHA-256 | Location | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| 6AD-INV-001 | Inventory summary / `0460db8ad5bfb5d50f2ca212da63a62be36fa699890e449ee13296d95510f57e` | `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/summary.json` | 28 APK、0 AAPT failures；classification=`CONFIRMED_IN_SCANNED_SOURCES` | inventory 執行完整 | Confirmed |
| 6AD-INV-002 | Inventory CSV / `248bc559e73f5abe77125b0fbcd92b54575b6bf2fe75cf48c5761549d9d49c4b` | `protected-broadcast-inventory.csv` row 28 | 目標 action 唯一出現在 `android.amazon.perm.apk`；158 declarations | 保存 APK scope 的唯一來源 | Confirmed |
| 6AD-INV-003 | APK / `5b72bdfcfb91b28d2c751e548f60d406de5c3cbb235e47e232014abdebcdc058` | `artifacts/phase6ac/android-amazon-perm-device-20260805-01/android.amazon.perm.apk` | source package manifest contains target protected-broadcast | action provenance | Confirmed |
| 6AD-INV-004 | Input hash table / `b41bb0f2ab3e22b09c9210b7ea856745a5fcb764d814deed163569446ad24b03` | `input-sha256.csv` | 28 個輸入 APK 均有 SHA-256 | 可重現 input scope | Confirmed |
| 6AD-INV-005 | Inventory tool | `tools/scripts/audit_phase6ac_protected_broadcast_inventory.py` | 支援 explicit roots、`--dry-run`、拒絕覆寫、host-only parser | 可重現且不改動輸入 | Confirmed |
| 6AD-INV-006 | Graph / `8e7e6afadaeceb1a58f6302f92336711cac3d68575646ffafdc2727775937112` | `protected-broadcast-inventory.mmd` | manifest → PackageParser → PMS set → caller check | 靜態控制鏈摘要 | Strong evidence |
| 6AD-INV-007 | Runtime boundary | `findings/phase-6ac-protected-broadcast-source.md`; `findings/phase-6r-bootafter-system-ota-authorization.md` | 完整 runtime set、shell caller path 與自然 OTA observation 尚未取得 | 不把 artifact inventory 過度外推 | Hypothesis / pending |

## Safety

本階段沒有接觸裝置；沒有送出 broadcast、Binder transaction、OTA/recovery
請求、設定或 package mutation。完整 output hash 位於：

`artifacts/phase6ad/protected-broadcast-inventory-20260805-01/sha256sums.txt`
