#!/usr/bin/env python3
"""
Fix: tambahkan flag -@ (overlay support) khusus untuk target .dtbo
di scripts/Makefile.lib, supaya dtc bisa resolve reference macam &tlmm
yang dipakai file-file overlay (cepheus-pinctrl.dtsi, dll).

Tanpa fix ini, dtc gagal parse overlay dengan error:
  "syntax error" / "Unable to parse input tree"
karena label seperti &tlmm dianggap tidak terdefinisi.
"""

import sys

TARGET_FILE = "scripts/Makefile.lib"

old_snippet = "$(DTC_INCLUDE)) $(DTC_FLAGS) \\"
new_snippet = "$(DTC_INCLUDE)) $(DTC_FLAGS) $(if $(filter %.dtbo,$@),-@) \\"

def main():
    try:
        with open(TARGET_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: {TARGET_FILE} tidak ditemukan. Jalankan dari root folder 'kernel'.")
        sys.exit(1)

    count = content.count(old_snippet)

    if count == 0:
        print("WARNING: pattern tidak ditemukan. Mungkin sudah dipatch, atau formatnya beda.")
        sys.exit(0)

    if count > 1:
        print(f"WARNING: pattern ditemukan {count}x (harusnya 1x). "
              "Tetap lanjut replace yang pertama, tapi periksa manual kalau hasil masih error.")

    content = content.replace(old_snippet, new_snippet, 1)

    with open(TARGET_FILE, "w") as f:
        f.write(content)

    print(f"OK: flag -@ untuk target .dtbo berhasil ditambahkan di {TARGET_FILE}")

if __name__ == "__main__":
    main()
