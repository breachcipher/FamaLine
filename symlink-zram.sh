# Alternatif jika mengikuti struktur murni LFS/BLFS:
ln -sf /etc/rc.d/init.d/zram /etc/rc.d/rc2.d/S02zram
ln -sf /etc/rc.d/init.d/zram /etc/rc.d/rc3.d/S02zram
ln -sf /etc/rc.d/init.d/zram /etc/rc.d/rc4.d/S02zram
ln -sf /etc/rc.d/init.d/zram /etc/rc.d/rc5.d/S02zram

ln -sf /etc/rc.d/init.d/zram /etc/rc.d/rc0.d/K98zram
ln -sf /etc/rc.d/init.d/zram /etc/rc.d/rc1.d/K98zram
ln -sf /etc/rc.d/init.d/zram /etc/rc.d/rc6.d/K98zram
