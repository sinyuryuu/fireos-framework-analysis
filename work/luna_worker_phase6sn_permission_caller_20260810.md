# Phase 6SN — permission-holder / caller closure

Date: 2026-08-10. Host-only static review. No adb, Binder/service call,
package mutation, settings mutation, or exploit analysis was performed.

## Bottom line

`amazon.permission.ADD_RM_PKG_METADATA` is **Confirmed** as an exact-build declaration with raw protection `0x80000002` (`signature|privileged`) and as a method-local gate on all four Amazon Package Manager metadata/flags mutators. The mutators persist through `AmazonApplicationFlags.writeToFile` to `/data/system/amazon_package_flags.xml`; this is not a preferred-HOME or component/application-enabled-state writer.

The exact permission's holder, runtime grant, and production caller/UID/signing identity remain **Unknown**. The holder census joins ordinary framework permissions only; its lack of an exact custom-permission row is not proof of absence. The private service publication and framework facade prove an API surface, not a production caller.

`com.amazon.device.permission.PROFILE_INTERACTION` is **Confirmed** as a signature|privileged declaration and as a `Context.checkPermission` gate using service process/user IDs. Its holder and production caller remain **Unknown**. The DCPMS service manifest requests it, but that is a declaration of use, not proof of grant or the caller of `AmazonProfileService`.

HOME and package-state evidence stays separate. The bounded HOME sinks are PMS `setHomeActivity` / preferred-activity methods with their own user and permission checks. The exact KFT path is **Confirmed** child/profile-scoped: `IAmazonUserManager.enableKftLauncher(UserInfo)` uses transaction **3**; the service implementation calls `enableKftLauncherComponent(UserInfo)`, which sets Tahoe component state and Fire/Launcher3 application state for the supplied user. A production lifecycle caller is present for child users, but the external Binder caller/UID is not closed. No static edge joins this KFT path to `ADD_RM_PKG_METADATA`.

## Remaining unknowns

1. Which package/UID, if any, holds and is granted `amazon.permission.ADD_RM_PKG_METADATA`, including signing/privapp provenance.
2. The production caller chain into the four Amazon PM mutators, including runtime caller UID and whether any caller is outside system-server or the framework facade.
3. The holder/grant and production caller for `PROFILE_INTERACTION`.
4. The external caller and authorization gate for KFT transaction 3; static evidence establishes only the proxy transaction and internal child-user lifecycle call.
5. Whether omitted/generated/native code consumes Amazon metadata to affect HOME or package state; the bounded corpus found no such edge.

