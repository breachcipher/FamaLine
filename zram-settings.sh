#!/bin/bash

cat >> /etc/sysctl.conf << 'EOF'

# ZRAM
vm.swappiness = 180
vm.watermark_boost_factor = 0
vm.watermark_scale_factor = 125
vm.vfs_cache_pressure = 50
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5
EOF

# Apply sekarang
sysctl -p
