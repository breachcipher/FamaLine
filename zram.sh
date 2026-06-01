cat > /etc/init.d/zram << 'EOF'
#!/bin/sh
# Begin /etc/init.d/zram
# Provides: zram
# Required-Start: $local_fs
# Required-Stop: $local_fs
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Description: Setup ZRAM swap

. /lib/lsb/init-functions

# Set ZRAM ke 4 GB (4 * 1024 * 1024 = 4194304 KB)
ZRAM_KB=4194304
ZRAM_DEV="/dev/zram0"

case "$1" in
    start)
        log_info_msg "Setting up ZRAM swap (4GB)..."

        # Load modul
        modprobe zram num_devices=1

        # Tunggu device siap
        sleep 1

        # Set kompressor
        echo zstd > /sys/block/zram0/comp_algorithm 2>/dev/null ||

        # Set ukuran 4GB
        echo "${ZRAM_KB}K" > /sys/block/zram0/disksize

        # Buat dan aktifkan swap
        mkswap "$ZRAM_DEV" > /dev/null
        swapon "$ZRAM_DEV" -p 100

        log_success_msg
        ;;

    stop)
        log_info_msg "Stopping ZRAM swap..."

        if grep -q "$ZRAM_DEV" /proc/swaps; then
            swapoff "$ZRAM_DEV"
        fi

        # Reset device
        echo 1 > /sys/block/zram0/reset 2>/dev/null

        # Unload modul
        modprobe -r zram

        log_success_msg
        ;;

    status)
        echo "=== ZRAM Status ==="
        if [ -b "$ZRAM_DEV" ]; then
            echo "Device   : $ZRAM_DEV aktif"
            echo "Algorithm: $(cat /sys/block/zram0/comp_algorithm)"
            echo "Size     : $(cat /sys/block/zram0/disksize) bytes"
            grep "$ZRAM_DEV" /proc/swaps || echo "Swap     : tidak aktif"
        else
            echo "ZRAM tidak aktif"
        fi
        ;;

    restart)
        $0 stop
        sleep 1
        $0 start
        ;;

    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac

exit 0
# End /etc/init.d/zram
EOF

chmod 754 /etc/init.d/zram
