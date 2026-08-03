# Phase 5D — Amazon LK unlock surface and public-route compatibility

## Scope

This phase follows the failed `mtk-easy-su` root-control attempt and the
exact-source tail search. It reviews three public projects against the
available adjacent PS7331 bootloader artifacts and performs one bounded,
read-only attempt to read the installed PS7330 LK block through the Android
shell.

No root exploit, BROM connection, DA upload, fastboot unlock, certificate
submission, `seccfg` change, reboot, remount, erase, or partition write was
executed.

Device:

| Field | Value |
|---|---|
| Serial | `G001LT0511550CFT` |
| Model/product | `KFTRWI` / `trona` |
| SoC | MT8183 |
| Installed build | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` |
| Fire OS / Android | 7.3.3.0 / Android 9 API 28 |
| Security state | verified boot green; `ro.boot.flash.locked=1`; SELinux Enforcing |
| Android-visible boot descriptors | PL `d1a4a4b-20231011_072631`; LK `79172a1-20231008_072039` |

Raw and derived evidence is under
`artifacts/phase5/public-lk-route-review-20260803/`.

The post-check in `ps7330-postcheck.txt` confirms that the Android-visible
state remained unchanged after the bounded LK read attempt.

## New finding: Amazon has a signed temporary-unlock surface in the adjacent LK

The PS7331 `lk.img` contains the following string cluster:

| Offset | String |
|---:|---|
| `0x04b254` | `amzn_verify_unlock` |
| `0x04b284` | `amzn_get_temp_unlock_idme_code` |
| `0x04b388` | `amzn_get_temp_unlock_idme_data` |
| `0x04b3a8` | `amzn_get_temp_unlock_idme_cert` |
| `0x04b3c8` | `amzn_verify_temp_unlock_code` |
| `0x04b435` | `Device is temporarily unlocked, %d reboots remaining` |
| `0x04e883` | `flash:unlock` |
| `0x04e890` | `flash:tucert` |
| `0x04ec67` | `unlock signature verify failed, do nothing!` |
| `0x07a426` | `getvar:unlock_code` |
| `0x07a439` | `getvar:unlock_status` |
| `0x086577` | `Vt_unlock_code` |
| `0x086597` | `Vt_unlock_cert` |

This is **Confirmed, artifact-scoped**: the adjacent PS7331 LK contains an
Amazon-specific unlock/certificate path. It is not proof that the installed
PS7330 build accepts a caller-provided certificate, nor that a valid
certificate/code is publicly obtainable.

The string `Device is temporarily unlocked, %d reboots remaining` is
especially important. It indicates a time/reboot-bounded state rather than a
generic Android setting. The relevant input names (`tucert`, unlock code and
IDME data) point to an Amazon-signed or factory-authorized credential path.
No credential was found in the Android baseline or public source review.

## Exact PS7330 LK is not shell-readable

The shell-visible device node exists as a symlink to the LK block, but a
bounded read returned:

```text
dd: /dev/block/platform/bootdevice/by-name/lk: Permission denied
```

This is **Confirmed for the tested shell context**. It does not prove that the
block is unreadable with root, a DA, or a signed service; it proves only that
the current Android shell cannot supply the exact PS7330 LK image needed for a
device-specific static match.

The IDME HAL is present in `lshal` as
`fireos.hardware.idme@1.1::IIdme/default`, but `dumpsys idme` reports no
Android service and no `idme` shell binary is installed. No unknown Binder
transaction was attempted. This leaves the Amazon unlock credential source
unresolved.

## Public project compatibility

### `lkpatcher`

The pinned source is commit
`68034be95401da72ab17251e57d224c0a942d8ad`. Its default patterns and comments
are for specific LK layouts, including OPlus `oplusreserve` lock logic. A
byte-count check against the adjacent PS7331 LK found zero matches for all
six default needles. This is **Confirmed for the adjacent artifact**, not a
claim about PS7330.

It also states that patched images require `seccfg` handling, matching LK
images, and backups. It is an offline patcher, not an ADB-only route and not a
source of an Amazon unlock certificate.

### `pwnage24mtk`

The pinned source is commit
`14df908af0ef6d748888b8f07cdccf9341eb16fb`. Its README describes a
CERT1/CERT2 ASN.1 parsing issue and image reconstruction workflow. Running
its read-only parser against the adjacent PS7331 `lk.img` produced one `lk`
part-header image and `total: 0 sub-image(s)`; its verifier reported:

```text
error: no signed target with following CERT1/CERT2 found
```

Running the same part-header parser against the adjacent preloader failed at
the first bytes (`0x434d4d45`, `EMMC_BOOT`, rather than `0x58881688`). This is
**Confirmed as an input-format mismatch for the inspected files**. It does
not disprove that Amazon authenticates the boot chain; the preloader's own
strings contain certificate, DA-authentication, SBC, and RPMB paths.

### `fenrir`

The pinned source is commit
`39688713455ea81667003c240dd53ce7310681b8`. Its device list contains
Pacman/PacmanPro, Tetris, Q25, LG7n/LG8n/LH7n, several Redmi/Xiaomi and
related devices. It has no `trona`, `KFTRWI`, or MT8183 Amazon profile, and
its payload headers contain device-specific stage addresses. Porting it would
require exact boot-chain reverse engineering and a low-level execution/write
primitive. It was not built or run.

## Route decision tree

```text
Amazon temporary unlock strings in adjacent LK
  ├─ exact PS7330 LK available to compare? ── no: Android shell read denied
  ├─ valid Amazon tucert/unlock credential found? ── no
  ├─ public exact trona implementation? ── no
  └─ decision: research lead only; no safe command exists to execute now

