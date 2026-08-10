# Phase 6TW — H2 custom permission owner/grant/client closure

日期：2026-08-10（Asia/Taipei）

## Bounded result

Host-only exact-build closure is **OWNER POSITIVE / EXPLICIT GRANTS POSITIVE / REQUESTED-PERMISSION DECLARATION UNKNOWN / ACTUAL BIND CLIENT UNKNOWN**.

The strongest owner record is the preserved exact-build PackageManager permission dump: `com.amazon.alta.h2clientservice.permission.BIND_SERVICE` has `sourcePackage=android.amazon.perm`, owner UID `1000`, `packageSetting=android.amazon.perm/1000`, and `prot=signature|amazon` (CSV row 2). This is a custom permission owner record; it is not inferred from H2's UID, priv-app placement, or platform grants.

The exact-build H2 XML-tree independently records the symbolic declaration with raw `protectionLevel=0x2` (signature) at lines 69–74 (CSV row 3). The same corpus records H2 package UID `10012`, path `/system/priv-app/com.amazon.h2clientservice`, and signing digest `e627f73a` (CSV row 4). These identify the service package, not the effective custom owner.

Ten package records explicitly contain `com.amazon.alta.h2clientservice.permission.BIND_SERVICE: granted=true`: `com.amazon.venezia` (UID 10076), `com.amazon.h2settingsfortablet` (10130), `com.amazon.csapp` (10077), `com.amazon.tahoe` (10128), `com.amazon.kindle.otter.oobe` (10023), `com.amazon.wifilocker` (10069), `com.amazon.ags.app` (10046), `com.amazon.parentalcontrols` (10058), `com.amazon.avod` (10106), and `com.amazon.kindle` (10052). Their package records show signing digest `e627f73a`. These are **explicit custom grants and client candidates**, not proof that each package actually binds H2. No Binder/service operation was performed.

## Requested-permission and policy boundary

The bounded artifacts expose install-permission/grant records, but do not provide a complete per-package manifest `uses-permission` declaration for each grantee. Therefore `requested_permission=UNKNOWN` is retained for every candidate. An install grant must not be upgraded into an actual bind client without a static manifest request plus code-level bind edge.

The bounded `privapp_permissions.xml`, `privapp-permissions-platform.xml`, and `framework-sysconfig.xml` search found no matching custom H2 entry. The H2 policy block only records platform permissions. Accordingly, platform grants, UID 10012, system-priv-app status, and package signing digest are not treated as custom holders or custom grants. The effective custom owner is supported only by the explicit `sourcePackage` record above.

## Client closure

The bounded JADX corpus contains the generated `IH2ClientService` contract and H2 implementation, but no additional production implementation/bind caller. The service-resolution record confirms `H2ClientService` is gated by the custom permission; it does not identify an external accepted caller. Thus actual client package/UID remains **UNKNOWN** even though the ten explicit grants are listed as candidates.

## Safe boundary

No adb, device access, bind, service call, Binder replay, transaction construction, or mutation was used. Next safe step: preserve exact-build per-package manifests and static caller code, then join `uses-permission` → signing digest → explicit grant → bind edge. Do not invoke the service or infer caller identity from UID/priv-app/platform grants.

## Evidence ledger

The complete row-level ledger, including SHA-256, path, line, class, classification, and next safe step, is [the companion CSV](luna_worker_phase6tw_h2_owner_grant_20260810.csv). It contains 16 data rows: owner record, manifest declaration, H2 package record, 10 explicit-grant candidates, service reference, bounded policy result, and bounded client scan.
