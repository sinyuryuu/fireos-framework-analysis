# Phase 6D：AOSP anchor 與 PS7331 `/init` pipeline 差異映射

## 判定摘要

**已證實：** 官方 AOSP Android 9 `system/core/init/selinux.cpp` 含有下列
policy-loader anchors，且本輪取得的 `android-9.0.0_r1` 與 `android-9.0.0_r61`
版本內容 SHA-256 相同：

| Function | Lines |
|---|---:|
| `StatusFromCmdline` | 78–89 |
| `IsEnforcing` | 91–96 |
| `FindPrecompiledSplitPolicy` | 201–236 |
| `LoadSplitPolicy` | 256–367 |
| `LoadMonolithicPolicy` | 369–376 |
| `LoadPolicy` | 378–380 |
| `SelinuxInitialize` | 384–406 |

**已證實：** PS7331 stripped `/init` 的既有指令級證據包含：

- `0x41bd60`：`androidboot.selinux`／`permissive` 比較候選；
- `0x41ad00`：rootable policy path-builder 候選；
- `0x41af80`：standard policy path-builder 候選；
- `0x41be00`：兩組 path 都會到達的 stripped common-helper 候選；
- `0x41be48`：helper 入口附近以 `w5` 分支的指令；
- `0x41bf00`：standard hash marker 參考候選。

**高可信推論：** 這些 binary regions 與 AOSP split-policy pipeline 在功能形狀上
相容：property／precompiled-hash／policy-path／load-helper 形成一個 decision
surface。`rootable_*` path 是實際 code-level reference，不只是 `strings` 殘留。

**待驗證：** stripped binary 沒有符號，故仍不能把 `0x41ad00` 直接命名為
`LoadSplitPolicy`，也不能把 `w5=1/0` 直接命名為 rootable/standard selection
flag。`0x4041fc` 的 caller、`0x41bd60` 的 caller／回傳欄位、以及目前 stock boot
實際載入的 policy blob 均未取得直接證據。

**無法取得證據：** GPL tarball 沒有 `system/core/init`，因此本輪沒有 Amazon
`selinux.cpp` source-level diff。這不是「Amazon 沒修改」的證明。

**因風險拒絕測試：** 修改 boot property／cmdline、選擇 rootable policy、讀寫
live SELinux policy、remount、bootloader／fastboot、刷寫 image、執行 futex race、
kernel panic、heap shaping 或提權 payload。

## AOSP pipeline anchor

在 AOSP anchor 中，`LoadPolicy()` 依 `IsSplitPolicyDevice()` 選擇
`LoadSplitPolicy()` 或 `LoadMonolithicPolicy()`；split path 先由
`FindPrecompiledSplitPolicy()` 檢查 precompiled policy 與 platform/mapping hash，
不適用時才走編譯／載入 fallback。這是比較基準，不是對 PS7331 binary 的完整
反編譯結論。

## 機器可讀輸出

- `artifacts/phase6d/phase6d-init-pipeline-diff-20260804-01/pipeline.json`
- `artifacts/phase6d/phase6d-init-pipeline-diff-20260804-01/anchor-map.csv`
- `artifacts/phase6d/phase6d-init-pipeline-diff-20260804-01/pipeline-knowledge-base.mmd`
- `output/call-graphs/phase6d-init-pipeline-knowledge-base.mmd`

Pipeline map：

```text
boot cmdline/properties
  -> /init decision surface
     -> StatusFromCmdline candidate
     -> FindPrecompiledSplitPolicy candidate
        -> LoadSplitPolicy candidate
           -> common helper candidate
              -> active policy [UNRESOLVED]
```

## 完整性

| Artifact | SHA-256 |
|---|---|
| `pipeline.json` | `a1a98ed3c5ddd2d736f00061f7d4a6cb26e6b0fea64eaec4ab23cb0969e0b563` |
| `anchor-map.csv` | `4697d1794f5dc771f9a9e09c6cad66244fc8b286f573566ad87e124fbbc2b4b3` |
| `pipeline-knowledge-base.mmd` | `509f566664345ec1dcb8e6f72d100752fef55ada95d3d832e654ad33051a17f5` |

## 重現

```sh
python3 tools/scripts/fetch_aosp9_init_baseline.sh --dry-run \
  --output aosp/android-9/init-source-YYYYMMDD-NN
python3 tools/scripts/fetch_aosp9_init_baseline.sh \
  --output aosp/android-9/init-source-YYYYMMDD-NN

python3 tools/scripts/analyze_phase6d_init_pipeline.py --dry-run \
  --aosp-root aosp/android-9/init-source-YYYYMMDD-NN \
  --audit-json artifacts/phase6c/phase6c-init-policy-loader-audit-20260804-02/policy-loader-audit.json \
  --inventory artifacts/phase6d/phase6d-init-property-inventory-20260804-01/property-cmdline-inventory.json \
  --output artifacts/phase6d/phase6d-init-pipeline-diff-YYYYMMDD-NN
```

所有工具均拒絕覆寫既有輸出；AOSP fetch 僅取官方 source，不接觸裝置。
