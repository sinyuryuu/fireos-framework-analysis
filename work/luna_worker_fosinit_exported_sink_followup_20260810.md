# fosinit / exported-component / sink follow-up

Scope: PS7331 host artifacts only, public baseline `77c076b76`. The artifact contains 123 fosinit XML files. This follow-up is a static join of registration, manifest exported/permission metadata, caller/user gates, and downstream sinks. No action was manually triggered and no device-side mutation was performed.

## Result

No new ordinary-app or shell-legitimate path was found that converges on a User-0 HOME resolver change, `setHome`/preferred activity, `setApplicationEnabledSetting`, Settings/SettingsProvider writer, or DevicePolicy writer.

The only high-impact lifecycle edge retained as a non-ordinary-caller item is `BootAfterSystemOTAReceiver`: its source can enable `OobeHomeActivity` and reopen OOBE setup state, but the sender is system-server-only (`phase == 550 && PMS.isUpgrade()`), delivery is permission/protected-action gated, and no manual trigger was attempted. The Amazon UserManager component-state writer is child/profile scoped and remains closed by the existing Phase 6Q/6PW evidence.

## Evidence and dedupe notes

- Registration inventory: `artifacts/phase6jd-fosinit-20260808-01` (123 XML files), with representative registrations in `amazondevicepolicymanager_fosinit.xml`, `amazonusermanager_fosinit.xml`, `amazonpackagemanager_fosinit.xml`, `amazonprofileservice_fosinit.xml`, `amazonactivitymanager_fosinit.xml`, and `amazonappsettings_fosinit.xml`.
- Existing dedupe baselines: `output/tables/phase6jd-fosinit-registration-audit.csv`, `phase6q-binder-service-matrix.csv`, `phase6r-oobe-authorization-matrix.csv`, `phase6px-provenance-closure.csv`, and `phase6pw-route-classification.csv`.
- Exported candidates: `artifacts/phase6w/exported-component-audit-20260805-01/high-impact-exported-candidates.csv`; candidate exposure is not caller reachability or sink proof.
- OOBE manifest/source: `artifacts/phase6j/ota-oobe-manifest-audit-20260805-01/manifest.txt` and `artifacts/phase6ab/ota-input-validation-20260805-01/ota-input-validation.csv`.
- Static setter/source excerpts: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54318-54324,54537-54548,96117-96126` (KFT component state, setup settings, and system-server OTA sender).

Status vocabulary: `closed` means no qualifying ordinary caller-to-sink edge in the preserved host corpus; `rejected/lifecycle-only` means a sink exists but its gate is not an ordinary app/shell route.
