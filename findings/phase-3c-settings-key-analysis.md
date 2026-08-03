# Phase 3C settings key analysis

The canonical input is adb/phase3c/PHASE3C-BASELINE-20260803-02. The inventory is generated from all three
settings list outputs and exact-string searches in the existing Fire Launcher,
Settings, SystemUI, and Amazon framework decompilations.

Runtime launcher-shaped keys include tb_custom_launcher,
firelauncher_appsgrid_version, launcher_zero_margin_enabled, and
LAUNCHER_FTUE_FLAG. The inspected code has UI/content readers for some of
these keys, but no HOME-selector reader/writer; tb_custom_launcher itself had
no exact reader/writer. They were not randomly modified.
device_provisioned and user_setup_complete are provisioning state and were
rejected as unsafe HOME experiments.

Status:

- 已證實: no tested settings key changed HOME; system and secure settings were
  unchanged before and after rollback.
- 高可信推論: tb_custom_launcher is legacy/tool or UI state on this build,
  not the PackageManager HOME selector.
- 待驗證: an uncollected native/account service could read a key indirectly.
- 因風險拒絕測試: provisioning and navigation-bar settings.

The global differences after reboot were boot_count and atz_response_provider
timestamps, not launcher control. Raw values remain in adb/phase3c/PHASE3C-BASELINE-20260803-02/settings; the
derived inventory redacts identity-shaped values.