lkpatcher
  ├─ exact device-specific pattern match? ── no match in PS7331 artifact
  └─ decision: reject as generic route

pwnage24mtk
  ├─ CERT1/CERT2 target in available LK? ── no
  └─ decision: reject as an unverified input-format port

fenrir
  ├─ supported trona/KFTRWI profile? ── no
  └─ decision: reject as a device-specific boot-chain exploit port
```

## Classification

| Finding | Status |
|---|---|
| Amazon LK has an unlock/temporary-unlock code path | **Confirmed, PS7331 artifact-scoped** |
| The path uses a public, arbitrary shell-writable credential | **Disproved by current evidence**; no such input found |
| Exact PS7330 LK can be statically matched from Android shell | **Disproved for tested shell context**; read denied |
| `lkpatcher` is a drop-in route for this tablet | **Disproved for inspected adjacent LK**; zero default-pattern matches |
| `pwnage24mtk` can process the available LK/preloader pair | **Disproved for inspected file formats** |
| `fenrir` supports this tablet | **Disproved by pinned device list** |
| A new exact-device root/unlock route is ready for execution | **Disproved** |
| Amazon-signed temporary unlock may be worth further research | **High-confidence lead**, pending exact PS7330 LK and credential-source evidence |

## Level 3 boundary for a future Amazon certificate test

No execution approval is requested by this report because the required
credential and exact PS7330 bootloader input are absent. If a valid,
device-matched `tucert` and exact PS7330 protocol are later obtained, the
operation must be reviewed separately with these fields:

- Operation: submit/query the Amazon temporary-unlock certificate path in the
  exact PS7330 bootloader.
- Purpose: determine whether an authorized temporary unlock changes the
  bootloader state without permanently writing an unverified image.
- Why ADB is insufficient: Android shell cannot read LK and does not expose
  the IDME HAL as a shell command.
- Exact commands and files: currently **unknown**; no `flash:tucert`,
  `flash:unlock`, `fastboot flashing unlock`, DA, BROM or certificate command
  was run.
- Compatibility: must match `PS7330.4104N`, PL descriptor
  `d1a4a4b-20231011_072631`, LK descriptor `79172a1-20231008_072039`, and
  Amazon's credential/signature format.
- Risks: temporary or persistent boot-state change, data loss, anti-rollback
  interaction, failed boot, and no guaranteed recovery without an exact stock
  PS7330 set.
- Recovery: not established; `fastboot reboot` is not a recovery plan for a
  failed authenticated boot-chain state.
- Alternative: continue host-only source/firmware discovery and request a
  read-only, exact-device protocol review before any command is selected.

This section is a **Level 3 proposal boundary, not authorization**.

## Conclusion

The failed root APK did not close the research. It exposed a more precise
direction: Amazon's bootloader has a product-specific signed temporary-unlock
surface, but the current public and local evidence lacks both sides required
to use it—an exact PS7330 LK image and a valid Amazon credential/protocol.

The best next safe step is not another generic root APK or MTK payload. It is
to obtain an authorized exact PS7330 boot-chain artifact or documented Amazon
unlock credential path, then perform a source-only compatibility review. Until
then, BROM/DA, `seccfg`, LK patching, `flash:tucert`, and partition writes
remain rejected experiments.
