# Phase 6X2 control surfaces

```mermaid
flowchart LR
  classDef unknown fill:#fff3cd,stroke:#856404
  classDef sink fill:#d1ecf1,stroke:#0c5460
  N5888204305["external dumpsys caller subject to DUMP; exact UID UNKNOWN"]
  N3b7c76d3a7["android.permission.DUMP checked in dump; service-manager/SELinux rule UNKNOWN"]
  N9c3ca09573["device/default settings user (explicit user overload absent)"]
  N33ccbf4bb1["FireOsDisplayPowerControllerService$BinderService"]
  N5888204305 -->|WG-001| N3b7c76d3a7
  N3b7c76d3a7 -->|WG-001| N9c3ca09573
  N9c3ca09573 -->|WG-001| N33ccbf4bb1
  N33ccbf4bb1:::sink
  Nd9e50f0a3f["system_server input-monitor caller/publisher; external Binder caller not recove…"]
  Nb83491d570["system_server/internal callback; permission and SELinux/service-manager gate UN…"]
  N41f8314df1["system/default secure-settings scope (non-user overload)"]
  N5b107e26b1["InputFilterMonitorInputManagerServiceCallback"]
  Nd9e50f0a3f -->|WG-002| Nb83491d570
  Nb83491d570 -->|WG-002| N41f8314df1
  N41f8314df1 -->|WG-002| N5b107e26b1
  N5b107e26b1:::sink
  Nb02fcc14c5["remote Binder caller with MODE_SWITCH; exact UID UNKNOWN"]
  N1d0f73f422["com.amazon.alexa.permission.MODE_SWITCH enforced by checkCallingOrSelfPermissio…"]
  N9fe5dd7651["USER_CURRENT/-2 passed to putIntForUser"]
  Neabd83298f["AlexaModeSwitchManagerService$AlexaModeSwitchAPIImpl"]
  Nb02fcc14c5 -->|WG-003| N1d0f73f422
  N1d0f73f422 -->|WG-003| N9fe5dd7651
  N9fe5dd7651 -->|WG-003| Neabd83298f
  Neabd83298f:::sink
  N25ba44ec3b["UNKNOWN"]
  N25ba44ec3b -->|6WL-ROW-004| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-004| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-004| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6WL-ROW-005| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-005| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-005| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6WL-ROW-006| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-006| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-006| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6WL-ROW-007| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-007| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-007| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6WL-ROW-008| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-008| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-008| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6WL-ROW-009| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-009| N25ba44ec3b
  N25ba44ec3b -->|6WL-ROW-009| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nf28b9987ea["policy names device type only; no exact caller identity or framework/HOME/packa…"]
  N25ba44ec3b -->|WI-01| N25ba44ec3b
  N25ba44ec3b -->|WI-01| Nf28b9987ea
  Nf28b9987ea -->|WI-01| N25ba44ec3b
  N25ba44ec3b:::unknown
  N4ea9eea018["ION library labels are same_process_hal_file; no exact identity and no package/…"]
  N25ba44ec3b -->|WI-02| N25ba44ec3b
  N25ba44ec3b -->|WI-02| N4ea9eea018
  N4ea9eea018 -->|WI-02| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nac7c89dd9d["no userland identity or sensitive sink identified"]
  N25ba44ec3b -->|WI-03| N25ba44ec3b
  N25ba44ec3b -->|WI-03| Nac7c89dd9d
  Nac7c89dd9d -->|WI-03| N25ba44ec3b
  N25ba44ec3b:::unknown
  N89e4f97d27["HAL service identity is privileged-domain context only; no exact package/HOME/P…"]
  N25ba44ec3b -->|WI-04| N25ba44ec3b
  N25ba44ec3b -->|WI-04| N89e4f97d27
  N89e4f97d27 -->|WI-04| N25ba44ec3b
  N25ba44ec3b:::unknown
  N27299b7014["diagnostic HAL/domain name is not a proc caller and no package/HOME/privilege s…"]
  N25ba44ec3b -->|WI-05| N25ba44ec3b
  N25ba44ec3b -->|WI-05| N27299b7014
  N27299b7014 -->|WI-05| N25ba44ec3b
  N25ba44ec3b:::unknown
  N2382c43382["rpmb_svc identity is a service observation; no package/HOME sink"]
  N25ba44ec3b -->|WI-06| N25ba44ec3b
  N25ba44ec3b -->|WI-06| N2382c43382
  N2382c43382 -->|WI-06| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nc60af97a43["HAL/service identity only; no package/HOME/settings sink"]
  N25ba44ec3b -->|WI-07| N25ba44ec3b
  N25ba44ec3b -->|WI-07| Nc60af97a43
  Nc60af97a43 -->|WI-07| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-01| N25ba44ec3b
  N25ba44ec3b -->|WJ-01| N25ba44ec3b
  N25ba44ec3b -->|WJ-01| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-02| N25ba44ec3b
  N25ba44ec3b -->|WJ-02| N25ba44ec3b
  N25ba44ec3b -->|WJ-02| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-03| N25ba44ec3b
  N25ba44ec3b -->|WJ-03| N25ba44ec3b
  N25ba44ec3b -->|WJ-03| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-04| N25ba44ec3b
  N25ba44ec3b -->|WJ-04| N25ba44ec3b
  N25ba44ec3b -->|WJ-04| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-05| N25ba44ec3b
  N25ba44ec3b -->|WJ-05| N25ba44ec3b
  N25ba44ec3b -->|WJ-05| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-06| N25ba44ec3b
  N25ba44ec3b -->|WJ-06| N25ba44ec3b
  N25ba44ec3b -->|WJ-06| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-07| N25ba44ec3b
  N25ba44ec3b -->|WJ-07| N25ba44ec3b
  N25ba44ec3b -->|WJ-07| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-08| N25ba44ec3b
  N25ba44ec3b -->|WJ-08| N25ba44ec3b
  N25ba44ec3b -->|WJ-08| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-09| N25ba44ec3b
  N25ba44ec3b -->|WJ-09| N25ba44ec3b
  N25ba44ec3b -->|WJ-09| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WJ-10| N25ba44ec3b
  N25ba44ec3b -->|WJ-10| N25ba44ec3b
  N25ba44ec3b -->|WJ-10| N25ba44ec3b
  N25ba44ec3b:::unknown
  N8355aace37["DefaultPermissionGrantPolicy"]
  N5db745617b["system_server/internal policy path; exact caller gate UNKNOWN"]
  N17c37f2e47["userId argument"]
  N8355aace37 -->|WK-001| N5db745617b
  N5db745617b -->|WK-001| N17c37f2e47
  N17c37f2e47 -->|WK-001| N8355aace37
  N8355aace37:::sink
  N3c6d58b864["UserManagerService Binder implementation"]
  Ne2e679f3ac["checkManageOrCreateUsersPermission(flags); MANAGE_USERS or CREATE_USERS; system…"]
  N2136084e4d["system/default user scope"]
  N9263c45b38["UserManagerService"]
  N3c6d58b864 -->|WK-002| Ne2e679f3ac
  Ne2e679f3ac -->|WK-002| N2136084e4d
  N2136084e4d -->|WK-002| N9263c45b38
  N9263c45b38:::sink
  N7f367ab5e6["parent userId plus created profile"]
  N3c6d58b864 -->|WK-003| Ne2e679f3ac
  Ne2e679f3ac -->|WK-003| N7f367ab5e6
  N7f367ab5e6 -->|WK-003| N9263c45b38
  N9263c45b38:::sink
  Nf0792c753f["checkManageOrCreateUsersPermission('Only the system can remove users'); exact d…"]
  Ncd54039829["userHandle argument"]
  N3c6d58b864 -->|WK-004| Nf0792c753f
  Nf0792c753f -->|WK-004| Ncd54039829
  Ncd54039829 -->|WK-004| N9263c45b38
  N9263c45b38:::sink
  Nc76b2e48db["UserController Binder-facing path"]
  N01e4a78f40["INTERACT_ACROSS_USERS_FULL or amazon.aosp.permission.INTERACT_ACROSS_USERS_FULL…"]
  N69509065b9["userId; system user rejected"]
  N913fbd7a84["UserController"]
  Nc76b2e48db -->|WK-005| N01e4a78f40
  N01e4a78f40 -->|WK-005| N69509065b9
  N69509065b9 -->|WK-005| N913fbd7a84
  N913fbd7a84:::sink
  N3957f78701["ActivityManagerShellCommand"]
  N2efc01a571["shell command plus canSwitchUsers restriction; exact shell UID enforcement in d…"]
  Nd8b6f3d0de["supplied target user"]
  N3957f78701 -->|WK-006| N2efc01a571
  N2efc01a571 -->|WK-006| Nd8b6f3d0de
  Nd8b6f3d0de -->|WK-006| N3957f78701
  N3957f78701:::sink
  N699f619336["shell command path; downstream caller and SELinux gate UNKNOWN"]
  N3957f78701 -->|WK-007| N699f619336
  N699f619336 -->|WK-007| Nd8b6f3d0de
  Nd8b6f3d0de -->|WK-007| N3957f78701
  N3957f78701:::sink
  Nefe170573b["shell command path; downstream INTERACT_ACROSS_USERS_FULL gate visible in UserC…"]
  N3957f78701 -->|WK-008| Nefe170573b
  Nefe170573b -->|WK-008| Nd8b6f3d0de
  Nd8b6f3d0de -->|WK-008| N3957f78701
  N3957f78701:::sink
  N7006fa3073["AppRestrictionsHelper"]
  N42f6bce375["PackageManager validation; Settings UI/profile-policy caller and SELinux rule U…"]
  N559b9abd7c["explicit userId"]
  N7006fa3073 -->|WK-009| N42f6bce375
  N42f6bce375 -->|WK-009| N559b9abd7c
  N559b9abd7c -->|WK-009| N7006fa3073
  N7006fa3073:::sink
  Nfa75e0fca6["PackageManager uninstall validation; only restricted-profile branch visible"]
  N7006fa3073 -->|WK-010| Nfa75e0fca6
  Nfa75e0fca6 -->|WK-010| N559b9abd7c
  N559b9abd7c -->|WK-010| N7006fa3073
  N7006fa3073:::sink
  N15b285a43e["UserManagerHelper"]
  Nefe722e806["helper checks no_add_user restriction; service permission gate remains authorit…"]
  N2d40f06f6d["current process/default user scope"]
  N15b285a43e -->|WK-011| Nefe722e806
  Nefe722e806 -->|WK-011| N2d40f06f6d
  N2d40f06f6d -->|WK-011| N15b285a43e
  N15b285a43e:::sink
  N683c60d552["helper excludes system/current-user case; service permission gate remains autho…"]
  N40529f128f["userInfo.id"]
  N15b285a43e -->|WK-012| N683c60d552
  N683c60d552 -->|WK-012| N40529f128f
  N40529f128f -->|WK-012| N15b285a43e
  N15b285a43e:::sink
  N2ff4da4fa9["helper checks current/foreground user only; downstream switch gate and SELinux …"]
  N2d3569756b["target user id"]
  N15b285a43e -->|WK-013| N2ff4da4fa9
  N2ff4da4fa9 -->|WK-013| N2d3569756b
  N2d3569756b -->|WK-013| N15b285a43e
  N15b285a43e:::sink
  N08dfb1fbdb["external callers through exported SettingsProvider"]
  Ne0a25b9e14["global/secure writes enforce WRITE_SECURE_SETTINGS; system writes use WRITE_SET…"]
  N8f29561940["calling user and requested setting namespace"]
  N7a86629222["SettingsProvider"]
  N08dfb1fbdb -->|WK-014| Ne0a25b9e14
  Ne0a25b9e14 -->|WK-014| N8f29561940
  N8f29561940 -->|WK-014| N7a86629222
  N7a86629222:::sink
  N8d7dd60d61["android:exported=true; sharedUserId=android.uid.system; provider write methods …"]
  Nc568a5acc2["singleUser across users"]
  N7a86629222 -->|WK-015| N8d7dd60d61
  N8d7dd60d61 -->|WK-015| Nc568a5acc2
  Nc568a5acc2 -->|WK-015| N7a86629222
  N7a86629222:::sink
  N3c361edc10["MediaSessionService"]
  Nc2f78ff8a8["internal service path; exact caller/permission and SELinux rule UNKNOWN"]
  N2e50679b5f["full user id"]
  N3c361edc10 -->|WK-016| Nc2f78ff8a8
  Nc2f78ff8a8 -->|WK-016| N2e50679b5f
  N2e50679b5f -->|WK-016| N3c361edc10
  N3c361edc10:::sink
  Nf2612a93b1["system_server internal; file path, DAC, SELinux and caller gate UNKNOWN"]
  N4ed4246555["user list and user state"]
  N9263c45b38 -->|WK-017| Nf2612a93b1
  Nf2612a93b1 -->|WK-017| N4ed4246555
  N4ed4246555 -->|WK-017| N9263c45b38
  N9263c45b38:::sink
  N25ba44ec3b -->|WF-POL-001| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-001| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-001| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WF-POL-002| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-002| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-002| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WF-POL-003| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-003| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-003| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WF-POL-004| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-004| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-004| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|WF-POL-005| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-005| N25ba44ec3b
  N25ba44ec3b -->|WF-POL-005| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nd48aa1b8bd["Binder caller UID from Binder.getCallingUid(); verified default package resolve…"]
  Nd729b7fb9a["checkUidPermission(android.permission.CONTROL_KEYGUARD) OR checkUidPermission(c…"]
  N5dd9de7a00["caller UID is retained and forwarded with verified package; no clearCallingIden…"]
  N1862c5f2cf["IAmazonKeyguardServiceSystemUI.dismissWithPendingIntent; SystemUI keyguard dism…"]
  Nd48aa1b8bd -->|KX-IPC-001| Nd729b7fb9a
  Nd729b7fb9a -->|KX-IPC-001| N5dd9de7a00
  N5dd9de7a00 -->|KX-IPC-001| N1862c5f2cf
  N1862c5f2cf:::sink
  Ne821bb88c4["caller UID and verified package are forwarded to SystemUI; no identity clear ob…"]
  Nca5088118f["IAmazonKeyguardServiceSystemUI.setAccessibilityInfo; keyguard accessibility met…"]
  Nd48aa1b8bd -->|KX-IPC-002| Nd729b7fb9a
  Nd729b7fb9a -->|KX-IPC-002| Ne821bb88c4
  Ne821bb88c4 -->|KX-IPC-002| Nca5088118f
  Nca5088118f:::sink
  Nba24336edd["IAmazonKeyguardServiceSystemUI.setForegroundColor; keyguard foreground color/pr…"]
  Nd48aa1b8bd -->|KX-IPC-003| Nd729b7fb9a
  Nd729b7fb9a -->|KX-IPC-003| Ne821bb88c4
  Ne821bb88c4 -->|KX-IPC-003| Nba24336edd
  Nba24336edd:::sink
  Nf90e132fae["OTA privileged lifecycle is not established by this file alone"]
  N9562ab5058["manifest metadata records product/version/key_type; no runtime install gate is …"]
  N4ac0660e17["PS7331.4463N package identity only; installed baseline is PS7330.4104N; runtime…"]
  N3c9c88b1e9["No caller-to-writer inference; no exact installed-build post-install or rollbac…"]
  Nf90e132fae -->|6X-OTA-01| N9562ab5058
  N9562ab5058 -->|6X-OTA-01| N4ac0660e17
  N4ac0660e17 -->|6X-OTA-01| N3c9c88b1e9
  N3c9c88b1e9:::sink
  N3972a34f91["No installer/recovery caller; extraction is host-side"]
  N7ed6a592b4["file list and per-output SHA-256 only; no package signature, recovery, or execu…"]
  N675caf682e["Derived artifact identity only; runtime process/UID/SELinux UNKNOWN"]
  N2fabbeb30b["Framework/APK/VDEX outputs are analysis inputs, not post-install/native writer …"]
  N3972a34f91 -->|6X-OTA-02| N7ed6a592b4
  N7ed6a592b4 -->|6X-OTA-02| N675caf682e
  N675caf682e -->|6X-OTA-02| N2fabbeb30b
  N2fabbeb30b:::sink
  Nba0b4865b9["Privileged OTA lifecycle and recovery context are capability candidates; ordina…"]
  Nb64885d47f["metadata/hash/recovery-verification/controller gates precede handoff; indirect …"]
  N18d92bcfad["UpdateSystem/recovery UID, SELinux domain, AVB rollback authority, and exact us…"]
  N25af3afb47["Edify extraction/block-image/cache/readlink paths reach high-privilege file/par…"]
  Nba0b4865b9 -->|6X-OTA-03| Nb64885d47f
  Nb64885d47f -->|6X-OTA-03| N18d92bcfad
  N18d92bcfad -->|6X-OTA-03| N25af3afb47
  N25af3afb47:::sink
  Nf2666072aa["SideloadMover/MakeFreeSpaceOnCache are static callers only; external input prov…"]
  N1217c0f214["basename staging, rename/copy-delete fallback, readlink/unlink/free-space helpe…"]
  N34ae896d50["Path owner, race semantics, helper return dataflow, and writer identity UNKNOWN"]
  N3f56b1df5c["Potential staging/cache and native writer capability remains bounded; no arbitr…"]
  Nf2666072aa -->|6X-OTA-04| N1217c0f214
  N1217c0f214 -->|6X-OTA-04| N34ae896d50
  N34ae896d50 -->|6X-OTA-04| N3f56b1df5c
  N3f56b1df5c:::sink
  N66c7a955b8["uinput_fops: read, write, unlocked_ioctl, compat_ioctl; misc_register"]
  N0d36810def["CONFIG_INPUT_UINPUT=y (artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.conf…"]
  N8a19547a92["No exact shipped native ELF open/write/ioctl callsite; package and UID/domain n…"]
  N3d208bc5c2["Synthetic input device creation and event injection into the kernel input graph…"]
  N66c7a955b8 -->|6XG-001| N0d36810def
  N0d36810def -->|6XG-001| N8a19547a92
  N8a19547a92 -->|6XG-001| N3d208bc5c2
  N3d208bc5c2:::sink
  Na4e8e3abfd["POWER_SUPPLY_ATTR store; power_supply_store_property -> power_supply_set_proper…"]
  Ncb64ce3f15["CONFIG_POWER_SUPPLY=y; attributes are read-only by default and gain S_IWUSR onl…"]
  N68056e61cb["No exact shipped native sysfs write caller, package, UID, or domain established"]
  Nf4c7dcfe6a["Battery/charger power-supply property mutation when the provider advertises a w…"]
  Na4e8e3abfd -->|6XG-002| Ncb64ce3f15
  Ncb64ce3f15 -->|6XG-002| N68056e61cb
  N68056e61cb -->|6XG-002| Nf4c7dcfe6a
  Nf4c7dcfe6a:::sink
  N6d72536037["rpmb_fops: open, release, unlocked_ioctl; .write=NULL; .read=NULL; cdev_add/dev…"]
  N575b1a7ad9["CONFIG_RPMB=y; CONFIG_RPMB_INTF_DEV is not set in merged kernel.config:2235-223…"]
  Nf874439958["Existing rpmb_svc process evidence does not identify a native open/ioctl callsi…"]
  N976ae9b9a3["Authenticated persistent RPMB read/write/counter operations are available only …"]
  N6d72536037 -->|6XG-003| N575b1a7ad9
  N575b1a7ad9 -->|6XG-003| Nf874439958
  Nf874439958 -->|6XG-003| N976ae9b9a3
  N976ae9b9a3:::sink
  N4e0311e172["No source registration/API because path is absent"]
  N14175a5992["Archive-level path absence; do not infer that a separate vendor tree is kernel …"]
  N8e77d4f278["No caller/package/UID can be assigned to an absent path"]
  N21da87fbe1["No driver sink attributable to absent vendor/mediatek path; any vendor ELF/poli…"]
  N4e0311e172 -->|6XG-004| N14175a5992
  N14175a5992 -->|6XG-004| N8e77d4f278
  N8e77d4f278 -->|6XG-004| N21da87fbe1
  N21da87fbe1:::sink
  Nd82ce7e599["No exact shipped ELF open/write/ioctl caller; no uinput-specific file-context/a…"]
  Nc6ce4cd90e["Inventory/policy absence is a negative join only; it does not prove node absenc…"]
  N19cac871a1["No package, UID, or SELinux domain established"]
  Na7f3bb6b0b["No confirmed input-injection or package/HOME effect from shipped native code"]
  Nd82ce7e599 -->|6XG-005| Nc6ce4cd90e
  Nc6ce4cd90e -->|6XG-005| N19cac871a1
  N19cac871a1 -->|6XG-005| Na7f3bb6b0b
  Na7f3bb6b0b:::sink
  N18ffbe29ad["unknown/no bounded requester"]
  N6824b2716b["manifest declaration only; no service-side check joined; protection=0x0 (normal)"]
  N76e0ffd5ec["owner android.amazon.perm sharedUserId=android.uid.system; holder/grant not est…"]
  N2eb2b1a025["none joined in bounded exact manifests/disassembly"]
  N18ffbe29ad -->|6Y-001| N6824b2716b
  N6824b2716b -->|6Y-001| N76e0ffd5ec
  N76e0ffd5ec -->|6Y-001| N2eb2b1a025
  N2eb2b1a025:::sink
  N18ffbe29ad -->|6Y-002| N6824b2716b
  N6824b2716b -->|6Y-002| N76e0ffd5ec
  N76e0ffd5ec -->|6Y-002| N2eb2b1a025
  N2eb2b1a025:::sink
  N3552820474["manifest declaration only; no service-side check joined; protection=0x1 (danger…"]
  N18ffbe29ad -->|6Y-003| N3552820474
  N3552820474 -->|6Y-003| N76e0ffd5ec
  N76e0ffd5ec -->|6Y-003| N2eb2b1a025
  N2eb2b1a025:::sink
  Nce8aee6830["manifest declaration only; no service-side check joined; protection=UNKNOWN (no…"]
  N18ffbe29ad -->|6Y-004| Nce8aee6830
  Nce8aee6830 -->|6Y-004| N76e0ffd5ec
  N76e0ffd5ec -->|6Y-004| N2eb2b1a025
  N2eb2b1a025:::sink
  Nea4d7e99f1["SystemServer AmazonPackageManagerService.onBootPhase-550 plus PMS.isUpgrade"]
  N6daa3b4d3c["protected RECEIVE_BOOT_AFTER_SYSTEM_OTA plus receiver action-OOBE-retail-demo g…"]
  N9728571969["system-server Context user-derived; numeric user UNKNOWN"]
  N1804f28239["PackageHelper.enableComponent to OobeHomeActivity plus OOBEActivationHelper"]
  Nea4d7e99f1 -->|6Z-001| N6daa3b4d3c
  N6daa3b4d3c -->|6Z-001| N9728571969
  N9728571969 -->|6Z-001| N1804f28239
  N1804f28239:::sink
  Nd870af75f4["BootAfterSystemOTAReceiver guarded lifecycle sender"]
  Nb325bfc840["protected OTA lifecycle plus incremental-OOBE branch; no ordinary caller path; …"]
  N0a3e38649d["ContentResolver user inherited from receiver Context; numeric user UNKNOWN"]
  N1816043bd6["SettingsDBUtils to Settings.Secure-Global user_setup_complete=0 and isOOBEActiv…"]
  Nd870af75f4 -->|6Z-002| Nb325bfc840
  Nb325bfc840 -->|6Z-002| N0a3e38649d
  N0a3e38649d -->|6Z-002| N1816043bd6
  N1816043bd6:::sink
  Neca942c77b["upstream producer UNKNOWN; exported entry has no component permission in saved …"]
  Nfd22abe4bb["manifest action gate plus PROGRAM_ID and PACKAGE_NAME extras; action=com.amazon…"]
  Na0cea9dea9["receiver application user scope and cross-user acceptance UNKNOWN"]
  Nd05e1af285["CDE profile type and OS user type and active-app list persistence to DeviceExpe…"]
  Neca942c77b -->|6Z-003| Nfd22abe4bb
  Nfd22abe4bb -->|6Z-003| Na0cea9dea9
  Na0cea9dea9 -->|6Z-003| Nd05e1af285
  Nd05e1af285:::sink
  N36f1a1c6a4["system/framework USER_SWITCHED producer"]
  N08103db726["protected USER_SWITCHED gate; ordinary sender not established; action=android.i…"]
  N4c58279d75["receiver user and profile scope UNKNOWN"]
  Ncd0abdcf6a["CDE PCA-profile and OS-user persistence plus child active-app-list clear to eva…"]
  N36f1a1c6a4 -->|6Z-004| N08103db726
  N08103db726 -->|6Z-004| N4c58279d75
  N4c58279d75 -->|6Z-004| Ncd0abdcf6a
  Ncd0abdcf6a:::sink
  N1c459bab36["producer UNKNOWN"]
  N4524e2456d["caller must satisfy AmazonAccountPropertyService.property.changed; permission p…"]
  N2b5417a3eb["receiver user scope UNKNOWN"]
  Ndb7f8ca1c1["CDE profile type and OS-user persistence to evaluator"]
  N1c459bab36 -->|6Z-005| N4524e2456d
  N4524e2456d -->|6Z-005| N2b5417a3eb
  N2b5417a3eb -->|6Z-005| Ndb7f8ca1c1
  Ndb7f8ca1c1:::sink
  N8a1497225f["GLOBAL_SYNC required; holder-protection and caller route UNKNOWN; action=com.am…"]
  N23e18fade9["receiver exact user scope UNKNOWN"]
  Ne9467484cc["JobIntentService to GlobalContentSyncEventService to ArcusSyncService.syncCDEPo…"]
  N1c459bab36 -->|6Z-006| N8a1497225f
  N8a1497225f -->|6Z-006| N23e18fade9
  N23e18fade9 -->|6Z-006| Ne9467484cc
  Ne9467484cc:::sink
  N872922ad53["init and system-server loader"]
  Ndadd236623["registered in-process fosinit; no exported app component or external caller evi…"]
  N519c78a453["system-server service identity; Binder publication and caller gate UNKNOWN"]
  N7bd042d796["ProductPolicy service registration only; no verified HOME package Settings or O…"]
  N872922ad53 -->|6Z-007| Ndadd236623
  Ndadd236623 -->|6Z-007| N519c78a453
  N519c78a453 -->|6Z-007| N7bd042d796
  N7bd042d796:::sink
  N19a1cd1c37["Settings UI or shell read path; no new writer established"]
  N0480c378a3["DefaultHomePreferenceController resource gate; normal dashboard omits default_h…"]
  N0d7ccdf6a6["per-user PMS Settings state; exact shell authorization is existing PMS gate; no…"]
  N38452e1933["com.android.server.pm.Settings preferred-activities and persistent-preferred-ac…"]
  N19a1cd1c37 -->|6Z-008| N0480c378a3
  N0480c378a3 -->|6Z-008| N0d7ccdf6a6
  N0d7ccdf6a6 -->|6Z-008| N38452e1933
  N38452e1933:::sink
  N173da53b3e["adb shell getprop"]
  N8ebb5c0f9e["none; observation only"]
  N57a2d20c46["serial G001LT0511550CFT; User 0 current"]
  N973288ebb6["build fingerprint"]
  N173da53b3e -->|6X-LIVE-001| N8ebb5c0f9e
  N8ebb5c0f9e -->|6X-LIVE-001| N57a2d20c46
  N57a2d20c46 -->|6X-LIVE-001| N973288ebb6
  N973288ebb6:::sink
  N10f96ed2ec["shell read-only query"]
  Na582ee99bd["resolver observation"]
  Nd095acab18["User 0"]
  Nfaa2d4a040["formal HOME resolver"]
  N10f96ed2ec -->|6X-LIVE-002| Na582ee99bd
  Na582ee99bd -->|6X-LIVE-002| Nd095acab18
  Nd095acab18 -->|6X-LIVE-002| Nfaa2d4a040
  Nfaa2d4a040:::sink
  Ncf46065b2d["candidate set"]
  N10f96ed2ec -->|6X-LIVE-003| Na582ee99bd
  Na582ee99bd -->|6X-LIVE-003| Nd095acab18
  Nd095acab18 -->|6X-LIVE-003| Ncf46065b2d
  Ncf46065b2d:::sink
  N8592b00ae8["User 10 test profile"]
  N10f96ed2ec -->|6X-LIVE-004| Na582ee99bd
  Na582ee99bd -->|6X-LIVE-004| N8592b00ae8
  N8592b00ae8 -->|6X-LIVE-004| Ncf46065b2d
  Ncf46065b2d:::sink
  N3d74ff5eee["shell read-only dump"]
  N7a897014eb["package-state observation"]
  N87609ba772["User 0 enabled=0; User 10 enabled=2"]
  Nc4278cc979["package state"]
  N3d74ff5eee -->|6X-LIVE-005| N7a897014eb
  N7a897014eb -->|6X-LIVE-005| N87609ba772
  N87609ba772 -->|6X-LIVE-005| Nc4278cc979
  Nc4278cc979:::sink
  N6f47862f18["preferred state observation"]
  Nfd7540caaf["User 0 record"]
  Nf98282e1e2["ordinary preferred activity"]
  N3d74ff5eee -->|6X-LIVE-006| N6f47862f18
  N6f47862f18 -->|6X-LIVE-006| Nfd7540caaf
  Nfd7540caaf -->|6X-LIVE-006| Nf98282e1e2
  Nf98282e1e2:::sink
  N8310f09004["external dump caller; UID UNKNOWN"]
  N145dcaf2a8["android.permission.DUMP protection semantics not re-derived in bounded corpus"]
  N9120d01094["default/device settings user; explicit user overload absent"]
  N0ebd867696["Settings.System.putInt(screen_brightness)"]
  N8310f09004 -->|6X2-IPC-001| N145dcaf2a8
  N145dcaf2a8 -->|6X2-IPC-001| N9120d01094
  N9120d01094 -->|6X2-IPC-001| N0ebd867696
  N0ebd867696:::sink
  N177f58b876["remote Binder caller UNKNOWN"]
  N526059592f["com.amazon.alexa.permission.MODE_SWITCH protection level/holder UNKNOWN"]
  Nddcaff73a5["USER_CURRENT=-2"]
  N1ec8dbec33["SecureSettingsHelper.putIntForUser(orientation_in_previous_mode)"]
  N177f58b876 -->|6X2-IPC-002| N526059592f
  N526059592f -->|6X2-IPC-002| Nddcaff73a5
  Nddcaff73a5 -->|6X2-IPC-002| N1ec8dbec33
  N1ec8dbec33:::sink
  Nb6bc14bded["system_server/input-monitor publisher; external caller UNKNOWN"]
  Nbab1ca7f66["permission and protection UNKNOWN"]
  N2632c2107e["system/default secure scope; non-user overload"]
  Nf5b8e00f7e["Settings.Secure.putInt(camera_shutter_state)"]
  Nb6bc14bded -->|6X2-IPC-003| Nbab1ca7f66
  Nbab1ca7f66 -->|6X2-IPC-003| N2632c2107e
  N2632c2107e -->|6X2-IPC-003| Nf5b8e00f7e
  Nf5b8e00f7e:::sink
  N14d9b4dcdd["external sender UNKNOWN"]
  Na4b1445b6a["com.amazon.kindle.otter.oobe.OOBE_PERMISSION protection level and holder UNKNOWN"]
  N93b98ca5a0["downstream Settings/HOME/package sink not joined"]
  N14d9b4dcdd -->|6X2-IPC-004| Na4b1445b6a
  Na4b1445b6a -->|6X2-IPC-004| N2b5417a3eb
  N2b5417a3eb -->|6X2-IPC-004| N93b98ca5a0
  N93b98ca5a0:::sink
  Nfb5baa0963["com.amazon.dcp.sso.permission.AmazonAccountPropertyService.property.changed pro…"]
  Nbb508a1c68["CDE/profile persistence and evaluator; no HOME/PMS/OTA sink"]
  N1c459bab36 -->|6X2-IPC-005| Nfb5baa0963
  Nfb5baa0963 -->|6X2-IPC-005| N2b5417a3eb
  N2b5417a3eb -->|6X2-IPC-005| Nbb508a1c68
  Nbb508a1c68:::sink
  N050991d253["production caller UNKNOWN; test-only callers excluded"]
  Nb10852373e["register: no local permission; deregister: creator UID equality gate; protectio…"]
  N9f14c6a4d7["user scope not explicit; receiver map only"]
  Nee0052ecca["implicit receiver registration map; first package/HOME sink NOT_FOUND"]
  N050991d253 -->|6X2-IPC-006| Nb10852373e
  Nb10852373e -->|6X2-IPC-006| N9f14c6a4d7
  N9f14c6a4d7 -->|6X2-IPC-006| Nee0052ecca
  Nee0052ecca:::sink
  Nc0965cede0["external client UNKNOWN"]
  N5c62c4b9d0["signature BIND_SERVICE declaration; exact holder/grant join UNKNOWN"]
  N4c7a7442f1["trusted adult/child profile scope; exact user data-flow partial"]
  N0ea42802af["user creation/removal and profile Settings relay; no HOME/PMS component sink"]
  Nc0965cede0 -->|6X2-IPC-007| N5c62c4b9d0
  N5c62c4b9d0 -->|6X2-IPC-007| N4c7a7442f1
  N4c7a7442f1 -->|6X2-IPC-007| N0ea42802af
  N0ea42802af:::sink
  Ncb27cea5ab["caller/package/account provenance UNKNOWN"]
  Nf0bfc2d9d8["o() and qualification gates; exact permission protection UNKNOWN"]
  N0c7b116beb["UserHandle.myUserId plus injected user/profile semantics UNKNOWN"]
  N6c679c1368["secure-settings-class writer; browser-default/install bookkeeping; no HOME/Fire…"]
  Ncb27cea5ab -->|6X2-IPC-008| Nf0bfc2d9d8
  Nf0bfc2d9d8 -->|6X2-IPC-008| N0c7b116beb
  N0c7b116beb -->|6X2-IPC-008| N6c679c1368
  N6c679c1368:::sink
  N00b058b2b5["official OTA ZIP"]
  N75e7954111["PS7331.4463N trona release OTA; SHA-256 9f50d2f321f31d2db6bff9bc463cd5faa3597b2…"]
  Nb9f123cedf["PS7331"]
  N00b058b2b5 -->|6X2-OTA-001| N75e7954111
  N75e7954111 -->|6X2-OTA-001| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-001| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nf5c282f367["ZIP member inventory"]
  Na592fae6f1["META-INF metadata otacert update-binary updater-script; .new.dat.br; transfer l…"]
  Nf5c282f367 -->|6X2-OTA-002| Na592fae6f1
  Na592fae6f1 -->|6X2-OTA-002| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-002| N25ba44ec3b
  N25ba44ec3b:::unknown
  Ne557fa2a4d["No payload.bin and no A/B postinstall executable member"]
  Nf5c282f367 -->|6X2-OTA-003| Ne557fa2a4d
  Ne557fa2a4d -->|6X2-OTA-003| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-003| N25ba44ec3b
  N25ba44ec3b:::unknown
  N7e620f7c75["updater-script assertions"]
  Ne40e1df0a5["Build date and ro.product.device trona assertions"]
  N7e620f7c75 -->|6X2-OTA-004| Ne40e1df0a5
  Ne40e1df0a5 -->|6X2-OTA-004| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-004| N25ba44ec3b
  N25ba44ec3b:::unknown
  N58014ea616["SideloadMetadataChecker.check"]
  N52d5c5c240["Version signature-transition product and PVT checks"]
  N58014ea616 -->|6X2-OTA-005| N52d5c5c240
  N52d5c5c240 -->|6X2-OTA-005| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-005| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nc2e059682e["SideloadVerifier.verifySideloadWithRecoveryCheck"]
  Nab5559a9fd["Sanity metadata RecoverySystemWrapper.verifyPackage device state"]
  Nc2e059682e -->|6X2-OTA-006| Nab5559a9fd
  Nab5559a9fd -->|6X2-OTA-006| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-006| N25ba44ec3b
  N25ba44ec3b:::unknown
  N9a2dcfa1fe["OSUpdateValidator.validateOSUpdate"]
  Nd6f347774a["Hash then RecoverySystem.verifyPackage then OSUpdatePropertiesValidator"]
  N9a2dcfa1fe -->|6X2-OTA-007| Nd6f347774a
  Nd6f347774a -->|6X2-OTA-007| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-007| N25ba44ec3b
  N25ba44ec3b:::unknown
  N3f3fb27719["SideloadMover.maybeMoveSideloadFile"]
  N72f5ec86a2["Basename destination and FileHelper.moveFile"]
  N3f3fb27719 -->|6X2-OTA-008| N72f5ec86a2
  N72f5ec86a2 -->|6X2-OTA-008| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-008| N25ba44ec3b
  N25ba44ec3b:::unknown
  N29f712417f["SideloadInstaller.installSideload"]
  Nfc41156c27["Metadata/device checks then mover then installOSUpdate"]
  N29f712417f -->|6X2-OTA-009| Nfc41156c27
  Nfc41156c27 -->|6X2-OTA-009| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-009| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nd68393dbfe["UpdateSystemWrapper.install"]
  N68b00bfab7["Path prefix remap settings write then UpdateSystem.install"]
  Nd68393dbfe -->|6X2-OTA-010| N68b00bfab7
  N68b00bfab7 -->|6X2-OTA-010| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-010| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nd4e90e2134["OTA controller holders"]
  Nc1518e9461["com.amazon.dcp.ota.permission.CONTROLLER and PROCESS_UPDATES protected surface"]
  Nd4e90e2134 -->|6X2-OTA-011| Nc1518e9461
  Nc1518e9461 -->|6X2-OTA-011| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-011| N25ba44ec3b
  N25ba44ec3b:::unknown
  Ncfdca8a2ca["main to block-image registry"]
  N70805dcda8["RegisterBlockImageFunction to RegisterFunction; block_image_update to BlockImag…"]
  Ncfdca8a2ca -->|6X2-OTA-012| N70805dcda8
  N70805dcda8 -->|6X2-OTA-012| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-012| N25ba44ec3b
  N25ba44ec3b:::unknown
  Ne1d487672e["PackageExtractFileFn"]
  N4cb44971a5["PackageExtractFileFn to ota_open to open and extraction fsync close"]
  Ne1d487672e -->|6X2-OTA-013| N4cb44971a5
  N4cb44971a5 -->|6X2-OTA-013| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-013| N25ba44ec3b
  N25ba44ec3b:::unknown
  Na11bf86d4f["BlockImageUpdateFn to WriteToPartition"]
  N3ffdb959c7["PerformBlockImageUpdate to WriteToPartition to ota_write to write"]
  Na11bf86d4f -->|6X2-OTA-014| N3ffdb959c7
  N3ffdb959c7 -->|6X2-OTA-014| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-014| N25ba44ec3b
  N25ba44ec3b:::unknown
  N4f6570f8f8["updater-script"]
  Nd321f2f514["system vendor boot preloader lk tee1 tee2 spmfw sspm_1 cam_vpu1 cam_vpu2 cam_vp…"]
  N4f6570f8f8 -->|6X2-OTA-015| Nd321f2f514
  Nd321f2f514 -->|6X2-OTA-015| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-015| N25ba44ec3b
  N25ba44ec3b:::unknown
  N895e516192["MakeFreeSpaceOnCache"]
  N854cecd134["0x417bf0 to __readlink_chk 0x4ce4e8"]
  N895e516192 -->|6X2-OTA-016| N854cecd134
  N854cecd134 -->|6X2-OTA-016| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-016| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nf736d7b7aa["selected direct-call graph"]
  Ne7099e8895["No selected direct edge from readlink helper to extraction/block-image/write si…"]
  Nf736d7b7aa -->|6X2-OTA-017| Ne7099e8895
  Ne7099e8895 -->|6X2-OTA-017| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-017| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nacb23beced["CacheSizeCheck and callers"]
  N450bed7137["Body return/error branches and all indirect dispatch not fully selected"]
  Nacb23beced -->|6X2-OTA-018| N450bed7137
  N450bed7137 -->|6X2-OTA-018| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-018| N25ba44ec3b
  N25ba44ec3b:::unknown
  N6cd46d717a["platform recovery verifier"]
  N6f65713725["RecoverySystemWrapper delegates to platform RecoverySystem; exact native verifi…"]
  N6cd46d717a -->|6X2-OTA-019| N6f65713725
  N6f65713725 -->|6X2-OTA-019| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-019| N25ba44ec3b
  N25ba44ec3b:::unknown
  N5e91b606ab["otacert and verifyPackage"]
  Nb85ec5e1a4["Certificate material plus verification API call boundary"]
  N5e91b606ab -->|6X2-OTA-020| Nb85ec5e1a4
  Nb85ec5e1a4 -->|6X2-OTA-020| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-020| N25ba44ec3b
  N25ba44ec3b:::unknown
  Nd796ab4ec7["bootloader/recovery rollback index"]
  Nfad98cd969["No exact rollback-index decision branch in saved corpus"]
  Nd796ab4ec7 -->|6X2-OTA-021| Nfad98cd969
  Nfad98cd969 -->|6X2-OTA-021| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-021| N25ba44ec3b
  N25ba44ec3b:::unknown
  N240be13042["shell UID / ordinary app"]
  Ne535bb6575["No saved caller chain from shell or ordinary APK to UpdateSystem.install/recove…"]
  N240be13042 -->|6X2-OTA-022| Ne535bb6575
  Ne535bb6575 -->|6X2-OTA-022| Nb9f123cedf
  Nb9f123cedf -->|6X2-OTA-022| N25ba44ec3b
  N25ba44ec3b:::unknown
  N7a0d4dfaac["installed device snapshot"]
  N9f9a75989e["Installed snapshot PS7330.4104N versus adjacent OTA PS7331.4463N"]
  N6d0fd1b20d["PS7330"]
  N7a0d4dfaac -->|6X2-OTA-023| N9f9a75989e
  N9f9a75989e -->|6X2-OTA-023| N6d0fd1b20d
  N6d0fd1b20d -->|6X2-OTA-023| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-001| N25ba44ec3b
  N25ba44ec3b -->|AC-001| N25ba44ec3b
  N25ba44ec3b -->|AC-001| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-002| N25ba44ec3b
  N25ba44ec3b -->|AC-002| N25ba44ec3b
  N25ba44ec3b -->|AC-002| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-003| N25ba44ec3b
  N25ba44ec3b -->|AC-003| N25ba44ec3b
  N25ba44ec3b -->|AC-003| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-004| N25ba44ec3b
  N25ba44ec3b -->|AC-004| N25ba44ec3b
  N25ba44ec3b -->|AC-004| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-005| N25ba44ec3b
  N25ba44ec3b -->|AC-005| N25ba44ec3b
  N25ba44ec3b -->|AC-005| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-006| N25ba44ec3b
  N25ba44ec3b -->|AC-006| N25ba44ec3b
  N25ba44ec3b -->|AC-006| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-007| N25ba44ec3b
  N25ba44ec3b -->|AC-007| N25ba44ec3b
  N25ba44ec3b -->|AC-007| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-008| N25ba44ec3b
  N25ba44ec3b -->|AC-008| N25ba44ec3b
  N25ba44ec3b -->|AC-008| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-009| N25ba44ec3b
  N25ba44ec3b -->|AC-009| N25ba44ec3b
  N25ba44ec3b -->|AC-009| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-010| N25ba44ec3b
  N25ba44ec3b -->|AC-010| N25ba44ec3b
  N25ba44ec3b -->|AC-010| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|AC-011| N25ba44ec3b
  N25ba44ec3b -->|AC-011| N25ba44ec3b
  N25ba44ec3b -->|AC-011| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6X2-ROUTES-001| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-001| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-001| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6X2-ROUTES-002| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-002| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-002| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6X2-ROUTES-003| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-003| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-003| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6X2-ROUTES-004| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-004| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-004| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6X2-ROUTES-005| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-005| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-005| N25ba44ec3b
  N25ba44ec3b:::unknown
  N25ba44ec3b -->|6X2-ROUTES-006| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-006| N25ba44ec3b
  N25ba44ec3b -->|6X2-ROUTES-006| N25ba44ec3b
  N25ba44ec3b:::unknown
```
