# Phase 5DI — additional preserved ODEX futex surface

日期：2026-08-04

本輪補掃描兩個已存在工作樹、但未列入 Phase 5DD 16-file native inventory
的 ODEX：

- artifacts/services/services.odex
- artifacts/services/fosservices.odex

兩者都是 AArch64 ELF。只使用 file、strings、nm metadata；沒有執行
ODEX/ELF、反組譯 exploit、接觸裝置或產生 syscall／payload。

## 結果

| Artifact | SHA-256 | Result |
|---|---|---|
| services.odex | cec4a2eb32e6a68f515b0d1321b2fb63a736cc1d7fc5ba5259a19b582f9e0e02 | no named requeue-PI marker |
| fosservices.odex | abb1efeb7ed954b53b8fb8dc2c2d98a4107fa46d21bbae76065a31b6d4f42446 | no named requeue-PI marker |

完整 inventory 與 output hashes：

artifacts/phase5/phase5di-additional-odex-futex-surface-20260804-01/

## 判定

- **已證實：** 這兩個 preserved ODEX 的可見 strings/symbol surface 沒有
  futex、rtmutex、requeue-PI 或 generic syscall marker。
- **高可信推論：** 目前保存的 Fire native／ODEX artifact 集合仍沒有
  named requeue-PI caller 證據。
- **待驗證：** stripped/inline/numeric syscall、未擷取 APK split 或其他
  native component 仍可能不出現在 marker scan。
- **已排除／不支持：** 把 ODEX marker absence 當作 runtime impossibility。
- **因風險拒絕測試：** 將 ODEX 執行、推送至平板、觸發 futex race 或嘗試
  kernel memory／root chain。
