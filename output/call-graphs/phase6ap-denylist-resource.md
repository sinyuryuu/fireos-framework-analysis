# Phase 6AP deny-list resource closure

```text
AmazonPackageManagerService / DenyListArcusHelper.processJSON()
  [PS7331 services VDEX consumer]
      |
      +--> Resources.getSystem().openRawResource(0x7e05000a)
              |
              +--> fireos-res.apk, package ID 0x7e (amazon.fireos)
                      |
                      +--> amazon.fireos:raw/package_manager_deny_list
                              |
                              +--> JSON packages_deny_list
                                      |
                                      +--> com.amazon.firelauncher
                                              |
                                              +--> PackageManagerDenyList seed
                                                      |
                                                      +--> ControlProtectedPackagesCallback
                                                              |
                                                              +--> setComponentEnabledSetting rejection
                                                                    before state mutation
```

The resource mapping and package membership are directly extracted from the
preserved PS7331 `system.img` by the host-only audit script. The VDEX consumer
is existing static evidence; this graph does not imply that every package
operation shares the same enforcement path.
