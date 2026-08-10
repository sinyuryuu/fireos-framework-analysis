# Phase 6WF — live ProductPolicy XML read-only check

## Scope

This is a single exact-serial, read-only check of the policy files consumed by
the statically identified `AmazonProductPolicyService`. No package/component
state, settings, user/profile state, HOME resolver, service, or system image was
modified.

Device evidence:

- Serial: `G001LT0511550CFT`
- Fingerprint: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- Incremental: `0031575863172`
- Raw capture: `artifacts/phase6wf-product-policy-readonly-20260810-01/`

## Static-to-live join

The exact Fire OS disassembly shows `AmazonProductPolicyService` parsing these
files from `/system/etc/` at `disassembly.log:56550-56590` and dispatching
entries through `IAction.performAction` at `:56508-56516`. The
`EnableDisableComponentAction` sink calls Amazon PackageManager enabled-state
APIs at `:293688`, `:293698`, `:293736`, and `:293742`. Its event logic covers
user switch, create-user, PFM, device-region, mode-change, and upgrade paths;
the device-region path iterates `UserManagerService.getUsers()` and passes each
`UserInfo.id` at `:294136-294168`.

The live read-only files show:

| File | Observed content | Verdict |
|---|---|---|
| `global_policy.xml` | Empty `<policy/>` | **已證實：no live entry** |
| `common_device_policy.xml` | Child-only Cloud9/Cloud9 content/kids browser entries on `onUserSwitch` | **已證實：no Fire Launcher entry** |
| `multimodal_device_policy.xml` | Adult/child disable rules for Paladin and ECS on `onUserSwitch` | **已證實：no Fire Launcher entry** |
| `receiver_filter_policy.xml` | Static Facebook activity filtering for SEND intents | **已證實：not a HOME/package-state writer** |
| `product_policy.xml` | `/system/etc` object absent on this live device; pull returned `No such file or directory` | **待驗證：target file-map vs installed layout mismatch** |

## Decision

The accessible live policy inputs do not explain Fire Launcher restoration or
User-0 HOME selection. They do confirm that ProductPolicy is a real privileged
package/component-state writer for other scoped policy entries, but no evidence
connects this live input set to `com.amazon.firelauncher`.

The absent `product_policy.xml` is not treated as proof that no product policy
is applied: the PS7331 OTA file map lists `/system/etc/product_policy.xml`,
while the live path is absent. The remaining possibilities are an image/layout
variant, an extraction/provenance mismatch, or an alternate policy source.
This boundary requires host-side exact-image extraction or a matching artifact;
it does not justify triggering ProductPolicy events or calling private services.

## Verdicts

- **已證實:** four accessible live policy files were read without mutation;
  none contains `com.amazon.firelauncher`.
- **高可信推論:** the visible ProductPolicy entries are child/adult scoped
  feature policy, not the User-0 Fire HOME selector.
- **待驗證:** the source and delivered location/content of `product_policy.xml`
  and any alternate policy input.
- **已排除:** the accessible `global`, `common_device`, `multimodal`, and
  receiver-filter files as direct Fire Launcher writers.
- **因風險拒絕測試:** no event injection, private Binder call, package-state
  setter, reboot, or policy mutation was attempted.

## Reproduction

```sh
tools/scripts/capture_phase6wf_product_policy.sh \
  --serial G001LT0511550CFT \
  --output artifacts/phase6wf-product-policy-readonly-YYYYMMDD-NN
```

The script refuses to overwrite an existing output directory and records raw
pull logs plus SHA-256 values.
