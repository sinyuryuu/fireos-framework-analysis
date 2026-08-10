# Phase 20E — PS7331 provenance/source scope

日期：2026-08-10。只做現有工作區的主機端 path、SHA-256、版本與 source-scope 對齊；未下載、未執行外部工具或保存的 script/ELF/updater、未接觸設備、未修改既有檔案。本輪只新增本報告與同名 CSV。

## 結論

現有證據支持以下新結論，且只限 PS7331 或明確標註的 PS7330 provenance：

1. PS7331 GPL source tar、`platform.tar`、`fireos.tar` 與 kernel source path/hash 可支持 PS7331 kernel/Amazon-driver/source provenance；它不是完整 Amazon framework、`/init`、SELinux 或 private userspace source drop。
2. PS7331 `boot.img`、unpacked kernel/Image、OTA/bin、`ota.prop`、`build.prop` 與 selected/compiled extraction artifacts 的版本欄位均對齊 `PS7331.4463N` / `trona` / security patch `2024-08-01`。這些 artifacts 不是 exact PS7330 signed boot/kernel/OTA。
3. PS7331 extracted framework/services JAR/VDEX/ODEX 是可用的 PS7331 static-analysis inputs；但 `artifacts/framework/*`、`artifacts/services/*` 的同名檔案有一部分是 2026-08-03 從設備 pull 的 PS7330-baseline capture。它們必須按 path provenance 分層，不能只因某些 SHA 相同就宣稱整套 PS7331 或整套 PS7330 build 相同。
4. 既有 reports 大致支持上述分層，但有些報告把 device-pulled `artifacts/framework`/`artifacts/services` 稱為「exact-build inputs」而未在同一行標出 PS7330 capture provenance。P20E 將其修正為：內容可供 host-only static analysis；版本歸屬以來源 path/manifest 為準；不把它們升格成 PS7331 OTA payload。
5. Phase 19 的 `build.prop` hash gap 已由既有 Phase 6MV inventory 補齊：`068b257362514773113671a7be67ff1288c484382ee43694872a19dbcb93e15e`。

## P20E evidence ledger

