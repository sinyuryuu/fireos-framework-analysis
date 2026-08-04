#!/bin/sh
# Host-only extraction of selected ext4 policy/config directories.
# Uses debugfs read-only commands only; never mounts or writes an image/device.

set -eu

system_image=''
vendor_image=''
output_dir=''
debugfs_bin=''
dry_run=0

usage() {
    cat <<'EOF'
Usage: extract_phase6c_image_policy_readonly.sh \
  --system-image FILE --vendor-image FILE --output DIR [--debugfs FILE] [--dry-run]

The extractor reads only these directories with debugfs rdump:
  system: /init, /system/etc/seccomp_policy, init, selinux, sysconfig, permissions, bpf
  vendor: /etc/seccomp_policy, init, selinux, permissions

It does not mount images, run extracted binaries, contact ADB, or modify an
input image.  The output directory must not already exist.
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --system-image) system_image=$2; shift 2 ;;
        --vendor-image) vendor_image=$2; shift 2 ;;
        --output) output_dir=$2; shift 2 ;;
        --debugfs) debugfs_bin=$2; shift 2 ;;
        --dry-run) dry_run=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
    esac
done

if [ -z "$system_image" ] || [ -z "$vendor_image" ] || [ -z "$output_dir" ]; then
    usage >&2
    exit 2
fi

if [ -z "$debugfs_bin" ]; then
    if command -v debugfs >/dev/null 2>&1; then
        debugfs_bin=$(command -v debugfs)
    elif [ -x /opt/homebrew/opt/e2fsprogs/sbin/debugfs ]; then
        debugfs_bin=/opt/homebrew/opt/e2fsprogs/sbin/debugfs
    else
        echo "debugfs not found; supply --debugfs FILE" >&2
        exit 2
    fi
fi

if [ "$dry_run" -eq 1 ]; then
    printf '%s\n' '{' \
        '  "dry_run": true,' \
        '  "device_contacted": false,' \
        '  "image_mounted": false,' \
        '  "image_written": false,' \
        '  "elf_executed": false,' \
        '  "system_image": "'"$system_image"'",' \
        '  "vendor_image": "'"$vendor_image"'",' \
        '  "debugfs": "'"$debugfs_bin"'",' \
        '  "output": "'"$output_dir"'"' \
        '}'
    exit 0
fi

for input_image in "$system_image" "$vendor_image"; do
    if [ ! -f "$input_image" ]; then
        echo "missing image: $input_image" >&2
        exit 2
    fi
done
if [ ! -x "$debugfs_bin" ]; then
    echo "debugfs is not executable: $debugfs_bin" >&2
    exit 2
fi
if [ -e "$output_dir" ]; then
    echo "refusing to overwrite existing output: $output_dir" >&2
    exit 2
fi

mkdir -p "$output_dir/logs" "$output_dir/system/etc" "$output_dir/vendor/etc"

{
    printf '%s\n' "extractor=extract_phase6c_image_policy_readonly.sh"
    printf '%s\n' "debugfs=$debugfs_bin"
    printf '%s\n' "system_image=$system_image"
    printf '%s\n' "vendor_image=$vendor_image"
    printf '%s\n' "image_mounted=false"
    printf '%s\n' "image_written=false"
    printf '%s\n' "device_contacted=false"
} > "$output_dir/metadata.txt"

file "$system_image" "$vendor_image" > "$output_dir/image-file.txt" 2>&1 || true
shasum -a 256 "$system_image" "$vendor_image" > "$output_dir/image-sha256sums.txt"
"$debugfs_bin" -R stats "$system_image" > "$output_dir/system-debugfs-stats.txt" 2>&1 || true
"$debugfs_bin" -R stats "$vendor_image" > "$output_dir/vendor-debugfs-stats.txt" 2>&1 || true

run_rdump() {
    image_path=$1
    source_dir=$2
    destination_parent=$3
    log_name=$4
    mkdir -p "$destination_parent"
    printf '%s\n' "\"$debugfs_bin\" -R \"rdump $source_dir $destination_parent\" \"$image_path\"" >> "$output_dir/commands.txt"
    set +e
    "$debugfs_bin" -R "rdump $source_dir $destination_parent" "$image_path" \
        > "$output_dir/logs/$log_name.stdout.txt" \
        2> "$output_dir/logs/$log_name.stderr.txt"
    command_status=$?
    set -e
    printf '%s\n' "$command_status" > "$output_dir/logs/$log_name.exit_code.txt"
    # Homebrew debugfs may report chown failures while still extracting bytes
    # as the unprivileged host user.  The manifest below is authoritative for
    # which files were actually recovered.
}

