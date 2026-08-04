# PS7331 futex entry audit

- Source reachability: **SYSCALL_TO_PI_REQUEUE_PROXY_PATH_PRESENT**
- Direct credential gate in scoped functions: **not_observed_in_scoped_functions**
- Userspace policy status: **UNRESOLVED_FROM_KERNEL_SOURCE_ONLY**
- Runtime exploitability proven: **False**
- Root/privilege gain proven: **False**

Absence of a direct capability check in these files does not bypass Android SELinux, seccomp, process domains, or other runtime policy.
