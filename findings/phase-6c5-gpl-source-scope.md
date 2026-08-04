# Phase 6C.5：PS7331 GPL 原始碼範圍確認

## 結論

**已證實：** `firmware/extracted/PS7331-SOURCE-20250617` 是有限範圍的 Amazon GPL
source package。它包含 MT8183 4.4 kernel 與 Amazon device/kernel support，包括：

- `platform/kernel/mediatek/mt8183/4.4/kernel/futex.c`
- `platform/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`
- `platform/device/amazon`

**已證實：** 下列 Android `/init` 原始碼不存在：

- `platform/system/core/init/`
- `platform/system/core/init/selinux.cpp`
- `platform/system/core/init/selinux.h`

全域命名檔案掃描只找到 kernel／外部元件的 `selinux.h`，沒有
`rootable_*` 或 `sepolicy` init policy-loader source。這些結果由機器可讀的
`scope.json`、`scope.csv` 與 manifest 封存。

**高可信推論：** 這份 GPL tarball 可作為 PS7331 kernel／GhostLock provenance
基準，但不能直接提供 Amazon `/init` 的 `selinux.cpp` 差異。`/init` pipeline
仍需以 AOSP source anchor 加上 stripped binary 的主機端控制流分析。

**待驗證：** Amazon 是否在未公開的 Android platform overlay、私有 build input
或另一個 source package 中維護 `/init` 修改。

**已排除：** 「GPL tarball 沒有 `system/core/init`」不等於 PS7331 `/init` 沒有
Amazon 修改；它只排除了本 tarball 作為該 diff 的直接 source。也沒有因檔名命中
`selinux` 就把 kernel header 誤認為 init policy loader。

## 完整性

| Artifact | SHA-256 |
|---|---|
| `scope.json` | `8ab20dd811f93b30163f0f5b5f8dadb75bb3e73cc8199571a0f62f9709963221` |
| `scope.csv` | `99b4c831b30d2ffd5863b55480605426946568afdc4b5aab1e6b18525660e163` |
| `result.md` | `d795172e4d8202b426d96491f1085bf6f596dd401cff8fbc879ad5c6837d49a9` |

原始 source 未覆寫；本輪只新增 audit artifact。

## 重現

```sh
python3 tools/scripts/audit_phase6c5_gpl_source_scope.py --dry-run \
  --source-root firmware/extracted/PS7331-SOURCE-20250617 \
  --output artifacts/phase6c5/gpl-source-scope-YYYYMMDD-NN

python3 tools/scripts/audit_phase6c5_gpl_source_scope.py \
  --source-root firmware/extracted/PS7331-SOURCE-20250617 \
  --output artifacts/phase6c5/gpl-source-scope-YYYYMMDD-NN
```

本工具為 host-only，不 build／execute source，不接觸裝置。