run_rdump "$system_image" /system/etc/seccomp_policy "$output_dir/system/etc" system-seccomp-policy
run_rdump "$system_image" /system/etc/init "$output_dir/system/etc" system-init
run_rdump "$system_image" /system/etc/selinux "$output_dir/system/etc" system-selinux
run_rdump "$system_image" /system/etc/sysconfig "$output_dir/system/etc" system-sysconfig
run_rdump "$system_image" /system/etc/permissions "$output_dir/system/etc" system-permissions
run_rdump "$system_image" /system/etc/bpf "$output_dir/system/etc" system-bpf
run_rdump "$vendor_image" /etc/seccomp_policy "$output_dir/vendor/etc" vendor-seccomp-policy
run_rdump "$vendor_image" /etc/init "$output_dir/vendor/etc" vendor-init
run_rdump "$vendor_image" /etc/selinux "$output_dir/vendor/etc" vendor-selinux
run_rdump "$vendor_image" /etc/permissions "$output_dir/vendor/etc" vendor-permissions

run_dump() {
    image_path=$1
    source_file=$2
    destination_file=$3
    log_name=$4
    mkdir -p "$(dirname "$destination_file")"
    printf '%s\n' "\"$debugfs_bin\" -R \"dump $source_file $destination_file\" \"$image_path\"" >> "$output_dir/commands.txt"
    set +e
    "$debugfs_bin" -R "dump $source_file $destination_file" "$image_path" \
        > "$output_dir/logs/$log_name.stdout.txt" \
        2> "$output_dir/logs/$log_name.stderr.txt"
    command_status=$?
    set -e
    printf '%s\n' "$command_status" > "$output_dir/logs/$log_name.exit_code.txt"
}

run_dump "$system_image" /init.zygote32.rc "$output_dir/root/init.zygote32.rc" root-init-zygote32
run_dump "$system_image" /init.zygote64_32.rc "$output_dir/root/init.zygote64_32.rc" root-init-zygote64-32
run_dump "$system_image" /init "$output_dir/root/init" root-init-binary
run_dump "$system_image" /init.environ.rc "$output_dir/root/init.environ.rc" root-init-environ
run_dump "$system_image" /init.rc "$output_dir/root/init.rc" root-init
run_dump "$system_image" /default.prop "$output_dir/root/default.prop" root-default-prop
run_dump "$system_image" /system/build.prop "$output_dir/system/build.prop" system-build-prop
run_dump "$system_image" /system/etc/ld.config.28.txt "$output_dir/system/etc/ld.config.28.txt" system-ld-config
run_dump "$system_image" /system/bin/app_process64 "$output_dir/system/bin/app_process64" system-app-process64
run_dump "$system_image" /system/bin/linker64 "$output_dir/system/bin/linker64" system-linker64
run_dump "$system_image" /system/lib64/libc.so "$output_dir/system/lib64/libc.so" system-libc
run_dump "$system_image" /system/lib64/libandroid_runtime.so "$output_dir/system/lib64/libandroid_runtime.so" system-libandroid-runtime
run_dump "$system_image" /system/lib64/libart.so "$output_dir/system/lib64/libart.so" system-libart

find "$output_dir" -type f -print | sort | while IFS= read -r recovered_file; do
    case "$recovered_file" in
        "$output_dir/logs"/*|"$output_dir/commands.txt"|"$output_dir/metadata.txt"|"$output_dir/image-file.txt"|"$output_dir/image-sha256sums.txt"|"$output_dir/system-debugfs-stats.txt"|"$output_dir/vendor-debugfs-stats.txt"|"$output_dir/extracted-file-manifest.tsv") continue ;;
    esac
    size=$(stat -f '%z' "$recovered_file")
    digest=$(shasum -a 256 "$recovered_file" | awk '{print $1}')
    printf '%s\t%s\t%s\n' "${recovered_file#"$output_dir"/}" "$size" "$digest"
done > "$output_dir/extracted-file-manifest.tsv"

printf '%s\n' "device_contacted=false" "image_mounted=false" "image_written=false" \
    "elf_executed=false" "futex_triggered=false" "kernel_memory_accessed=false" \
    "payload_or_address_generated=false" > "$output_dir/safety.txt"
shasum -a 256 \
    "$output_dir/metadata.txt" "$output_dir/image-file.txt" \
    "$output_dir/image-sha256sums.txt" "$output_dir/extracted-file-manifest.tsv" \
    "$output_dir/safety.txt" > "$output_dir/output-sha256sums.txt"

recovered_count=$(wc -l < "$output_dir/extracted-file-manifest.tsv" | tr -d ' ')
printf '%s\n' "output=$output_dir" "recovered_files=$recovered_count" \
    "image_mounted=false" "image_written=false" "device_contacted=false"
