#!/usr/bin/env python3
"""
Fix duplicate 'event' declaration di kernel/trace/trace_event_perf.c
Dipakai di GitHub Actions workflow build kernel (Evo cepheus KSUN).
"""

import sys

TARGET_FILE = "kernel/trace/trace_event_perf.c"

old = "\tstruct perf_event *event;\n" \
      "\tstruct ftrace_entry *entry;\n" \
      "\tstruct perf_event *event;\n" \
      "\tstruct hlist_head head;"

new = "\tstruct perf_event *event;\n" \
      "\tstruct ftrace_entry *entry;\n" \
      "\tstruct hlist_head head;"

def main():
    try:
        with open(TARGET_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: {TARGET_FILE} tidak ditemukan. Jalankan script ini dari root folder 'kernel'.")
        sys.exit(1)

    if old not in content:
        print("WARNING: pattern 'old' tidak ditemukan di file. "
              "Mungkin sudah pernah di-patch, atau formatnya beda. Tidak ada perubahan dilakukan.")
        sys.exit(0)

    content = content.replace(old, new, 1)

    with open(TARGET_FILE, "w") as f:
        f.write(content)

    print(f"OK: duplicate 'event' declaration berhasil di-fix di {TARGET_FILE}")

if __name__ == "__main__":
    main()
