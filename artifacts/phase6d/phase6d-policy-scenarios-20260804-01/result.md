# PS7331 `/init` policy-loader scenario classification

Host-only evidence join. The binary was not executed and no boot/property,
SELinux policy, partition, kernel-memory, or privilege operation was attempted.

## Conservative classification

- **S1 userspace-controlled selector — 待驗證 / Hypothesis.** No evidence
  currently connects a shell/untrusted-writable setting to the rootable branch.
- **S2 boot/cmdline selector — 高可信推論 / Strong evidence.** The image has
  an `androidboot.selinux`/`permissive` parser candidate and separate standard
  and rootable path-builder call sites; the exact selector remains unresolved.
- **S3 AVB/signature/fuse binding — 待驗證 / Hypothesis.** AVB and crypto
  markers are present, but no current CFG edge proves they guard the rootable
  path or read an eFuse.
- **S4 dead code — string-only residue is 已排除; runtime reachability is
  待驗證.** ADRP/ADD references and a common-helper call make a pure strings-only
  explanation insufficient.

## Safety boundary

Boot-property injection, alternate-policy selection, verification bypass,
remount, bootloader/fastboot, image writes, kernel races, panic tests and
root payloads remain rejected.
