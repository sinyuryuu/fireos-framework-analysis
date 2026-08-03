# AOSP Android 9 versus Fire OS HOME path

## Scope

The comparison uses the selected Android 9 r1 and r61 PackageManager sources,
the Fire OS JADX source, and matching VDEX instruction listings. It is not a
claim that every Fire OS class is byte-for-byte comparable to either AOSP tag.

| Area | AOSP-standard behavior | Fire OS evidence | Classification |
|---|---|---|---|
| `PackageManagerService.resolveIntent` | Query candidates, then choose best | Same method chain and priority/preferred structure | `AOSP_STANDARD` |
| `chooseBestActivity` | Priority/order/default comparison precedes ordinary preferred tie path | Same decision shape in selected Fire OS source | `AOSP_STANDARD` |
| `findPreferredActivity` / persistent helper | Preferred and persistent resolver helpers exist | Same method family exists | `AOSP_STANDARD` / version-aware |
| `ActivityStackSupervisor.resolveIntent` | Standard PM internal resolution | Fire calls vendor callback array first, then PM internal | `AMAZON_ADDITION` |
| Home short press | Framework launches Home | Fire calls `KeyPolicyManager` before framework behavior | `AMAZON_ADDITION` |
| `startDockOrHome` | Framework Home intent launch | Fire adds custom-dock and on-start vendor callbacks | `AMAZON_ADDITION` |
| Fire package identity | No AOSP package | Privileged `/system/priv-app` package with manifest priority 50 | `AMAZON_ADDITION` package data |
| explicit Fire target inside selected PM chooser | Not applicable | No selected package-name branch found | `UNKNOWN` outside inspected classes; Probable absent in scope |

## Minimum difference explaining current result

The minimum evidence-backed difference is not a resolver algorithm patch: it is
the OEM-installed privileged Fire Launcher candidate with effective priority
50, while sideloaded launchers are capped at effective priority 0. The Fire OS
framework also exposes Amazon callback boundaries around resolution and Home-key
handling, but the preserved data does not show those callbacks replacing the
result for the normal tablet mode.

## Important non-equivalence

The existence of a vendor callback is not proof that it returns a Fire
`ResolveInfo`; the callback aggregator returns null when no callback claims the
intent. Likewise, a Home-key hook is not proof that the key bypasses the HOME
intent. The clean keyevent log shows the same explicit Fire destination as the
explicit HOME sample.
