Phase 5D public LK-route review

Scope: host-side static review plus a bounded, read-only attempt to read the
installed PS7330 LK block through the Android shell. No root exploit, BROM
probe, DA upload, fastboot unlock, certificate submission, seccfg change,
partition write, erase, remount, or reboot was executed in this review.

Device context:
  serial=G001LT0511550CFT
  model=KFTRWI
  product=trona
  soc=MT8183
  build=Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
  current state=normal ADB device, verified boot green, flash.locked=1,
                SELinux Enforcing

The complete PS7331 OTA LK and preloader are adjacent-version artifacts. They
are not treated as PS7330 inputs and were not copied to the device.

Reviewed public source snapshots:
  lkpatcher  68034be95401da72ab17251e57d224c0a942d8ad
  pwnage24mtk 14df908af0ef6d748888b8f07cdccf9341eb16fb
  fenrir 39688713455ea81667003c240dd53ce7310681b8

The Amazon-specific unlock strings in the PS7331 LK show a real signed or
certificate-controlled bootloader surface (`amzn_verify_unlock`, temporary
unlock helpers, `flash:tucert`, and `getvar:unlock_status`). They do not expose
an unlock credential. The source and image comparison therefore identifies a
new research lead, not an executable unlock method.
