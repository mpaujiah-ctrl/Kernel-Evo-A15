#!/usr/bin/env python3
"""Suntik 5 hook manual KernelSU-Next ke kernel source."""
import sys

def patch_file(path, anchor, insert_before=None, insert_after=None, marker="CONFIG_KSU"):
    with open(path, "r") as f:
        content = f.read()

    if marker in content and "ksu_handle" in content:
        print(f"[SKIP] {path} sudah dipatch sebelumnya")
        return True

    if anchor not in content:
        print(f"[GAGAL] Anchor tidak ditemukan di {path}:")
        print(f"        {anchor!r}")
        return False

    if insert_before:
        content = content.replace(anchor, insert_before + anchor, 1)
    if insert_after:
        content = content.replace(anchor, anchor + insert_after, 1)

    with open(path, "w") as f:
        f.write(content)
    print(f"[OK] {path} berhasil dipatch")
    return True


results = []

# 1. kernel/reboot.c
results.append(patch_file(
    "kernel/reboot.c",
    anchor="SYSCALL_DEFINE4(reboot, int, magic1, int, magic2, unsigned int, cmd,",
    insert_before=(
        "#ifdef CONFIG_KSU\n"
        "extern int ksu_handle_sys_reboot(int magic1, int magic2, unsigned int cmd, void __user **arg);\n"
        "#endif\n\n"
    ),
))
results.append(patch_file(
    "kernel/reboot.c",
    anchor="\tint ret = 0;\n",
    insert_after=(
        "\n#ifdef CONFIG_KSU\n"
        "\tksu_handle_sys_reboot(magic1, magic2, cmd, &arg);\n"
        "#endif\n"
    ),
))

# 2. fs/exec.c
results.append(patch_file(
    "fs/exec.c",
    anchor="int do_execve(struct filename *filename,",
    insert_before=(
        "#ifdef CONFIG_KSU\n"
        "extern int ksu_handle_execveat(int *fd, struct filename **filename_ptr,\n"
        "\t\t\t\tvoid *argv, void *envp, int *flags);\n"
        "#endif\n\n"
    ),
))
results.append(patch_file(
    "fs/exec.c",
    anchor="\tstruct user_arg_ptr envp = { .ptr.native = __envp };\n\treturn do_execveat_common(AT_FDCWD, filename, argv, envp, 0);",
    insert_before=(
        "\tstruct user_arg_ptr envp = { .ptr.native = __envp };\n"
        "#ifdef CONFIG_KSU\n"
        "\tksu_handle_execveat((int *)AT_FDCWD, &filename, &argv, &envp, 0);\n"
        "#endif\n"
    ),
))

# 3. fs/open.c
results.append(patch_file(
    "fs/open.c",
    anchor="SYSCALL_DEFINE3(faccessat, int, dfd, const char __user *, filename, int, mode)",
    insert_before=(
        "#ifdef CONFIG_KSU\n"
        "extern int ksu_handle_faccessat(int *dfd, const char __user **filename_user,\n"
        "\t\t\t\tint *mode, int *flags);\n"
        "#endif\n"
    ),
))
results.append(patch_file(
    "fs/open.c",
    anchor="\tunsigned int lookup_flags = LOOKUP_FOLLOW;\n\n\tif (mode & ~S_IRWXO)",
    insert_before=(
        "\tunsigned int lookup_flags = LOOKUP_FOLLOW;\n\n"
        "#ifdef CONFIG_KSU\n"
        "\tksu_handle_faccessat(&dfd, &filename, &mode, NULL);\n"
        "#endif\n"
    ),
))

# 4. fs/read_write.c
results.append(patch_file(
    "fs/read_write.c",
    anchor="SYSCALL_DEFINE3(read, unsigned int, fd, char __user *, buf, size_t, count)",
    insert_before=(
        "#ifdef CONFIG_KSU\n"
        "extern bool ksu_vfs_read_hook __read_mostly;\n"
        "extern int ksu_handle_sys_read(unsigned int fd,\n"
        "\t\t\t\tchar __user **buf_ptr, size_t *count_ptr);\n"
        "#endif\n\n"
    ),
))
results.append(patch_file(
    "fs/read_write.c",
    anchor="\tssize_t ret = -EBADF;\n",
    insert_after=(
        "\n#ifdef CONFIG_KSU\n"
        "\tif (unlikely(ksu_vfs_read_hook))\n"
        "\t\tksu_handle_sys_read(fd, &buf, &count);\n"
        "#endif\n"
    ),
))

# 5. fs/stat.c
results.append(patch_file(
    "fs/stat.c",
    anchor="#if !defined(__ARCH_WANT_STAT64) || defined(__ARCH_WANT_SYS_NEWFSTATAT)",
    insert_before=(
        "#ifdef CONFIG_KSU\n"
        "extern int ksu_handle_stat(int *dfd, const char __user **filename_user,\n"
        "\t\t\t\tint *flags);\n"
        "#endif\n\n"
    ),
))
results.append(patch_file(
    "fs/stat.c",
    anchor="\tstruct kstat stat;\n\tint error;\n",
    insert_after=(
        "\n#ifdef CONFIG_KSU\n"
        "\tksu_handle_stat(&dfd, &filename, &flag);\n"
        "#endif\n"
    ),
))

print("\n=== RINGKASAN ===")
gagal = results.count(False)
print(f"Berhasil: {results.count(True)}/{len(results)}, Gagal: {gagal}")
if gagal > 0:
    sys.exit(1)
