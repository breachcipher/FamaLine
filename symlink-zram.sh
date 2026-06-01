# Start di runlevel 2,3,4,5 — urutan awal (S02)
ln -sf /etc/init.d/zram /etc/rc2.d/S02zram
ln -sf /etc/init.d/zram /etc/rc3.d/S02zram
ln -sf /etc/init.d/zram /etc/rc4.d/S02zram
ln -sf /etc/init.d/zram /etc/rc5.d/S02zram

# Stop di runlevel 0,1,6 — urutan akhir (K98)
ln -sf /etc/init.d/zram /etc/rc0.d/K98zram
ln -sf /etc/init.d/zram /etc/rc1.d/K98zram
ln -sf /etc/init.d/zram /etc/rc6.d/K98zram
