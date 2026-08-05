# Phase 6AB evidence index

本索引只引用保存的主機端 source／manifest／VDEX 輸入與 Phase 6AB artifact。
本階段未接觸設備。

| Evidence ID | Source / file | Location | Observation | Classification | Confidence |
|---|---|---|---|---|---|
| `6AB-OOBE-001` | `BootAfterSystemOTAReceiver.java` (`c29b32bf...5cb90`) | `:22,27-80` | action、OOBE predicates、incremental prefs、enable OOBE Home、activation | 高風險 post-OTA/OOBE lifecycle | Confirmed |
| `6AB-OOBE-002` | same receiver | `:43-45` | exception path logs and disables receiver component | state side effect | Confirmed |
| `6AB-OOBE-003` | `OOBEActivationHelper.java` (`6ebcb7ee...223d2`) | `:53-56` | `user_setup_complete=0`, `isOOBEActive=1` | setup state mutation | Confirmed |
| `6AB-OOBE-004` | OOBE manifest (`bcc51d83...7275ff`) | `:433-465`, `:531-541` | priority-100 setup HOME and receiver declaration | manifest surface, not caller proof | Confirmed |
| `6AB-OOBE-005` | `fosservices/disassembly.log` (`ecbe62fe...5151c`) | `:96107-96126` | boot phase 550 + `isUpgrade()` sends action with receiver permission | system-server gated sender | Confirmed |
| `6AB-OTA-001` | `SideloadFilenameFilter.java` (`fbd2d76a...11849`); `OTASettings.java` | `:17,22`; `:169-170` | runtime regex, default `update-.*\\.(bin|zip)$`, `.find()` | discovery only | Strong evidence |
| `6AB-OTA-002` | `SideloadDirectory.java`; `SideloadFileObserver.java` | `:25-39`; `:116-161` | stable-size check, metadata check, newest compatible version selection | discovery then metadata gate | Confirmed |
| `6AB-OTA-003` | `BuildPropertiesFactory.java`; `ZipHelper.java` | `:22-42`; `:30-46` | exact `system/build.prop` ZIP entry and `Properties.load()` | metadata extraction | Confirmed |
| `6AB-OTA-004` | `Sideload.java` + `BuildProperties.java` (`877af296b3167d5a5869b7fad0947a1afd82f7f6233689bacfb7ea41d12137a8` / `4b3f386b274099fb68954abd7e183eb57b469e0a68516d6ccee21a30ac07df61`) | contract JADX tree `Sideload.java:10-100`; `BuildProperties.java:8-108` | Parcelable model、File/BuildProperties 關係與 build/product/signature/version property mapping 已可讀取 | Java model coverage closed; native OTA semantics remain separate | Confirmed |
| `6AB-OTA-005` | `SideloadMetadataChecker.java` (`4df89b5a...32f5c6`) | `:24-82` | version, signature, product and transition gates | metadata validation | Confirmed |
| `6AB-OTA-006` | `SideloadPVTChecker.java` (`30834da9...de809`) | `:18-32` | PVT non-user build rejection unless unlocked | build policy | Confirmed |
| `6AB-OTA-007` | `SideloadVerifier.java` (`4ba31d32...49eea`) | `:22-68` | sanity → metadata → recovery package verification → device state | verification boundary | Confirmed |
| `6AB-OTA-008` | `SideloadSanityChecker.java` | `:21-35` | file exists and properties non-empty | basic gate | Confirmed |
| `6AB-OTA-009` | `SideloadInstaller.java`; `UpdateSystemWrapper.java` | `:65-90`; `:30-45` | verification precedes move and `UpdateSystem.install` | high-impact sink | Confirmed |
| `6AB-OTA-010` | `SideloadDeviceStateChecker.java` (`a9be9a33...c6b97`) | `:27-62` | insufficient cache may delete download-cache contents | local cleanup side effect | Confirmed |
| `6AB-OTA-011` | `SideloadMover.java`; `FileHelper.java` | `:31-45`; `:305-340` | basename destination and rename/copy/delete; no Java no-follow marker observed | bounded hardening unknown | Strong evidence |
| `6AB-OTA-012` | `OSUpdatePropertiesValidator.java` (`03193c3a...616a`) | `:24-63` | background version/signature/PVT checks | background OTA gate | Confirmed |
| `6AB-SAFETY-001` | `artifacts/phase6ab/ota-input-validation-20260805-03/summary.json` | generated summary | no device, broadcast, Binder, OTA, recovery or partition operation | runtime trigger rejected | Confirmed |

完整來源 hash 以 `artifacts/phase6ab/ota-input-validation-20260805-03/input-sha256.csv`
為準；machine-readable row 以同一目錄的 `ota-input-validation.csv` 為準。
舊的 `...-02` artifact 不覆寫，保留其 selected-source coverage-gap 歷史狀態。