| ID | 內容 | path / provenance | SHA-256 | 對齊結果 |
|---|---|---|---|---|
| P20E-001 | PS7331 official GPL outer source | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | exact PS7331 source input；2,563,328,975 bytes、35 members、EOF=true、未執行 |
| P20E-002 | PS7331 platform GPL nested source | `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | 138,574 members；kernel/device/platform provenance；沒有完整 `frameworks/base`、Amazon namespace 或 `system/core/init` source member |
| P20E-003 | PS7331 FireOS GPL nested source | `firmware/extracted/PS7331-SOURCE-20250617/fireos.tar` | `bb7030296545dd45edcf47d3e742043e7813852844f4b0fbbe8d223899b369` | 53,549 members；有限 FireOS/GPL scope；沒有完整 `system/core/init`、`frameworks/base`、Amazon private framework source |
| P20E-004 | PS7331 kernel source | `.../platform/kernel/mediatek/mt8183/4.4/kernel/futex.c`；`.../kernel/locking/rtmutex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`；`6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | PS7331 source-family kernel evidence；可支持 source semantics，不支持 PS7330 signed binary semantics |
| P20E-005 | PS7331 boot and Image | `firmware/extracted/PS7331/boot.img`；`boot_unpacked/kernel`；`boot_unpacked/Image` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`；`a608a5f99c155dc8e8b12b308528cbd17175b47199985d017613f9e2fbb1edba`；`10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d` | PS7331 boot/Image only；source/Image report supports PS7331 semantic comparison, not exact PS7330 booted kernel |
| P20E-006 | PS7331 OTA container | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | exact PS7331 OTA container; `ota-type=BLOCK`, `pre-device=trona`, PS7331.4463N; no execution/reachability claim |
| P20E-007 | OTA updater members | `firmware/extracted/PS7331/META-INF/com/google/android/{update-binary,updater-script}` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`；`4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | PS7331 OTA static capability only；not a device mutation or PS7330 writer proof |
| P20E-008 | PS7331 OTA/build properties | `firmware/extracted/PS7331/ota.prop`；`META-INF/com/android/metadata`；`system/build.prop` | `ota.prop=f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded`; `build.prop=068b257362514773113671a7be67ff1288c484382ee43694872a19dbcb93e15e` | Fire OS 7.3.3.1; `PS7331.4463N`; product/device/board `trona`; fingerprint `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`; patch `2024-08-01` |
| P20E-009 | PS7331 selected framework/services | `firmware/extracted/PS7331/selected/system/framework/{framework.jar,services.jar,fosframework.jar,fosservices.jar}` | `framework.jar=1c16f5976318fadcf7add92c518a93896f99e2a78f742b7347d8539103264882`; `services.jar=1c16f5976318fadcf7add92c518a93896f99e2a78f742b7347d8539103264882`; `fosframework.jar=ef1491b8850be6d6cab0101d6b4fcf34e1dabb13cd2d08e3d72e615ddb21d188`; `fosservices.jar=364603c0228058973ed976ff1bef51c3cab2fa8fc163ec63c727157bb92dec96` | PS7331 extracted payload scope；JAR hash equality with a PS7330-pulled path is byte equality only, not full build identity |
| P20E-010 | PS7331 compiled framework/services | `firmware/extracted/PS7331/compiled-02/system/framework/{oat/arm64/services.vdex,services.odex,fosservices.vdex,fosservices.odex,boot-framework.vdex,boot-fosframework.vdex}` | `b3cdefcb8e150c478983195657a4ebaeb02ae9b9139756e09737361992b3f297`; `a4cee1acdaae7fcee905697979c4f9299bcc884bb1bcf55a5ee9f4034dc8f8d2`; `e20411372ebfa1b8ec605d2903e8894392be1333d71746a659818b06876d8c1a`; `8f8959b335a384af020e80cafffd622cbfed2a0d2cffc713e86077b97a092f0a`; `992324d14a6e8c439dfa9578bbf0cd94ca7038c9cf3e5388d399334373958642`; `00f7a0e1a77b9059051df6c8b3c88a5318a741b0c7cf3873fe9bfbb382a1e4dd` | PS7331 compiled extraction scope; differs from 2026-08-03 device-pulled VDEX/ODEX hashes |
| P20E-011 | Device-pulled framework/services comparison set | `firmware/manifests/ARTIFACT-20260803-01/02/command_manifest.tsv`; `artifacts/framework/*`; `artifacts/services/*` | `framework.jar=1c16f5976318fadcf7add92c518a93896f99e2a78f742b7347d8539103264882`; `services.jar=1c16f5976318fadcf7add92c518a93896f99e2a78f742b7347d8539103264882`; `fosframework.jar=fd57eea7793993361b3811651a905ea6be34f5c7a72b1fcea81cf798d0e3f481`; `fosservices.jar=364603c0228058973ed976ff1bef51c3cab2fa8fc163ec63c727157bb92dec96`; `services.vdex=06cb78333df89d97da741b921d7c62680b4a931aade45b83581b39d498cdbdc4`; `fosservices.vdex=584673e398894936dcba7a79c07d1f5abda7f2d03b3e36bd1792f764dd4dcffa`; `boot-framework.vdex=9a160fc8d64b147beb3c19a16bbf40a9ccc2007c3d595092d15ae4437dfc6404`; `boot-fosframework.vdex=d91bb12295e9ac55da414347643ff0e880e431eedc675f0944ad3f30cae06714` | provenance is 2026-08-03 device pull while saved baseline was PS7330; classify as PS7330 runtime capture, not PS7331 OTA extraction. Same JAR bytes do not promote VDEX/ODEX or whole build. |
| P20E-012 | Existing report consistency | `work/luna_worker_phase6mv_gpl_ota_inventory_20260810.md`; `work/luna_worker_continuation_inventory_20260810.md`; `findings/project-inventory.md`; `work/luna_worker_phase6ug_permission_parser_20260810.md` | report hashes preserved in cited files; no new hash generated | GPL scope, OTA/image hashes and selected payload hashes are mutually consistent; `phase6ug` exact-build wording must be read with P20E-011 path provenance, not as PS7331 runtime proof |

## Version and PS7330 separation

PS7331 payload fields are: Fire OS `7.3.3.1`, build `PS7331.4463N`, OTA version number `0031575863172`, post-build fingerprint `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`, product/device `trona`, security patch `2024-08-01`.

The saved PS7330 baseline is Fire OS `7.3.3.0`, build `PS7330.4104N`, incremental `0030099376128`, fingerprint `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`, product/device `trona`, model `KFTRWI`, security patch `2024-02-01`. PS7330 source archive SHA-256 is `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665`.

因此：

- P20E-001–010 are PS7331 source/OTA/extracted-payload evidence, not exact PS7330 evidence.
- P20E-011 is saved device-pulled runtime capture with PS7330 baseline provenance; it is not a PS7331 OTA extraction, even where JAR SHA equals a PS7331 selected JAR.
- No new conclusion about installed PS7330 kernel, boot Image, OTA acceptance, framework runtime state, or security patch status is supported by PS7331 artifacts alone.

## Source-scope limits

- GPL tar member absence supports a bounded negative only: complete Amazon `/init`, SELinux policy source, private framework source, deny-list resource producers and OTA post-install implementation are not present in the audited source member scope. It does not prove their compiled binaries contain no Amazon modifications.
- Source-to-signed-Image reproducibility is not established. The PS7331 source/Image report is a version-scoped semantic/provenance comparison.
- JAR/VDEX/ODEX hashes establish file identity at the recorded path, not execution, caller reachability, OTA acceptance, or device mutation.
- No PS7330 signed `boot.img`/kernel/Image hash is available in the reviewed corpus; PS7331 boot/Image must remain adjacent/reference artifacts.

