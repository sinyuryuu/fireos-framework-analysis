# High-impact installed-package permission holder inventory — 2026-08-10

Host-only static inventory. No ADB/device access, Binder/service call, ioctl, root,
exploit, OTA/recovery/flash, permission mutation, or state mutation was performed
for this inventory. A holder row is not an exploit or proof of caller reachability.

## Scope and result

The preserved Phase 6MC holder table contains 60 installed package rows and these
six requested permission families: CHANGE_COMPONENT_ENABLED_STATE (12),
WRITE_SECURE_SETTINGS (45), MANAGE_USERS (37), INSTALL_PACKAGES (7),
DELETE_PACKAGES (8), and FORCE_STOP_PACKAGES (3). Counts are from the preserved
CSV, not a new device query:
output/tables/phase6mc-permission-holders.csv:1-61,
SHA-256 1f97fa825f8b7cd86f05653259ecf43359d496d15af4e21e0c53512274ebdb18.

The normalized per-package inventory is the companion CSV. Each row preserves
package/UID, code path, system and privileged flags, requested permission set,
grant/provenance status, sink/reachability classification, and claim-level source
references. The source table does not preserve per-holder grant bit flags, so those
are explicitly recorded as "granted=true; per-holder grant flags not preserved."
Signature digests are recorded where the focused component audit preserved them;
otherwise UNKNOWN is retained.

com.android.vending is the exceptional /data/app, non-privileged-flag row in the
Phase 6MC table. Its separate saved Vending dump records UID 10180, /data/app
code path, digest e3ca78d8, and granted REBOOT in addition to the six-family
table: adb/phase6mb-vending-20260810-01/dumpsys_package_vending.txt:1292-1547,
SHA-256 08c767ce505c431fcdf4057305a83deecb98ac77842cccb8f90576efc091a958.
The saved grant source/history remains UNKNOWN; the audited extracted privapp XML
has no direct Vending grant block:
findings/phase-6mb-vending-permission-and-state-writer-audit.md:50-58,
and the two XML SHA-256 values there are
643cf114ed7d7b82a642fea650ed7d2f53b5dab2291e4f043c272cbe577df732 and
0b30c1624ffdab6c5454746737a060157276da5d2bd43addc74cd3919ae4aad1.

## Permission definitions and coverage gaps

The preserved package dump defines the requested Android permissions as follows:

| Permission | Protection level | Definition evidence |
|---|---|---|
| CHANGE_COMPONENT_ENABLED_STATE | signature|privileged | artifacts/phase6j/phase6j-ota-controller-holders-20260805-01/dumpsys_package_all.stdout.txt:10107-10112 |
| WRITE_SECURE_SETTINGS | signature|privileged|development | same file :12259-12264 |
| MANAGE_USERS | signature|privileged | same file :13260-13264 |
| INSTALL_PACKAGES | signature|privileged | same file :9992-9996 |
| DELETE_PACKAGES | signature|privileged | same file :16273-16277 |
| FORCE_STOP_PACKAGES | signature|privileged | same file :14901-14905 |
| REBOOT | signature|privileged | same file :14201-14205 |
| STATUS_BAR_SERVICE | signature | same file :12439-12443 |
| INJECT_EVENTS | signature | same file :16013-16017 |
| DUMP | signature|privileged|development | same file :15872-15876 |
| INTERACT_ACROSS_USERS | signature|privileged|development | same file :13595-13599 |
| INTERACT_ACROSS_USERS_FULL | signature|installer | same file :12108-12112 |
| com.amazon.device.permission.PROFILE_INTERACTION | signature|amazon | same file :13021-13025 |
| Amazon OTA/profile examples | signature|amazon | same file :11776-11780 (RECEIVE_BOOT_AFTER_SYSTEM_OTA); Phase 6Q index records the wider Amazon definition set at findings/phase-6q-evidence-index.md:25 |

The audited holder capture has no preserved holder rows for STATUS_BAR_SERVICE,
INJECT_EVENTS, DUMP, INTERACT_ACROSS_USERS(_FULL), or the Amazon
device/profile-owner permission family. This means holder, grant provenance, and
caller reachability for those permissions are UNKNOWN here—not "no holders."
The package dump does record the Android permission definitions and the system UID
package-setting owner (uid=1000), but that is definition metadata, not an
installed-APK holder inventory. Source SHA-256 for this package dump:
6f2754f4e9655567524de00c5b044326cbd992d6a9022b87397369fb5b905909.

## Sink and reachability cross-check

Saved code evidence supports only bounded classifications:

- The KFT child-user path reaches PMS application/component setters for the
  supplied child UserInfo.id; it also references profile-owner/admin setup. This
  is a system-server writer, not proof that every holder row can invoke it:
  output/tables/phase6mh-package-state-writers.csv:4-6,
  SHA-256 39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a;
  output/tables/phase6mc-amazon-caller-provenance.csv:3-4,
  SHA-256 fbb4f21dad1c3948bb3748fe7bcf652b6b136a6fb07e62cb4e7d7e6d51e1b11d.
- The H2 service has a signature-bound exported service and a static
  household/profile create-child chain, but no direct HOME writer in the bounded
  APK review: findings/phase-6mc-permission-and-h2-audit.md:80-133.
- The existing route closure records the KFT tx3 PMS boundary, DPM persistent
  preferred writer, and the bounded Vending package-state writer review:
  output/tables/phase6ps-privilege-route-closure.csv:2-12,
  SHA-256 efb335c6babb0bed4eb23e601a1d90bd179ffa3afbeccd19871a866b16132c0c.
- The Phase 6MC table marks literal Fire/HOME hits, but those booleans are only
  dump-block indicators. They do not prove a relevant code sink; the companion
  CSV therefore marks actual caller reachability UNKNOWN unless a preserved
  Phase 6 code path supports a narrower statement.

No row is classified as an exploit. In particular, "granted permission" does not
remove PMS protected-package checks, establish a preferred/HOME writer, establish
device/profile-owner status, or establish a credential/credential-locker path.

## Reproducibility

All commands below are host-only and read preserved files:

    python3 tools/scripts/audit_phase6mc_permission_holders.py
      --package-dump adb/phase6mc-permission-holders-20260810-01/package_dump.stdout.txt
      --permission-dump adb/phase6mc-permission-holders-20260810-01/permission_definitions.stdout.txt
      --output artifacts/phase6mc-permission-holder-audit-20260810-01

    python3 tools/scripts/audit_phase6lz_component_state_permissions.py
      --output-dir output/tables/phase6lz-component-state-permissions

    python3 - <<'PY'
    import csv
    with open("output/tables/phase6mc-permission-holders.csv", newline="") as f:
        rows=list(csv.DictReader(f))
    print(len(rows))
    print(sorted({p for r in rows for p in r["granted_permissions"].split(";")}))
    PY

    shasum -a 256 output/tables/phase6mc-permission-holders.csv
      output/tables/phase6lz-component-state-permissions/component-state-permission-holders.csv
      artifacts/phase6j/phase6j-ota-controller-holders-20260805-01/dumpsys_package_all.stdout.txt

The companion CSV was generated by a read-only transformation of the preserved
Phase 6MC table, with focused signature values joined from the Phase 6LZ table;
no original evidence was changed.

