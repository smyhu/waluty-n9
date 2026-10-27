#!/bin/sh
# Builds dist/waluty_<version>_armel.deb from this tree (on any Linux with dpkg-deb).
# native/waluty-fetch-armel is prebuilt for the N9 (see native/README.md).
set -e
cd "$(dirname "$0")"
VERSION=$(sed -n 's/^Version: //p' packaging/DEBIAN/control)
P=$(mktemp -d)
chmod 755 $P
mkdir -p $P/DEBIAN $P/opt/waluty $P/etc/init/apps $P/usr/share/applications \
         $P/usr/share/icons/hicolor/80x80/apps $P/usr/share/doc/waluty
cp packaging/DEBIAN/* $P/DEBIAN/
cp src/*.py $P/opt/waluty/
cp -r src/qml $P/opt/waluty/
cp native/waluty-fetch-armel $P/opt/waluty/waluty-fetch
cp packaging/init/waluty-tlo.conf $P/etc/init/apps/
cp packaging/waluty.desktop $P/usr/share/applications/
cp packaging/waluty80.png $P/usr/share/icons/hicolor/80x80/apps/
cp packaging/copyright packaging/LICENSE-flag-icons $P/usr/share/doc/waluty/
chmod 755 $P/DEBIAN/postinst $P/DEBIAN/prerm $P/opt/waluty/main.py $P/opt/waluty/tlo.py \
          $P/opt/waluty/fetch.py $P/opt/waluty/waluty-fetch
chmod 644 $P/opt/waluty/common.py
(cd $P && find opt usr etc -type f -exec md5sum {} + > DEBIAN/md5sums)
mkdir -p dist
dpkg-deb -Zgzip --root-owner-group -b $P dist/waluty_${VERSION}_armel.deb
rm -rf $P
