#!/bin/bash

cd /home/leaks/leaks-minimal/boot

# 1. Cek apakah /bin/sh ada
zcat initrd.img-5.18.19 | cpio -t | grep -E '^bin/sh$|^bin/bash$'

# 2. Cek symlink sh
zcat initrd.img-5.18.19 | cpio -t | grep -E 'sh$'

# 3. Cek lokasi ld-linux (harus bisa diakses)
zcat initrd.img-5.18.19 | cpio -t | grep ld-linux

# 4. Lihat struktur direktori penting
zcat initrd.img-5.18.19 | cpio -t | grep -E '^bin/|^lib|^usr/lib' | head -25
