# Phase 6SJ–SM control surfaces (plain text)

```text
6SJ exact permission XML
  -> signature|privileged declaration [CONFIRMED]
  -> holder/grant/production caller [UNKNOWN]
  -> AmazonApplicationFlags metadata writer [CONFIRMED]
  -> HOME/PMS/component-state edge [BOUNDED NOT FOUND]

6SK Java OTA verifier/install
  -> RecoverySystem / UpdateSystem [CONFIRMED]
  -> updater/partition-write capability [OBSERVED-CAPABILITY]
  -> shell/ordinary-app caller [NOT ESTABLISHED]

6SL source/config/policy
  -> shipped node
  -> exact native open/ioctl/proc caller [UNKNOWN for all 7]
  -> sensitive effect [NOT ESTABLISHED]

6SM existing tests
  -> canonical / duplicate / changed premise / rejected
  -> no repeated private Binder, driver, OTA, recovery or Fire Launcher mutation

All lines
  -> bounded conclusion: no new ordinary-app/shell -> trusted identity -> sensitive sink
```
