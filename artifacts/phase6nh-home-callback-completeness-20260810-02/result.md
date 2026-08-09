# Phase 6NH — collected HOME callback completeness audit

## Scope

This is a host-only audit of the preserved PS7331 `fosinit` XML and services
VDEX disassembly. It does not invoke `adb`, Binder, the OTA updater, or any
device operation. It answers only whether the collected configuration names
additional `VendorActivityStackSupervisorCallback` implementations and
whether those implementations contain a concrete `resolveIntent` method.

## Result

The audit found the complete set of matching callback registrations in the
collected XML directory and mapped each registration against both collected
services disassembly logs. A callback is not treated as absent from the real
device merely because it is absent from this preserved artifact set; that
residual limitation is recorded explicitly.

### com.amazon.android.server.am.AppCompatActivityStackSupervisorCallback
- XML: `artifacts/amazon-services/appcompatsupport_fosinit.xml` (SHA-256 `e89888106c2cdde0b39f2c97e3ebefde7502919adf688cd5c2b9db458302ee8e`)
- class in collected VDEX: `True`
- concrete `resolveIntent`: `True`
- direct `IPackageManager.resolveIntent`: `True`
- exception/null return path observed: `True`

```text
virtual_method #5024: resolveIntent (Landroid/content/Intent;Ljava/lang/String;II)Landroid/content/pm/ResolveInfo;
    access=0001 (PUBLIC)
    codeOff=37954 (227668)
    quickening_size=0 (0)
      037958: 1200                                   |0000: const/4 v0, #int 0 // #0
      03795a: 0701                                   |0001: move-object v1, v0
      03795c: 7100 b001 0000                         |0002: invoke-static {}, Landroid/app/AppGlobals;.getPackageManager:()Landroid/content/pm/IPackageManager; // method@01b0
      037962: 0c02                                   |0005: move-result-object v2
      037964: 1503 0100                              |0006: const/high16 v3, #int 65536 // #1
      037968: b683                                   |0008: or-int/2addr v3, v8
      03796a: d633 0004                              |0009: or-int/lit16 v3, v3, #int 1024 // #0400
      03796e: d633 0020                              |000b: or-int/lit16 v3, v3, #int 8192 // #2000
      037972: 7257 b502 5236                         |000d: invoke-interface {v2, v5, v6, v3, v7}, Landroid/content/pm/IPackageManager;.resolveIntent:(Landroid/content/Intent;Ljava/lang/String;II)Landroid/content/pm/ResolveInfo; // method@02b5
      037978: 0c02                                   |0010: move-result-object v2
      03797a: 0721                                   |0011: move-object v1, v2
      03797c: 7020 9f13 1400                         |0012: invoke-direct {v4, v1}, Lcom/amazon/android/server/am/AppCompatActivityStackSupervisorCallback;.isUninstalledApp:(Landroid/content/pm/ResolveInfo;)Z // method@139f
      037982: 0a02                                   |0015: move-result v2
      037984: 3902 0300                              |0016: if-nez v2, 0019 // +0003
      037988: 1101                                   |0018: return-object v1
      03798a: 2802                                   |0019: goto 001b // +0002
      03798c: 0d02                                   |001a: move-exception v2
      03798e: 1100                                   |001b: return-object v0
```

### com.fireos.eve.EveActivityStackSupervisorCallback
- XML: `artifacts/amazon-services/eve_launch_time_fosinit.xml` (SHA-256 `95f31591f3fd288565bb6901b3e9cb59a13ae782fc3de3f66ad48020a9b22efd`)
- class in collected VDEX: `True`
- concrete `resolveIntent`: `False`
- direct `IPackageManager.resolveIntent`: `False`
- exception/null return path observed: `False`
