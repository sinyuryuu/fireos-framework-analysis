# Phase 6MA — DenyList provenance, fosinit registration, and KFT reachability

## Scope

This phase closes the remaining static question around the Fire Launcher
protected-package gate and reconciles it with the saved child-profile runtime
observations. All new work was host-only except for no new device operation;
the runtime material cited here was collected in earlier, explicitly bounded
tests. No private Binder transaction, exploit payload, driver ioctl, APK
execution, Root method, OTA, reboot, package mutation, or partition write was
performed in this phase.

## 1. Protected-package source

The PS7331 system-image resource extraction maps resource ID `0x7e05000a` to
`amazon.fireos:raw/package_manager_deny_list`. The preserved raw JSON contains
`com.amazon.firelauncher` at line 6:

```text
artifacts/phase6ap/denylist-resource-closure-20260805-01/
  res/raw/package_manager_deny_list.json:2-7
```

Evidence anchors:

- raw deny-list SHA-256:
  `16086fecbfce0a20c0b37535e25d690635d398b30d582fa6d231736dc9bdf710`
- extraction summary SHA-256:
  `eb194e437f97246110112dac4aa54111310bf04daf97c38bb7b595e779d52404`
- matching system-image SHA-256:
  `da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5`

**已證實（本 PS7331 system-image artifact）：** Fire Launcher is explicitly
present in Amazon's package-manager deny-list resource. This is stronger than
inferring membership from the `Cannot disable a protected package` error.
It does not imply that the list is writable by shell or that a future Arcus
refresh can be invoked by shell.

## 2. Framework registration boundary

The extracted `amazonpackagemanager_fosinit.xml` registers:

- `AmazonPackageManagerService` as a vendor PackageManager service;
- `AmazonPackageManagerCallback` and related callbacks;
- `ControlProtectedPackagesCallback` as a `VendorProtectedPackagesCallback`;
- the Amazon PackageManager implementation and statistics instance.

Evidence: `artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonpackagemanager_fosinit.xml:9-31`, SHA-256
`eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286`.

The registration is `SYSTEMSERVER` code, not an application-side service
registration. Existing runtime evidence reports the corresponding service
names in the service list but `service check` cannot obtain a usable shell
handle, and SELinux denies the shell `find` operation for the Amazon service
contexts. Therefore:

**已證實：** registration exists in the extracted Fire OS artifact.

**高可信推論：** the deny-list gate is a PackageManager/system-server control
surface, not a HOME resolver-only preference.

**已證實（saved runtime boundary）：** ordinary shell cannot reach the focused
Amazon services through the saved enforcing SELinux/service-manager path. A
Binder Stub or transaction mapping in a decompiled artifact is not evidence of
caller reachability.

## 3. KFT and child-profile reconciliation

The extracted `amazonusermanager_fosinit.xml` registers
`AmazonUserManagerService`, while `kindlefreetime_fosinit.xml` registers the
child/profile ActivityManager callbacks. Static disassembly shows a
per-`UserInfo.id` writer that enables Tahoe's child launcher and disables Fire
Launcher/Launcher3 for the selected child profile.

The saved runtime observation used only lifecycle operations on the already
existing User 10 profile, then returned to User 0 and stopped User 10. It did
not send the private KFT transaction. The observed result was:

- User 0 remained the current user after rollback;
- User 0 HOME remained Fire Launcher;
- User 10 remained pre-existing and stopped;
- User 10 resolved to `FallbackHome` in that run, not a new Tahoe HOME;
- no new Android user was created by the UI submission follow-up.

Evidence:

- `findings/phase-6bk-kft-runtime.md`
- `adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/`
- `adb/phase6bk/PHASE6BK-KFT-RUNTIME-20260810-01/`
- static writer: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325`

**已證實：** the KFT writer is user-scoped in the recovered code shape.

**已排除（tested boundary）：** switching the existing child profile is not a
User-0 Fire Launcher replacement and does not give shell a private KFT Binder
handle.

**待驗證：** the exact local commit/rollback reason inside Tahoe's application
workflow. It is not necessary to invoke the private transaction to answer the
User-0 launcher question, and doing so is outside this phase's safe scope.

## 4. Native and service registration scan

The selected native overlay scan reports zero launcher/HOME literals and zero
package-state setter literals in its bounded system/vendor input set:

`artifacts/phase6je-native-overlay-20260808-01/native-scan-summary.tsv`

SHA-256: `c3a42869b6bd77f75c636cbe254cd2e01e42056f4336678d72ad5971a511a4bc`.

**高可信推論（bounded scope）：** no native HOME/package-state writer was found
in the scanned artifacts.

**無法取得證據（global scope）：** the scan does not prove that every
runtime-loaded native registration outside the extracted set is absent.

## 5. Decision table

| Question | Finding | Confidence |
|---|---|---|
| Why does `pm disable-user` fail? | Fire Launcher is a member of the PS7331 package-manager deny-list and the protected-package gate rejects the mutation before state change. | Confirmed |
| Is the gate only ordinary Android priority logic? | No. Priority explains HOME ranking, while the deny-list is a separate package-state protection source. | Confirmed |
| Is there a shell-writable deny-list path? | None found; the list is an image resource and runtime service access is blocked in saved evidence. | Strong evidence |
| Can KFT disable Fire Launcher? | Yes, statically, for a supplied child/profile user ID. | Confirmed, child/profile scope |
| Can ordinary shell invoke KFT for User 0? | No reachable path was found; service name visibility is not a Binder handle. | Strong evidence |
| Does OTA/OOBE provide a normal launcher bypass? | No; those paths are protected lifecycle/setup writers with fixed recovery scope. | Confirmed |
| Does a vendor driver provide a HOME bridge? | No driver-to-PMS/AMS/ATMS/HOME source edge was found. | Strong evidence |

The machine-readable version is
`output/tables/phase6ma-route-matrix.csv`.

## 6. Remaining research value

The highest-value remaining host-only work is to complete the caller graph from
the exported `IAmazonUserManager` contract to the KFT writer and to document
the Arcus refresh sender/permission provenance. That work may clarify trusted
production lifecycle behavior, but it is not currently a shell bypass.

No physical exploit or private Binder transaction is justified by the present
evidence. Any future device work should remain read-only or an explicitly
user-visible, reversible foreground redirect experiment.

## Reproduction

The deny-list provenance tool supports a host-only dry run:

```sh
python3 tools/scripts/audit_phase6ap_denylist_resource.py --dry-run
```

The previously captured resource artifacts are immutable evidence; rerunning
the tool against the same output directory is intentionally refused to avoid
overwriting originals.
