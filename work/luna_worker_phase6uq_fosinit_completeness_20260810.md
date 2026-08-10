# PS7331 fosinit/service-registration completeness (host-only)

Date: 2026-08-10. Scope is static reconciliation only. No service, broadcast, package, OTA, reboot, driver, root, or exploit action was performed.

## Result

The preserved registration corpus is complete enough to close the reviewed Amazon Binder-service set, but not enough to claim every Amazon callback/receiver has a source-to-effect proof. The complete fosinit extraction contains 244 XML entries; the saved runtime service inventory contains 186 services; and the reviewed contract tables cover the principal private Binder contracts (31 methods across the Amazon activity/window/package/user surfaces). Runtime presence and global listing do not imply a caller handle: the saved SELinux observations report shell UID 2000 `service_manager find` denial for private services such as `amazonactivitymanager`, `amazonpackagemanager`, `amazonprofileservice`, `amazonusermanagerservice`, and `amazonwindowmanager`.

No unreviewed Amazon entry is shown by the preserved evidence to provide an ordinary external route to a package, component/HOME, settings, user, or OTA effect. There are, however, unclosed static edges. The next safe target is host-only source/JADX closure for the callback/receiver and policy entries listed below, followed by a read-only registration-to-runtime diff; do not invoke the entries.

## Reconciliation model

Each edge is classified independently:

* **Source** — implementation/class or callback is present in a source/JADX/disassembly tree.
* **Registration** — a fosinit XML or system-server publication string names the edge.
* **Handle visibility** — the saved runtime inventory and saved shell/SELinux result establish whether a caller can obtain a Binder handle. Listing alone is not visibility.
* **Method gate** — a method-local permission, UID, owner, phase, or caller-context check is identified.
* **Effect** — a concrete package/component/HOME/settings/user/OTA state write is identified, rather than a query, callback, or notification.

This prevents “class present”, “registered”, and “effect reachable” from being treated as equivalent.

## Closed or bounded edges

| Surface | Source / registration | Handle visibility | Gate | Effect conclusion |
|---|---|---|---|---|
| `amazonactivitymanager` / `IAmazonActivityManager` | Class, interface, transaction map, and `amazonactivitymanager_fosinit.xml` present | Listed, but saved shell `find` denied | Per-method permission/shell/exception markers in reviewed contract table | Activity/prewarm/PIP and state-query functions; no formal HOME/package writer shown |
| `amazonwindowmanager` / `IAmazonWindowManager` | Class, interface, transaction map, and fosinit present | Listed, shell `find` denied | Permission markers in reviewed methods | Lock/window/PIP state; no package/HOME resolver writer shown |
| `amazonpackagemanager` / `IAmazonPackageManager` | Class/contract and fosinit present | Listed, shell `find` denied | Amazon permission markers; OTA sender requires phase 550 and `PMS.isUpgrade()` | Protected-package/metadata and OTA lifecycle callbacks; no ordinary shell package writer |
| `amazonusermanagerservice` / `IAmazonUserManager` | Class/contract and fosinit present | Listed, shell `find` denied | Interface enforcement; KFT transaction has trusted lifecycle context in saved analysis | Can participate in trusted child-user launcher state; no User-0 shell route |
| `amazonprofileservice` | Class and fosinit present | Listed, shell `find` denied | `PROFILE_INTERACTION` on `initiateLauncher` | Profile lifecycle/picker support; no formal resolver writer |
| `amazon_input`, `amazon_keyevent` | Classes/callbacks and fosinit present | Listed, shell `find` denied | System/signature/Amazon input permissions | Input observation/filtering; no HOME/package/settings writer established |
| `fosdebug` | `FireOSDebugService` source/disassembly and core fosinit present | Runtime handle/dump saved | `DUMP` | Diagnostic/read-only surface |
| `AppCompatActivityStackSupervisorCallback` | Source/class, fosinit, and callback table present | Local system-server callback, not a public Binder handle | Inherited framework callback context | Delegates to `IPackageManager.resolveIntent` and filters uninstalled apps; no direct resolver override proven |
| `EveActivityStackSupervisorCallback` | Source/class and fosinit present | Local callback | No concrete override; inherited base returns null in saved review | No effect edge established |

## Missing edges / residual candidates

