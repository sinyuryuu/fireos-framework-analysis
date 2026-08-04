/*
 * Phase 6A benign PI-futex reachability smoke test.
 *
 * It performs exactly one uncontended FUTEX_LOCK_PI_PRIVATE followed by one
 * FUTEX_UNLOCK_PI_PRIVATE on a zero-initialized private word, then exits.
 * It does not use requeue-PI operations, create a race, access kernel memory,
 * change credentials, or attempt exploitation.
 *
 * This file is intentionally freestanding so it can be built without an NDK
 * sysroot.  It is for an AArch64 Android/Linux target only.
 */

typedef unsigned long ulong;
typedef unsigned int u32;

enum {
  NR_EXIT = 93,
  NR_FUTEX = 98,
  FUTEX_LOCK_PI_PRIVATE = 6 | 128,
  FUTEX_UNLOCK_PI_PRIVATE = 7 | 128,
};

static volatile u32 futex_word;

static long syscall6(long number, long a0, long a1, long a2, long a3,
                     long a4, long a5) {
  register long x0 asm("x0") = a0;
  register long x1 asm("x1") = a1;
  register long x2 asm("x2") = a2;
  register long x3 asm("x3") = a3;
  register long x4 asm("x4") = a4;
  register long x5 asm("x5") = a5;
  register long x8 asm("x8") = number;
  asm volatile("svc #0"
               : "+r"(x0)
               : "r"(x1), "r"(x2), "r"(x3), "r"(x4), "r"(x5), "r"(x8)
               : "memory");
  return x0;
}

__attribute__((noreturn)) void _start(void) {
  long lock_result =
      syscall6(NR_FUTEX, (long)&futex_word, FUTEX_LOCK_PI_PRIVATE, 0, 0, 0, 0);
  long exit_code = 0;

  if (lock_result != 0) {
    exit_code = 11;
  } else {
    long unlock_result = syscall6(NR_FUTEX, (long)&futex_word,
                                  FUTEX_UNLOCK_PI_PRIVATE, 0, 0, 0, 0);
    if (unlock_result != 0) {
      exit_code = 12;
    }
  }

  syscall6(NR_EXIT, exit_code, 0, 0, 0, 0, 0);
  for (;;) {
  }
}
