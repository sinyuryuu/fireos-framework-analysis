# Phase 6LZ — component-state permission holder audit

## Scope

This is a host-only parse of the preserved package-manager dump. It answers a
narrow question: which installed packages were recorded as holding
`android.permission.CHANGE_COMPONENT_ENABLED_STATE`? It does **not** test the
permission, grant it, call a package API, or infer a protected-package bypass.

Input:

- `artifacts/phase6j/phase6j-ota-controller-holders-20260805-01/dumpsys_package_all.stdout.txt`
- SHA-256: `6f2754f4e9655567524de00c5b044326cbd992d6a9022b87397369fb5b905909`

The canonical hash is emitted by the reproducible parser under
`output/tables/phase6lz-component-state-permissions/result.json`.

## Result

The permission definition in the same saved package dump is:

```text
Permission [android.permission.CHANGE_COMPONENT_ENABLED_STATE]
sourcePackage=android
uid=1000
prot=signature|privileged
```

The holder inventory contains system/privileged Amazon packages, managed
provisioning, SystemUI-related packages, and a notable data-app snapshot for
`com.android.vending`. The latter is recorded as `granted=true` while its
saved code path is `/data/app/...` and its private flags do not include
`PRIVILEGED`. That is an evidence item requiring provenance review, not proof
of an exploitable grant: the dump does not show how the grant was established,
what APIs the Play Store calls, or whether the Fire Launcher protected-package
gate would accept its caller.

The reproducible parser found 11 package blocks with this granted permission.
It intentionally stops package parsing at the dump's `Shared users:` section;
shared-user records are not counted as package holders.

## Relevant evidence

- Permission definition: `dumpsys_package_all.stdout.txt:10107-10110`.
- `com.android.vending` holder snapshot: `:21397-21463`; data path and
  non-privileged flags at `:21400-21411`, grant at `:21452-21464`.
- `com.amazon.tahoe` holder snapshot: `:23704-23718` and its grant block
  immediately below.
- `com.amazon.cloud9.kids` holder snapshot and grant:
  `:31118-31157`.
- Amazon KFT state writer remains a separate system-server path:
  `fosservices/disassembly.log:54297-54325` and
  `artifacts/phase6ay/launcher-state-services-20260805-02/selected-method-snippets.txt`.
- Existing component-disable tests prove that a state-changing caller still
  meets the protected-package gate before Fire Launcher state changes. The
  holder table does not invalidate those results.

## Confidence labels

- **Confirmed:** the saved dump records the permission definition and the
  listed `granted=true` holder states.
- **Strong evidence:** most holders are system/privileged packages with
  Amazon/platform signatures; the permission is not an ordinary runtime
  permission.
- **待驗證:** provenance of the Play Store data-app grant and whether its
  implementation ever invokes the relevant API.
- **已排除:** this table alone is not a shell-to- Fire-Launcher bypass, not a
  HOME replacement, and not a root path.

## Safe next step

Only a host-side provenance comparison is justified: compare the saved
`com.android.vending` package metadata against its manifest/signature and
privapp/permission configuration if those artifacts are already available.
Do not invoke Play Store components, grant/revoke permissions, or repeat the
Fire Launcher disable test solely because the holder appears in this dump.

## Reproduction

```sh
python3 tools/scripts/audit_phase6lz_component_state_permissions.py \
  --output-dir output/tables/phase6lz-component-state-permissions
python3 -m py_compile tools/scripts/audit_phase6lz_component_state_permissions.py
```

The parser performs no device operation.