These are not findings of exploitability. They are the minimum host-only closure set where registration, source class, gate, or effect evidence is incomplete or spread across trees:

1. `amazonservicespolicy_fosinit.xml`: policy callbacks on ActivityManager/PackageManager/DevicePolicy surfaces. Registration is preserved, but callback-by-callback method-gate and effect mapping is not complete.
2. `core_fosinit.xml`: broad `VendorSystemServerCallback` and boot-receiver callback registration. It is a high fan-out edge; source and boot-phase gates must be mapped separately from service publication.
3. `tabletkeypolicymanager_fosinit.xml`, `keypolicymanager_fosinit.xml`, `tabletlauncherhijackpreventer_fosinit.xml`, and `launcherhijackpreventer_fosinit.xml`: HOME-adjacent callbacks. Existing evidence bounds custom-home signaling and `canSeeHomeTask`, but does not prove a persistent preferred-HOME/package write in these entries.
4. `amazonappsettings_fosinit.xml`, `packagewhitelister_fosinit.xml`, `factoryresetwhitelist_fosinit.xml`, and `packagerecency_fosinit.xml`: package/settings-adjacent callbacks. Registration is present, but the complete source-to-PMS method-gate/effect chain is not uniformly mapped.
5. `amazonusermanager_fosinit.xml`, `kindlefreetime_fosinit.xml`, and `toddlermode_fosinit.xml`: user/component-adjacent service/callback entries. The reviewed `IAmazonUserManager` surface is bounded, but these auxiliary entries need class/registration/consumer reconciliation to rule out alternate component writers.
6. `fireossystemota_fosinit.xml`, `crlsetmanager_fosinit.xml`, `amazoncertpininstall_fosinit.xml`, and `core_fosinit.xml` boot/OTA callbacks: registration and package-side OTA evidence exist, but callback-local sender/phase/upgrade gates are not closed for every entry.
7. `receiverfilter_fosinit.xml` and `tabletbroadcastrelay_fosinit.xml`: receiver/broadcast routing entries. The preserved protected-broadcast and manifest work bounds several receivers, but no complete union of every fosinit receiver to exportedness, permission, caller identity, and sink is present.

## Sink assessment

* **Package:** Amazon Package Manager has package-adjacent methods and OTA lifecycle callbacks, but saved handle denial and method gates prevent an ordinary shell path; no unreviewed package mutation edge is proven.
* **Component/HOME:** HOME-adjacent callbacks can observe or route activity and custom-home signals. The saved resolver/package evidence keeps Fire as the User-0 fallback and shows no unreviewed persistent preferred-HOME writer. Trusted DPM/KFT paths are separate, explicitly gated paths.
* **Settings:** `amazonappsettings` and settings callbacks remain a static closure gap; no exported, ungated settings writer is shown in preserved evidence.
* **User:** `IAmazonUserManager` is registered and globally listed, but private handle visibility is denied to shell; the known KFT child-user path is trusted-context only. No alternate unreviewed User-0 writer is shown.
* **OTA:** OTA-related fosinit and receiver entries are registered, but the reviewed sender/receiver path carries phase/upgrade/signature conditions. No OTA invocation was made and no unreviewed reachable OTA sink is established.

## Confidence and limitations

Confidence is **high** for XML extraction count, saved runtime listing, reviewed private-service shell visibility, and the mapped Binder contracts; **medium** for the callback/policy residual list; and **low-to-medium** for a negative claim about unreviewed effects because a full source-to-method-to-sink mapping for all 244 entries is not preserved. Absence from a JADX tree is not proof of dead code, and runtime listing is not proof of caller visibility.

## Next safe target

Perform a host-only closure of the seven residual groups above: parse every fosinit `service`, `callback`, and `receiver` attribute; resolve the implementation class against both `decompiled/baksmali/vdexExtractor/fosservices` and `decompiled/jadx/ota-PS7331`; join system-server publication strings and saved runtime names; then record method-local gate and sink classification. Use only file reads, hashing, and static text/disassembly analysis. Do not call Binder, send broadcasts, alter package state, exercise OTA, reboot, or load drivers.

## Input hashes

SHA-256 values are recorded in the companion CSV. Key inputs include the complete fosinit extraction manifest, fosinit edge table, service-surface table, Binder contract table, saved runtime summary, vendor HOME callback table, and saved service list.
